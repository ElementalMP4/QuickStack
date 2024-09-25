#!/bin/bash

if [ ! -w "/usr/local/bin" ]; then
    echo "You do not have write permission to '/usr/local/bin'. Try running with sudo."
    exit 1
fi
cp "./quickstack.py" "/usr/local/bin/quickstack"

chmod +x "/usr/local/bin/quickstack"

if [ $? -eq 0 ]; then
    echo "Installation successful!"
else
    echo "Error during installation."
    exit 1
fi
