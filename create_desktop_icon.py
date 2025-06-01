#!/usr/bin/env python3

import os
import subprocess
import sys
from pathlib import Path

def create_app_bundle():
    """Create a macOS .app bundle for the AI Tools app"""
    
    # Get the current directory
    app_dir = Path(__file__).parent.absolute()
    
    # App bundle name
    app_name = "AI Tools"
    app_bundle = f"{app_name}.app"
    
    # Create the app bundle structure
    contents_dir = Path(app_bundle) / "Contents"
    macos_dir = contents_dir / "MacOS"
    resources_dir = contents_dir / "Resources"
    
    # Create directories
    for dir_path in [contents_dir, macos_dir, resources_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Create Info.plist
    info_plist = contents_dir / "Info.plist"
    info_plist.write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launch_ai_tools</string>
    <key>CFBundleIdentifier</key>
    <string>com.jonathanedwards.aitools</string>
    <key>CFBundleName</key>
    <string>{app_name}</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.9</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>''')
    
    # Create the launcher script
    launcher_script = macos_dir / "launch_ai_tools"
    launcher_script.write_text(f'''#!/bin/bash

# Change to the app directory
cd "{app_dir}"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Function to cleanup on exit
cleanup() {{
    echo "Stopping AI Tools..."
    # Kill the Streamlit process
    pkill -f "streamlit run app.py"
    exit 0
}}

# Set trap to cleanup when script exits
trap cleanup EXIT SIGTERM SIGINT

# Start the Streamlit app in background
streamlit run app.py --server.headless true --server.port 8501 &
STREAMLIT_PID=$!

# Wait a moment for the server to start
sleep 3

# Open the browser
open http://localhost:8501

# Monitor for browser process
echo "AI Tools is running at http://localhost:8501"
echo "Server will stop automatically when you quit the browser"

# Wait for the browser to close by monitoring the port
while true; do
    # Check if any browser is still connected to our port
    if ! lsof -i :8501 | grep -q ESTABLISHED; then
        # Wait a bit more to avoid false positives
        sleep 10
        if ! lsof -i :8501 | grep -q ESTABLISHED; then
            echo "No active browser connections detected. Stopping server..."
            break
        fi
    fi
    sleep 5
done

# Stop the Streamlit process
kill $STREAMLIT_PID 2>/dev/null
echo "AI Tools stopped."
''')
    
    # Make the launcher script executable
    launcher_script.chmod(0o755)
    
    print(f"✅ Created {app_bundle}")
    print(f"📁 Location: {Path.cwd() / app_bundle}")
    print("\n🚀 To use:")
    print(f"1. Drag {app_bundle} to your Desktop or Applications folder")
    print("2. Double-click to launch AI Tools")
    print("3. Your browser will open automatically to http://localhost:8501")
    
    return Path.cwd() / app_bundle

def main():
    try:
        app_path = create_app_bundle()
        
        # Ask if user wants to move to Desktop
        response = input("\n📋 Move to Desktop? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            desktop = Path.home() / "Desktop"
            if desktop.exists():
                import shutil
                desktop_path = desktop / app_path.name
                if desktop_path.exists():
                    shutil.rmtree(desktop_path)
                shutil.move(str(app_path), str(desktop))
                print(f"✅ Moved to Desktop: {desktop_path}")
            else:
                print("❌ Desktop folder not found")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()