#!/bin/bash

SCRIPT_PATH="./quickstack.py"
INSTALL_DIR="/usr/local/bin"
SCRIPT_NAME=$(basename "$SCRIPT_PATH")
DEST_PATH="$INSTALL_DIR/$SCRIPT_NAME"

if [ ! -w "$INSTALL_DIR" ]; then
    echo "You do not have write permission to '$INSTALL_DIR'. Try running with sudo."
    exit 1
fi

echo "Installing $SCRIPT_NAME to $INSTALL_DIR..."
cp "$SCRIPT_PATH" "$DEST_PATH"

chmod +x "$DEST_PATH"

if [ $? -eq 0 ]; then
    echo "Installation successful!"
else
    echo "Error during installation."
    exit 1
fi
