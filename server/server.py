import asyncio
from server.websocket import websocket_handler
import websockets
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, required=True, help="IP address (e.g. 192.168.1.1)")
    parser.add_argument("--port", type=int, required=True, help="Port number (1-65535)")
    return parser.parse_args()

async def main():
    args = parse_args()
    async with websockets.serve(websocket_handler, args.host, args.port):
        print(f"Server listening on {args.host}:{args.port}...")
        await asyncio.Future()

asyncio.run(main())