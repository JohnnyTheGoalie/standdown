import json
from pathlib import Path
import logging

DEFAULT_PORT = 8000
CONFIG_PATH = Path.home() / ".standdown_config.json"

def save_server(address: str, port: int = DEFAULT_PORT):
    CONFIG_PATH.write_text(json.dumps({"address": address, "port": port}))


def load_server():
    if CONFIG_PATH.exists():
        data = json.loads(CONFIG_PATH.read_text())
        return data.get("address"), data.get("port", DEFAULT_PORT)
    return None, DEFAULT_PORT
