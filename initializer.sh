#!/usr/bin/env bash

clear

EPOCHS = 50

echo "Start miner with genesis block"
gnome-terminal --window-with-profile=nocl -e "python3 miner.py -g 1 -l 10"

sleep 3

for i in `seq 0 9`;
        do
                echo "Start client $i"
                gnome-terminal --window-with-profile=nocl -e "python3 client.py -d \"data/d$i.d\" -e $EPOCHS"
        done


# echo "Start client 0"
# gnome-terminal --window-with-profile=nocl -e "python3 client.py -d \"data/d0.d\" -e 20"
# echo "Start client 1"
# gnome-terminal --window-with-profile=nocl -e "python3 client.py -d \"data/d1.d\" -e 20"
# echo "Start client 2"
# gnome-terminal --window-with-profile=nocl -e "python3 client.py -d \"data/d2.d\" -e 20"
# echo "Start client 3"
# gnome-terminal --window-with-profile=nocl -e "python3 client.py -d \"data/d3.d\" -e 20"
# echo "Start client 4"
# gnome-terminal --window-with-profile=nocl -e "python3 client.py -d \"data/d4.d\" -e 20"
# echo "Start client 5"
# gnome-terminal --window-with-profile=nocl -e "python3 client.py -d \"data/d5.d\" -e 20"
# echo "Start client 6"
# gnome-terminal --window-with-profile=nocl -e "python3 client.py -d \"data/d6.d\" -e 20"
# echo "Start client 7"
# gnome-terminal --window-with-profile=nocl -e "python3 client.py -d \"data/d7.d\" -e 20"
# echo "Start client 8"
# gnome-terminal --window-with-profile=nocl -e "python3 client.py -d \"data/d8.d\" -e 20"
# echo "Start client 9"
# gnome-terminal --window-with-profile=nocl -e "python3 client.py -d \"data/d9.d\" -e 20"
