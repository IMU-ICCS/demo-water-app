import os
import streamlit as st
import stomp
import json
import threading
import queue
import time
import pandas as pd
from datetime import datetime

# ----------------------------
# CONFIG
# ----------------------------
BROKER_HOST = os.getenv("BROKER_HOST") or "localhost"
BROKER_PORT = os.getenv("BROKER_PORT") or "61610"
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
TOPIC = os.getenv("TOPIC") or "/topic/attack_probability_score"

# ----------------------------
# Shared buffer (thread-safe)
# ----------------------------
data_queue = queue.Queue()
data_buffer = []

# ----------------------------
# STOMP listener
# ----------------------------
class Listener(stomp.ConnectionListener):
    def on_message(self, frame):
        try:
            msg = json.loads(frame.body)

            value = float(msg.get("metricValue"))
            #timestamp = msg.get("timestamp")
            timestamp = datetime.now().astimezone().isoformat()

            if timestamp is None:
                timestamp = datetime.now().astimezone().isoformat()

            data_queue.put({
                "timestamp": timestamp,
                "value": value
            })

        except Exception as e:
            print("Error parsing message:", e)


def start_stomp():
    conn = stomp.Connection([(BROKER_HOST, BROKER_PORT)])
    conn.set_listener("", Listener())
    conn.connect(USERNAME, PASSWORD, wait=True)
    conn.subscribe(destination=TOPIC, id=1, ack="auto")

# ----------------------------
# Start STOMP in background
# ----------------------------
threading.Thread(target=start_stomp, daemon=True).start()

# ----------------------------
# STREAMLIT UI
# ----------------------------
st.title("📡 Attack Probability score")

chart = st.empty()
status = st.empty()

status.info("Listening to STOMP stream...")

# ----------------------------
# Main loop
# ----------------------------
while True:

    # Drain queue
    while not data_queue.empty():
        data_buffer.append(data_queue.get())

    # Convert to DataFrame
    if data_buffer:
        df = pd.DataFrame(data_buffer)

        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")
        df["timestamp"] = df["timestamp"].dt.strftime("%H:%M:%S")

        chart.line_chart(
            #df.set_index("timestamp")["value"]
            df.set_index("timestamp")
        )

    time.sleep(0.5)