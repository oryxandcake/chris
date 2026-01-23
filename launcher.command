#!/bin/bash
# AES Decryptor Launcher

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if virtual environment exists
if [ ! -d "$DIR/venv" ]; then
    echo "Setting up virtual environment..."
    python3 -m venv "$DIR/venv"
    source "$DIR/venv/bin/activate"
    pip3 install pycryptodome
else
    source "$DIR/venv/bin/activate"
fi

# Run the GUI
python3 "$DIR/aes_decryptor_gui.py"
