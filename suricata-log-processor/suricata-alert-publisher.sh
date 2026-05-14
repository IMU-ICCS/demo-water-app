#!/bin/sh

while true; do
    python3 -u /app/suricata-alert-publisher.py
    exit_code=$?

    if [ $exit_code -eq 0 ]; then
        echo "Program exited normally"
        exit 0
    fi

    echo "Program crashed with exit code $exit_code"
    echo "Restarting in 5 seconds..."

    sleep 5
done