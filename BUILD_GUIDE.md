# VisionClaw Engineering Build Guide

**Goal:** Build and deploy the VisionClaw app and signaling server.

## 1. Prerequisites (macOS)

1.  **Xcode 15+** installed (for iOS development).
2.  **Node.js** (v18+ recommended) installed (for signaling server).
3.  **CocoaPods** (if not installed):
    ```bash
    sudo gem install cocoapods
    ```
4.  **Hardware Requirements**:
    *   **iPhone** (iOS 16+).
    *   **Claw (Network Camera)** or equivalent MJPEG stream source.
5.  **Gemini API Key**: Get one from [Google AI Studio](https://aistudio.google.com/apikey).

## 2. Building the iOS App

The sample app structure is located at `samples/CameraAccess`.

1.  **Navigate to the project directory**:
    ```bash
    cd samples/CameraAccess/CameraAccess.xcodeproj
    ```
    *(Note: You can open `.xcodeproj` directly)*
2.  **Open the project** in Xcode:
    ```bash
    open samples/CameraAccess/CameraAccess.xcodeproj
    ```
3.  **Configure API Key**:
    *   Open `samples/CameraAccess/CameraAccess/Gemini/GeminiConfig.swift`.
    *   Replace `YOUR_GEMINI_API_KEY` with your actual key.
4.  **Check Signing & Capabilities**:
    *   Select the `CameraAccess` target -> **Signing & Capabilities**.
    *   Select your **Team** (personal or company Apple ID).
    *   Ensure **Bundle Identifier** is unique (e.g., `com.yourname.VisionClaw`).
5.  **Build and Run**:
    *   Select your connected device (iPhone).
    *   Set the active scheme to `CameraAccess`.
    *   Click **Run** (Play button) or press `Cmd+R`.

## 3. Setting up OpenClaw (Optional - for Agent Skills)

OpenClaw enables the "Agent" features (e.g., "Add to shopping list", "Send message"). It runs on a Mac on the same network.

1.  **Install OpenClaw**: Follow the instructions at [https://github.com/nichochar/openclaw](https://github.com/nichochar/openclaw).
2.  **Configure Gateway**:
    *   Edit `~/.openclaw/openclaw.json`:
        ```json
        {
          "gateway": {
            "port": 18789,
            "bind": "lan",
            "auth": {
              "mode": "token",
              "token": "your-gateway-token-here"
            },
            "http": {
              "endpoints": {
                "chatCompletions": { "enabled": true }
              }
            }
          }
        }
        ```
    *   `bind: "lan"` allows the iPhone to reach it.
3.  **Start the Gateway**:
    ```bash
    openclaw gateway restart
    ```
4.  **Update iOS App Configuration**:
    *   In `GeminiConfig.swift`, set:
        *   `openClawHost`: Your Mac's Bonjour hostname (e.g., `http://Johns-MacBook-Pro.local`).
        *   `openClawGatewayToken`: The token you set in `openclaw.json`.

## 4. Running the Signaling Server (Optional)

The signaling server handles WebRTC connections for standard streaming (not needed for MJPEG/Network Camera mode).

1.  **Navigate to the server directory**:
    ```bash
    cd samples/CameraAccess/server
    ```
2.  **Install dependencies**:
    ```bash
    npm install
    ```
3.  **Start the server**:
    ```bash
    npm start
    ```
    *   Server runs on port **8080**.

## 5. Setting up the Network Camera (The "Claw")

Ensure you have a device serving an MJPEG stream on port **81**.

*   **Stream URL**: `http://<Device_IP>:81/stream` (MJPEG)
*   **Capture URL**: `http://<Device_IP>/capture` (Still JPEG)

## 6. Android Build (Placeholder)

*   **Status**: Android project **not found in this repository**.
*   **Action**: Create a new Android project or locate the existing one and import MJPEG streaming logic.
