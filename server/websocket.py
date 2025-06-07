from server.action import Action
import json

next_client_id = 0
connected_clients = {}

async def websocket_handler(connection):
    global connected_clients
    current_client_id = get_next_client_id()
    connected_clients[current_client_id] = connection
    print(f"Client connected: [id: {current_client_id}, addr: {connection.remote_address}]")
    
    # Wysyłamy innym, że nowy gracz dołączył
    await broadcast_system_message(f"JOIN:{current_client_id}")
    
    try:
        async for message in connection:
            await broadcast_message(current_client_id, message)
    finally:
        print(f"Client disconnected: [id: {current_client_id}, addr: {connection.remote_address}]")
        del connected_clients[current_client_id]
        await broadcast_system_message(f"LEAVE:{current_client_id}")

async def broadcast_message(sender_id, message):
    # Dodaj player_id do wiadomości
    message_json = json.loads(message)
    message_json["player_id"] = sender_id
    full_message = json.dumps(message_json)

    for client_id, conn in connected_clients.items():
        try:
            await conn.send(full_message)
        except Exception as e:
            print(f"Error sending to client {client_id}: {e}")

async def broadcast_system_message(msg):
    for client_id, conn in connected_clients.items():
        try:
            await conn.send(json.dumps({"system": msg}))
        except Exception as e:
            print(f"Error sending system message to client {client_id}: {e}")

def get_next_client_id():
    global next_client_id
    next_client_id += 1
    return next_client_id
