# VisionClaw Mac Client (Project Morph Prototype)

This is a Python-based client that runs directly on your Mac. It replaces the iPhone app for stationary demos.

**Architecture:**
1.  **Audio**: Use the default Mac Microphone & Speaker (e.g., your paired Bluetooth Headset).
2.  **Vision**: Connects to the Network Camera (The Claw) via MJPEG stream.
3.  **Brain**: Connects to Gemini Live API.
4.  **Hands**: Connects to local OpenClaw Gateway for tool execution.

**Prerequisites:**
1.  Python 3.10+
2.  `pip install -r requirements.txt`
3.  Gemini API Key (set in env variable `GEMINI_API_KEY`)
4.  OpenClaw running locally (gateway mode)
5.  Network Camera serving MJPEG stream at `http://<IP>:81/stream`

**How to Run:**
```bash
export GEMINI_API_KEY="your_key_here"
export CAMERA_URL="http://192.168.1.X:81/stream"
python mac_client.py
```
