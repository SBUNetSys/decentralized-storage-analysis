#!/bin/bash
# Announce the uploaded files to the network
# Usage: ./announce.sh filesize
# Example: ./announce.sh 1M
if [ "$#" -ne 2 ]; then
    echo "Usage: ./announce.sh <size> <loc>"
    echo "Example: ./announce.sh 1M us"
    exit 1
fi

ipfs daemon &
sleep 10
python3 re_announce_with_size.py --size=$1 --loc=$2