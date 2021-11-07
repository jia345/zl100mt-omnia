#!/bin/sh

count=0
while true; do
    echo $count
    echo "$count" | socat udp-datagram:$1:$2 -
    count=$(($count+1))
    sleep 0.1
done

