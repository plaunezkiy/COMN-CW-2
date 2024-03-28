#!/bin/bash
OUTPUT_FILE="data.txt"
# clear network settings
sudo tc qdisc del dev lo root
# set network settings
sudo tc qdisc add dev lo root netem loss 5% delay 25ms rate 10mbit

RECEIVER="127.0.0.1"
PORT=5005
SENDER_FNAME="test.jpg"
RECEIVER_FNAME="recv.jpg"
TIMEOUT=60
WINDOW_SIZES=(32)

for WINDOW_SIZE in ${WINDOW_SIZES[@]}; do
    printf "Window:${WINDOW_SIZE}\n" >> $OUTPUT_FILE
    for run in {1..5}; do
        python3 Receiver4.py $PORT $RECEIVER_FNAME $WINDOW_SIZE &

        STATS=$(python3 Sender4.py $RECEIVER $PORT $SENDER_FNAME $TIMEOUT $WINDOW_SIZE | tail -1)
        echo $STATS
        printf "${run}. ${STATS}\n" >> $OUTPUT_FILE
        sleep 1
        echo $(diff $SENDER_FNAME $RECEIVER_FNAME )
    done
    printf "\n" >> $OUTPUT_FILE
done


# clear network settings
sudo tc qdisc del dev lo root