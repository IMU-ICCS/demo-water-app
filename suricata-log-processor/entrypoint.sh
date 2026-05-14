#!/bin/sh

MODE=${MODE:-default}

case "$MODE" in
    default|suricata|alert|publisher)
        exec /app/suricata-alert-publisher.sh
        ;;
    prometheus)
        exec /app/simple-prometheus-exporter.sh
        ;;
    *)
        echo "Unknown MODE: $MODE"
        exit 1
        ;;
esac