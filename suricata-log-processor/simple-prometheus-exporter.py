#
# Copyright (C) 2017-2025 Institute of Communication and Computer Systems (imu.iccs.gr)
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at
# https://www.mozilla.org/en-US/MPL/2.0/
#

from prometheus_client import start_http_server, Counter, Summary, Gauge
from prometheus_client import generate_latest, REGISTRY
import random
from datetime import datetime
import time
import psutil
import os

# Port of Prometheus endpoint
PORT = 9000

# Create a metric to count requests made
REQUEST_COUNT = Counter( 'request_count', 'Number of requests')

# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

# CPU/GPU/RAM usage
cpu_usage = Gauge('cpu_usage_percent', 'CPU usage percentage')
gpu_usage = Gauge('gpu_usage_percent', 'GPU usage percentage')
mem_usage = Gauge('memory_usage_percent', 'RAM usage percentage')

water_usage = Gauge('water_consumption_lpm', 'Instant Water consumption (L/min)')

metrics_to_print = {
    "request_count_total",
    "request_processing_seconds_count",
    "cpu_usage_percent",
    "gpu_usage_percent",
    "memory_usage_percent",
    "water_consumption_lpm",
}

# Parameters file
PARAMS_FILE = os.getenv("PARAMS_FILE") or "params.txt"

def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

def random_from_file(filename):
    lower, upper = 0, 1000  # defaults

    try:
        if os.path.exists(filename):
            #print(f'random_from_file::Reading from PARAMS_FILE: {PARAMS_FILE}')
            with open(filename, 'r') as f:
                line = f.readline().strip()
                if line:
                    parts = line.replace(',', ' ').split()
                    if len(parts) >= 2:
                        lower = float(parts[0])
                        upper = float(parts[1])
                        #print(f'random_from_file::Read from PARAMS_FILE: {lower} - {upper}')
        else:
            print(f'random_from_file::PARAMS_FILE not found {PARAMS_FILE}')
        #print(f'random_from_file::Range: {lower}..{upper}')
    except Exception as e:
        # If anything goes wrong, keep defaults
        print(f'random_from_file::ERROR: {e}')
        pass

    # Generate random number
    # return random.uniform(lower, upper)
    return random.randint(int(lower), int(upper))

# Decorate function with metric.
@REQUEST_TIME.time()
def process_request(t):
    """A dummy function that takes some time."""
    time.sleep(t)
    REQUEST_COUNT.inc()
    cpu_usage.set(get_cpu_usage())
#     gpu_usage
#     mem_usage
#     water_usage.set( random.randint(50, 1000) )
    water_usage.set( random_from_file(PARAMS_FILE) )
    print_current_values()

def print_current_values():
    # Print all metrics in Prometheus exposition format
    #print(generate_latest(REGISTRY).decode("utf-8"))

    # Print only configured metrics' values
    print('--------------------------------------')
    print(datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z%z"))
    print('--------------------------------------')
    for metric in REGISTRY.collect():
        for sample in metric.samples:
            if sample.name in metrics_to_print:
                print(f"{sample.name} = {sample.value}")

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(PORT)
    print(f'Exposing Prometheus metrics at port: {PORT}')
    # Generate some requests.
    while True:
        try:
            # process_request(5 + 5 * random.random())
            process_request(2)
        except KeyboardInterrupt:
            print("Interrupted")
            exit(0)