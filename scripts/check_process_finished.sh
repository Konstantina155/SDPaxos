#!/bin/bash

while true; do
    pid=$(ps -all | grep "client" | grep -v "grep" | awk '{print $1}')

    if [[ -z "$pid" ]]; then
        break
    fi

    sleep 1
done

#aplay ../alert.wav
echo 'Client not running anymore!'