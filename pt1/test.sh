#!/bin/bash
# clear network settings
sudo tc qdisc del dev lo root
# network settings
sudo tc qdisc add dev lo root netem loss 0% delay 5ms rate 10mbit

RECEIVER="127.0.0.1"
PORT=5005
SENDER_FNAME="test.jpg"
RECEIVER_FNAME="recv.jpg"

python3 Receiver1.py $PORT $SENDER_FNAME &
python3 Sender1.py $RECEIVER $PORT $RECEIVER_FNAME
sleep 1
echo $(diff $SENDER_FNAME $RECEIVER_FNAME)
# clear network settings
sudo tc qdisc del dev lo root