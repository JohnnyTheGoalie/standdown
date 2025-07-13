# standdown/cli.py

import uvicorn
from standdown import server
from .config import save_server, DEFAULT_PORT


def connect(address: str):
    if ':' in address:
        host, port_str = address.split(':', 1)
        try:
            port = int(port_str)
        except ValueError:
            print(f"[ERROR] Invalid port in address '{address}'")
            return
    else:
        host = address
        port = DEFAULT_PORT

    save_server(host, port)
    print(f"[CLIENT] Set server to {host}:{port}")

def start_server(port: int = DEFAULT_PORT):
    print(f"[SERVER] Starting standdown FastAPI server on port {port}")
    uvicorn.run(server.app, host="0.0.0.0", port=port)
