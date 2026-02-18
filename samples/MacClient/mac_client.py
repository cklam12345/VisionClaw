import asyncio
import websockets
import pyaudio
import cv2
import json
import base64
import os
import requests
import numpy as np
import time
from dotenv import load_dotenv

load_dotenv()

# --- Config ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CAMERA_URL = os.getenv("CAMERA_URL") # e.g. http://192.168.1.5:81/stream
OPENCLAW_HOST = os.getenv("OPENCLAW_HOST", "http://localhost:18789")
OPENCLAW_TOKEN = os.getenv("OPENCLAW_TOKEN", "your-gateway-token")

MODEL = "models/gemini-2.5-flash-native-audio-preview-12-2025"
WS_URL = f"wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent?key={GEMINI_API_KEY}"

# Audio Config
SAMPLE_RATE_IN = 16000
SAMPLE_RATE_OUT = 24000
CHUNK_SIZE = 1024

# Video Config (Throttle)
FPS_TARGET = 1.0 

# --- Global State ---
video_loop_running = False
frame_queue = asyncio.Queue()

# --- OpenClaw Execution ---
async def execute_tool(task):
    if not OPENCLAW_HOST:
        print("[Client] OpenClaw host not configured.")
        return "Error: OpenClaw not configured."
    
    url = f"{OPENCLAW_HOST}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENCLAW_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Simple one-shot prompt
    payload = {
        "model": "openclaw",
        "messages": [{"role": "user", "content": task}],
        "stream": False
    }

    print(f"[OpenClaw] Executing: {task}")
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: requests.post(url, json=payload, headers=headers, timeout=10))
        
        if response.status_code == 200:
            data = response.json()
            # Extract content from OpenAI-compatible format
            result = data['choices'][0]['message']['content']
            print(f"[OpenClaw] Result: {result[:100]}...")
            return result
        else:
            print(f"[OpenClaw] Error {response.status_code}: {response.text}")
            return f"Error executing task: {response.text}"
    except Exception as e:
        print(f"[OpenClaw] Exception: {e}")
        return f"Error: {str(e)}"

# --- Video Capture ---
async def video_capture_loop():
    global video_loop_running
    video_loop_running = True
    
    if not CAMERA_URL:
        print("[Video] No CAMERA_URL provided. Video disabled.")
        return

    cap = cv2.VideoCapture(CAMERA_URL)
    if not cap.isOpened():
        print(f"[Video] Failed to open stream: {CAMERA_URL}")
        return

    print(f"[Video] Streaming from {CAMERA_URL}")
    
    last_frame_time = 0.0
    while video_loop_running:
        ret, frame = cap.read()
        if not ret:
            print("[Video] Create capture failed, reconnecting...")
            cap.release()
            await asyncio.sleep(2)
            cap = cv2.VideoCapture(CAMERA_URL)
            continue
            
        now = time.time()
        if now - last_frame_time >= (1.0 / FPS_TARGET):
            # Resize/Compress
            # Gemini expects JPEG bytes
            _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
            jpg_bytes = buffer.tobytes()
            
            # Add to queue (drop old if full)
            if frame_queue.full():
                try: frame_queue.get_nowait()
                except: pass
            await frame_queue.put(jpg_bytes)
            
            last_frame_time = now
            
        await asyncio.sleep(0.01) # Yield slightly
        
    cap.release()

# --- Main WebSocket Loop ---
async def gemini_session():
    # Setup PyAudio
    p = pyaudio.PyAudio()
    
    # Input Stream (Mic)
    mic_stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=SAMPLE_RATE_IN,
                        input=True,
                        frames_per_buffer=CHUNK_SIZE)
                        
    # Output Stream (Speaker)
    spk_stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=SAMPLE_RATE_OUT,
                        output=True)

    print(f"[Audio] Input: {SAMPLE_RATE_IN}Hz, Output: {SAMPLE_RATE_OUT}Hz")
    
    async with websockets.connect(WS_URL) as ws:
        print("[Gemini] Connected to WebSocket")
        
        # Initial Setup with Tools
        setup_msg = {
            "setup": {
                "model": MODEL,
                "tools": [{
                    "functionDeclarations": [{
                        "name": "execute",
                        "description": "Execute a task using the user's personal assistant (OpenClaw). Use this for searches, messaging, lists, and controlling devices.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "task": {"type": "STRING", "description": "The detailed task to perform."}
                            },
                            "required": ["task"]
                        }
                    }]
                }]
            }
        }
        await ws.send(json.dumps(setup_msg))
        print("[Gemini] Setup sent")
        
        # Wait for setup_complete (optional but good practice)
        # For simplicity in this script, we just start streaming, but a robust client would wait.
        
        # Task: Send Audio
        async def send_audio():
            while True:
                data = mic_stream.read(CHUNK_SIZE, exception_on_overflow=False)
                # Structure: { "realtime_input": { "media_chunks": [{ "mime_type": "audio/pcm", "data": base64 }] } }
                b64_data = base64.b64encode(data).decode('utf-8')
                msg = {
                    "realtime_input": {
                        "media_chunks": [{
                            "mime_type": "audio/pcm",
                            "data": b64_data
                        }]
                    }
                }
                await ws.send(json.dumps(msg))
                await asyncio.sleep(0.001)

        # Task: Send Video
        async def send_video():
            while True:
                jpg_data = await frame_queue.get()
                b64_data = base64.b64encode(jpg_data).decode('utf-8')
                msg = {
                    "realtime_input": {
                        "media_chunks": [{
                            "mime_type": "image/jpeg",
                            "data": b64_data
                        }]
                    }
                }
                await ws.send(json.dumps(msg))


        # Task: Receive
        async def receive_loop():
            async for message in ws:
                response = json.loads(message)
                
                # Check for Audio response
                if "serverContent" in response:
                    content = response["serverContent"]
                    if "modelTurn" in content:
                        parts = content["modelTurn"]["parts"]
                        for part in parts:
                            if "inlineData" in part: # Audio
                                b64_audio = part["inlineData"]["data"]
                                pcm_data = base64.b64decode(b64_audio)
                                spk_stream.write(pcm_data)
                
                # Check for Tool Calls
                if "toolCall" in response:
                    fc = response["toolCall"]["functionCall"]
                    tool_name = fc["name"]
                    args = fc["args"]
                    
                    if tool_name == "execute": # Assuming standard tool call
                        task_desc = args.get("task", "")
                        print(f"[Gemini] Tool Call: {task_desc}")
                        
                        # Execute
                        result = await execute_tool(task_desc)
                        
                        # Send Response
                        tool_resp = {
                            "toolResponse": {
                                "functionResponses": [{
                                    "name": tool_name,
                                    "response": {"result": result} 
                                }]
                            }
                        }
                        await ws.send(json.dumps(tool_resp))

        # Start Tasks
        try:
            await asyncio.gather(
                send_audio(),
                send_video(),
                receive_loop()
            )
        except Exception as e:
            print(f"[Gemini] Session Error: {e}")
        finally:
            mic_stream.stop_stream()
            mic_stream.close()
            spk_stream.stop_stream()
            spk_stream.close()
            p.terminate()

async def main():
    # Start Video Capture (Background)
    asyncio.create_task(video_capture_loop())
    
    # Start Session
    if not GEMINI_API_KEY:
        print("Please set GEMINI_API_KEY env var.")
        return
        
    await gemini_session()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped.")
