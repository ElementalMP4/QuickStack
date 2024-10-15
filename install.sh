#!/bin/bash

INSTALL_DIR=

if [ $OSTYPE == "linux-gnu" ]; then
    INSTALL_DIR="/usr/local/bin/qs"
else
    INSTALL_DIR=$HOME/bin/qs
fi

mkdir -p $HOME/bin
cp ./quickstack.py $INSTALL_DIR
chmod +x $INSTALL_DIR