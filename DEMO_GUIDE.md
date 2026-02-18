# VisionClaw Demo Guide (Sales Team)

**Goal:** Provide a seamless, "Grandma-proof" demo experience for the VisionClaw launch.

## 1. Preparation

Before the demo starts, ensure the following:
1.  **iPhone is connected to the Demo WiFi network.**
2.  **The "Claw" (Network Camera) is powered on and connected to the same WiFi.**
3.  **Get the IP Address of the "Claw".**
    *   The engineering team will provide this. It looks like `192.168.1.X` (e.g., `192.168.1.5`).
    *   Write it down on a sticky note if needed!

## 2. Running the Demo

### Option A: The "Claw" (Network Camera Demo) - **Recommended for Stage**
This mode uses the stationary "Claw" camera to show the product capabilities without wearing glasses.

1.  **Open the VisionClaw App** on the iPhone.
2.  **Find the "Server IP" field** on the main screen.
3.  **Type in the IP Address** of the Claw (e.g., `192.168.1.5`).
4.  **Tap "Start Network Camera"**.
5.  **Voice Demo**: Speak clearly to the microphone. The audio is piped to the PC running the Claw for the leadership demo.
    *   *Say:* "What am I looking at?" (Gemini describes the scene)
    *   *Say:* "Add milk to my shopping list" (Uses OpenClaw Agent skills)
    *   *Say:* "Search for coffee shops nearby"
6.  **Success!** You should see the live video feed from the Claw on the iPhone screen.

### Option B: The Glasses (Wearable Demo) - **For Personal Experience**
This mode lets users wear the glasses and see through them.

1.  **Put on the VisionClaw Glasses.**
2.  **Ensure they are paired** with the iPhone (Bluetooth settings).
3.  **Open the VisionClaw App.**
4.  **Tap "Start Streaming"**.
5.  **Voice Demo**: Same commands as above.
6.  **Success!** The iPhone screen will mirror what you see through the glasses.

## 3. Troubleshooting

*   **"Connection Failed" or Black Screen:**
    *   Check: Is the iPhone on the correct WiFi?
    *   Check: Is the IP Address correct? Retype it carefully.
    *   Check: Is the Claw powered on?

*   **"I can't do that" (Agent Skills Fail):**
    *   This means the **OpenClaw Gateway** is not running on the demo laptop.
    *   Check with engineering if the "Agent" features are enabled for this demo.

*   **"Permission Denied":**
    *   Go to **iPhone Settings -> VisionClaw**.
    *   Turn on **Local Network** and **Camera**.

*   **App Crashes:**
    *   Force close the app (swipe up) and restart it.
