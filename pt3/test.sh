#!/bin/bash
OUTPUT_FILE="data.txt"

DELAYS=(5 25 100)
# DELAY x 2 (both ways) + 10(buffer to process) gives a 
# the optimal (~20) not good since u need for RTT + process
# for 5, use optimal from 2
# clear network settings
sudo tc qdisc del dev lo root
# set network settings
sudo tc qdisc add dev lo root netem loss 5% delay 100ms rate 10mbit

RECEIVER="127.0.0.1"
PORT=5005
SENDER_FNAME="test.jpg"
RECEIVER_FNAME="recv.jpg"
TIMEOUT=210
WINDOWS=(1 2 4 8 16 32 64 128 256)
# TIMEOUTS=(100 75 50 40 30 25 20 15 10 5)

for WINDOW in ${WINDOWS[@]}; do
    printf "Window:${WINDOW}\n" >> $OUTPUT_FILE
    for run in {1..5}; do
        python3 Receiver3.py $PORT $RECEIVER_FNAME &

        STATS=$(python3 Sender3.py $RECEIVER $PORT $SENDER_FNAME $TIMEOUT $WINDOW | tail -1)
        echo $STATS
        printf "${run}. ${STATS}\n" >> $OUTPUT_FILE
        sleep 2
        echo $(diff $SENDER_FNAME $RECEIVER_FNAME )
    done
    printf "\n" >> $OUTPUT_FILE
done


# clear network settings
sudo tc qdisc del dev lo root