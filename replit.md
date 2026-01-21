# Vibration Controller

## Overview
This is a web-based version of an Android Vibration Controller app. The original project was built with Kivy/Buildozer for Android, but has been adapted to run as a web application in Replit.

The app connects to a remote server (`https://www.crashando.it/vibe/vibra.php`) to:
- Send vibration patterns (A, B, C, D) to all connected devices
- Poll for incoming vibration commands

## Project Structure
```
.
├── web_app.py          # Flask web application (main entry point)
├── main.py             # Original Android Kivy app (for reference/Android build)
├── service.py          # Original Android background service (for reference/Android build)
├── buildozer.spec      # Android build configuration
├── AndroidManifest.xml # Android manifest
└── pyproject.toml      # Python dependencies
```

## Running the App
The web application runs on port 5000 using Flask:
```
python web_app.py
```

## Features
- **Send Vibrations**: Click buttons A, B, C, or D to send vibration patterns
- **Receive Vibrations**: Start polling to listen for incoming vibration commands
- **Browser Vibration**: On supported mobile browsers, will attempt to vibrate the device

## Dependencies
- Flask (web framework)
- Requests (HTTP client)

## Notes
- The original Android app files (main.py, service.py) are kept for reference but require Android SDK/NDK to build
- The web version provides the same server connectivity but browser vibration is limited to supported mobile browsers
