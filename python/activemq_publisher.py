import stomp
import json
import time

class ActiveMQPublisher:
    """
    Publishes events (dictionaries) to a an ActiveMQ broker via STOMP.
    """
    def __init__(self, host='localhost', port=61613, queue='/queue/alerts', username=None, password=None):
        self.host = host
        self.port = port
        self.queue = queue
        self.username = username
        self.password = password
        self.conn = stomp.Connection12([(self.host, self.port)])
        self._connect()

    def _connect(self):
        """Establish a connection to the broker."""
        #self.conn.set_listener('', stomp.PrintingListener())  # optional: prints connection events
        if self.username and self.password:
            self.conn.connect(login=self.username, passcode=self.password, wait=True)
        else:
            self.conn.connect(wait=True)
        print(f"Connected to ActiveMQ at {self.host}:{self.port}, publishing to {self.queue}")

    def publish(self, flat_entry):
        """
        Publishes a flat_entry dictionary as a JSON string to the queue.
        """
        try:
            message = json.dumps(flat_entry)
            self.conn.send(
                destination=self.queue,
                body=message,
                headers={'type':'textMessage', 'amq-msg-type':'text'},  # ensures broker treats as text
                persistent='true')
            print("Published message:", message)
        except Exception as e:
            print("Error publishing message:", e)
            # Optionally reconnect on failure
            time.sleep(1)
            self._connect()

    def disconnect(self):
        """Disconnect from broker."""
        self.conn.disconnect()
