# standdown/cli.py

import json
from urllib import request

import uvicorn
from standdown import server
from .config import save_server, load_server, DEFAULT_PORT


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


def create_team_cli(name: str, admin_password: str):
    """Send a request to create a new team on the configured server."""
    address, port = load_server()
    if not address:
        print("[ERROR] No server configured. Use 'sd conn <address>' first.")
        return

    url = f"http://{address}:{port}/teams"
    data = json.dumps({"name": name, "admin_password": admin_password}).encode("utf-8")
    req = request.Request(url, data=data, headers={"Content-Type": "application/json"})

    try:
        with request.urlopen(req) as resp:
            if 200 <= resp.status < 300:
                print("[CLIENT] Team created")
            else:
                print(f"[ERROR] Server responded with status {resp.status}")
    except Exception as exc:
        try:
            # attempt to read error body if available
            body = exc.read().decode()
            print(f"[ERROR] {body}")
        except Exception:
            print(f"[ERROR] {exc}")
