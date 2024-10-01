#!/bin/bash

INSTALL_DIR=

if [ $OSTYPE == "linux-gnu" ]; then
    INSTALL_DIR="/usr/local/bin/quickstack"
else
    INSTALL_DIR=$HOME/bin/quickstack
fi

mkdir -p $HOME/bin
cp ./quickstack.py $INSTALL_DIR
chmod +x $INSTALL_DIR