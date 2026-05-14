#!/bin/sh

while true; do
    mkdir -p /app/logs/
    set -o pipefail
    python3 -u /app/simple-prometheus-exporter.py 2>&1 | tee -a /app/logs/simple-prometheus-exporter.log
    exit_code=$?

    if [ $exit_code -eq 0 ]; then
        echo "Program exited normally"
        exit 0
    fi

    echo "Program crashed with exit code $exit_code"
    echo "Restarting in 5 seconds..."

    sleep 5
done