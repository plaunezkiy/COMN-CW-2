#!/bin/bash

# network settings
sudo tc qdisc add dev lo root netem loss 0.5% delay 10ms rate 5mbit

RECEIVER="127.0.0.1"
PORT=5005
SENDER_FNAME="test.jpg"
RECEIVER_FNAME="recv.jpg"

python3 Receiver1.py $PORT $SENDER_FNAME &
python3 Sender1.py $RECEIVER $PORT $RECEIVER_FNAME &

echo diff $SENDER_FNAME $RECEIVER_FNAME
# clear network settings
sudo tc qdisc del dev lo root