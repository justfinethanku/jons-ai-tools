# Desktop Icon Setup

This document explains how to create a desktop icon for the AI Tools application.

## Quick Setup

Run the included script to automatically create a macOS app bundle:

```bash
python3 create_desktop_icon.py
```

This creates `AI Tools.app` which you can:
- Drag to your Desktop or Applications folder
- Double-click to launch the application
- The browser will automatically open to http://localhost:8501

## What the Script Does

The `create_desktop_icon.py` script creates a proper macOS `.app` bundle with:

1. **App Bundle Structure**: Creates the standard macOS app directory structure
2. **Info.plist**: Contains app metadata and configuration
3. **Launch Script**: Bash script that:
   - Activates the Python virtual environment
   - Starts the Streamlit server
   - Opens the browser automatically
   - Keeps the app running

## Manual Setup (Alternative)

If you prefer manual setup, you can create an Automator application:

1. Open Automator
2. Create new "Application"
3. Add "Run Shell Script" action
4. Set shell to `/bin/bash`
5. Add this script:

```bash
cd "/Users/jonathanedwards/jons-ai-tools"
source venv/bin/activate
streamlit run app.py --server.headless true --server.port 8501 &
sleep 3
open http://localhost:8501
wait
```

6. Save as "AI Tools" to Desktop

## Features

- **One-click launch**: Double-click to start the entire application
- **Auto-browser**: Browser opens automatically to the correct URL
- **Virtual environment**: Automatically activates the Python environment
- **Clean shutdown**: Closing the app properly stops the server

## Troubleshooting

- **Permission denied**: Run `chmod +x "AI Tools.app/Contents/MacOS/launch_ai_tools"`
- **Port in use**: The script uses port 8501 - ensure it's available
- **Virtual environment**: Ensure `venv` exists and contains the required packages