import websocket
import threading
import json
import time
from server.action import Action
from server.action_type import ActionType

class NetworkClient:
    def __init__(self, uri, on_message, on_system):
        self.uri = uri
        self.on_action_received = on_message
        self.on_system_message = on_system

        self.connected = False  # flaga połączenia

        self.ws = websocket.WebSocketApp(
            uri,
            on_open=self.on_open,
            on_close=self.on_close,
            on_error=self.on_error,
            on_message=self.on_message
        )

        self.thread = threading.Thread(target=self.ws.run_forever)
        self.thread.daemon = True
        self.thread.start()

    def wait_until_connected(self, timeout=5.0):
        """Blokuje grę do momentu połączenia z serwerem (max `timeout` sekund)."""
        start = time.time()
        while not self.connected and (time.time() - start) < timeout:
            time.sleep(0.05)
        return self.connected

    def on_open(self, ws):
        self.connected = True
        print("Connected to server.")

    def on_close(self, ws, close_status_code, close_msg):
        print("Disconnected from server.")
        self.connected = False

    def on_error(self, ws, error):
        print(f"WebSocket error: {error}")

    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            if "system" in data:
                self.on_system_message(data["system"])
            else:
                self.on_action_received(data)
        except Exception as e:
            print(f"Failed to process message: {e}")

    def send_action(self, action: Action):
        if not self.connected or not self.ws.sock or not self.ws.sock.connected:
            print("WebSocket not connected yet, skipping action.")
            return

        data = {
            "type": action.type.value,
            "field": action.field
        }
        self.ws.send(json.dumps(data))

    def send_raw(self, data):
        if self.ws and self.ws.sock and self.ws.sock.connected:
            self.ws.send(json.dumps(data))
