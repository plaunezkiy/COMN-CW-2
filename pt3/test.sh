#!/bin/bash
OUTPUT_FILE="data.txt"
# clear network settings
sudo tc qdisc del dev lo root
# set network settings
sudo tc qdisc add dev lo root netem loss 100% delay 10ms rate 5mbit

RECEIVER="127.0.0.1"
PORT=5005
SENDER_FNAME="test.jpg"
RECEIVER_FNAME="recv.jpg"

# TIMEOUTS=(5 10 15 20 25 30 40 50 75 100)
TIMEOUTS=(100 75 50 40 30 25 20 15 10 5)

for RETRY_TIMEOUT in ${TIMEOUTS[@]}; do
    printf "${RETRY_TIMEOUT}ms\n" >> $OUTPUT_FILE
    for run in {1..5}; do
        python3 Receiver2.py $PORT $RECEIVER_FNAME &

        STATS=$(python3 Sender2.py $RECEIVER $PORT $SENDER_FNAME $RETRY_TIMEOUT | tail -1)
        echo $STATS
        printf "${run}. ${STATS}\n" >> $OUTPUT_FILE
        sleep 1
        echo $(diff $SENDER_FNAME $RECEIVER_FNAME )
    done
    printf "\n" >> $OUTPUT_FILE
done


# clear network settings
sudo tc qdisc del dev lo root