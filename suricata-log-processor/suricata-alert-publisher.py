import os
import calendar
import time
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from activemq_publisher import ActiveMQPublisher
import atexit


class JsonFileMonitor(FileSystemEventHandler):
    def __init__(self, filepath, process_func):
        self.filepath = os.path.abspath(filepath)
        self.directory = os.path.dirname(self.filepath)
        self.filename = os.path.basename(self.filepath)
        self.process_func = process_func

        self.file = None
        self.inode = None
        self.buffer = ""

        self._open_file(ignore_existing=True)

    def _open_file(self, ignore_existing=False):
        if self.file:
            self.file.close()

        self.file = open(self.filepath, "r", encoding="utf-8")
        self.inode = os.fstat(self.file.fileno()).st_ino

        if ignore_existing:
            # Move to end so we ignore old content
            self.file.seek(0, os.SEEK_END)

    def _check_rotation(self):
        try:
            current_inode = os.stat(self.filepath).st_ino
            if current_inode != self.inode:
                print("File rotation detected.")
                self._open_file(ignore_existing=False)
        except FileNotFoundError:
            # File temporarily missing (during rotation)
            pass

    def _read_new_lines(self):
        while True:
            chunk = self.file.read()
            if not chunk:
                break

            self.buffer += chunk

            while "\n" in self.buffer:
                line, self.buffer = self.buffer.split("\n", 1)
                line = line.strip()
                if line:
                    try:
                        obj = json.loads(line)
                        self.process_func(obj)
                    except json.JSONDecodeError:
                        print("Invalid JSON skipped:", line)

    def on_modified(self, event):
        if os.path.abspath(event.src_path) == self.filepath:
            self._check_rotation()
            self._read_new_lines()

    def on_created(self, event):
        if os.path.abspath(event.src_path) == self.filepath:
            print("File recreated.")
            self._open_file(ignore_existing=False)


def process_json(obj):
    """
    Extracts relevant fields from the alert JSON and publish to EMS.
    """
    try:
        if obj["event_type"] == "alert":
            alert_entry = {
                "metricValue": -1,
                "level": -1,
                "timestamp": calendar.timegm(time.gmtime()),
                "ts": obj.get("timestamp"),
                "src_ip": obj.get("src_ip"),
                "src_port": obj.get("src_port"),
                "dest_ip": obj.get("dest_ip"),
                "dest_port": obj.get("dest_port"),
                "proto": obj.get("proto"),
                "signature_id": obj.get("alert", {}).get("signature_id"),
                "signature": obj.get("alert", {}).get("signature"),
                "severity": obj.get("alert", {}).get("severity"),
            }
            #print("Alert:", alert_entry)

            # Publish to EMS
            publisher.publish(alert_entry)

    except Exception as e:
        print("Error processing alert: OBJ: ", obj)
        print("Error processing alert: ERR: ", e)


ACTIVEMQ_URL = os.getenv("ACTIVEMQ_URL") or "localhost"
ACTIVEMQ_PORT = os.getenv("ACTIVEMQ_PORT") or "61610"
ACTIVEMQ_USERNAME = os.getenv("ACTIVEMQ_USERNAME")
ACTIVEMQ_PASSWORD = os.getenv("ACTIVEMQ_PASSWORD")
ACTIVEMQ_TOPIC = os.getenv("ACTIVEMQ_TOPIC") or "/topic/alerts_SENSOR"
SURICATA_EVE_PATH = os.getenv("SURICATA_EVE_PATH") or "/var/log/suricata/eve.json"


def main():
    global publisher
    publisher = ActiveMQPublisher(ACTIVEMQ_URL, port=int(ACTIVEMQ_PORT),
                                  queue=ACTIVEMQ_TOPIC,
                                  username=ACTIVEMQ_USERNAME, password=ACTIVEMQ_PASSWORD)
    atexit.register(lambda: publisher.disconnect())

    filepath = SURICATA_EVE_PATH  # NDJSON file
    event_handler = JsonFileMonitor(filepath, process_json)

    observer = Observer()
    observer.schedule(event_handler, event_handler.directory, recursive=False)
    observer.start()

    print(f"Monitoring {filepath} for new alerts...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    main()
