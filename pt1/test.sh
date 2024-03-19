#!/bin/bash
RECEIVER="127.0.0.1"
PORT=5005
SENDER_FNAME="test.jpg"
RECEIVER_FNAME="recv.jpg"
python3 Receiver1.py $PORT $SENDER_FNAME &
python3 Sender1.py $RECEIVER $PORT $RECEIVER_FNAME &

echo diff $SENDER_FNAME $RECEIVER_FNAME