#!/bin/bash

# Script to create an AppleScript application for AES Decryptor

APP_NAME="AES Decryptor"
APP_DIR="/Users/chris/Documents/Claude"

# Create the AppleScript
cat > /tmp/aes_decryptor.applescript << 'EOF'
on run
    set baseDir to "/Users/chris/Documents/Claude"
    set venvDir to baseDir & "/venv"
    set scriptPath to baseDir & "/aes_decryptor_gui.py"

    -- Check if venv exists
    tell application "System Events"
        set venvExists to exists folder venvDir
    end tell

    if not venvExists then
        display dialog "First-time setup: Installing dependencies..." & return & return & "This will take a moment." buttons {"OK"} default button 1 with icon note

        -- Create venv and install dependencies
        do shell script "cd " & quoted form of baseDir & " && python3 -m venv venv && source venv/bin/activate && pip3 install pycryptodome"

        display dialog "Setup complete! Starting AES Decryptor..." buttons {"OK"} default button 1 with icon note giving up after 2
    end if

    -- Run the GUI
    do shell script "cd " & quoted form of baseDir & " && source venv/bin/activate && python3 " & quoted form of scriptPath & " > /dev/null 2>&1 &"
end run
EOF

# Compile the AppleScript into an application
osacompile -o "$APP_DIR/$APP_NAME.app" /tmp/aes_decryptor.applescript

# Clean up
rm /tmp/aes_decryptor.applescript

echo "Application created successfully!"
echo "You can now double-click '$APP_NAME.app' in $APP_DIR"
