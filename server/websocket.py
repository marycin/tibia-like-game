from action import Action
import json

next_client_id = 0
connected_clients = {}

async def websocket_handler(connection, path):
    global connected_clients
    current_client_id = get_next_client_id()
    connected_clients[current_client_id] = connection
    print(f"Client connected: [id: {current_client_id}, addr: {connection.remote_address}]")
    try:
        async for message in connection:
            parse_message(current_client_id, message)
    finally:
        print(f"Client disconnected: [id: {current_client_id}, addr: {connection.remote_address}]")
        del connected_clients[current_client_id]

def parse_message(current_client_id, message):
    try:
        message_json = json.loads(message)
        action = Action.from_dict(message_json)
        print(current_client_id, action)
    except TypeError:
        print("Invalid message format")

def get_next_client_id():
    global next_client_id
    next_client_id += 1
    return next_client_id