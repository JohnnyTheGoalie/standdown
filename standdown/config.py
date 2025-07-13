import json
from pathlib import Path

DEFAULT_PORT = 8000
CONFIG_PATH = Path.home() / ".standdown_config.json"


def _read() -> dict:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {}


def _write(data: dict):
    CONFIG_PATH.write_text(json.dumps(data))


def save_server(address: str, port: int = DEFAULT_PORT):
    data = _read()
    data["address"] = address
    data["port"] = port
    _write(data)


def load_server():
    data = _read()
    return data.get("address"), data.get("port", DEFAULT_PORT)


def save_login(team: str, username: str, token: str):
    """Persist the authenticated team, username and token."""
    data = _read()
    data["team"] = team
    data["username"] = username
    data["token"] = token
    _write(data)


def load_login():
    """Return the stored team, username and token if present."""
    data = _read()
    return data.get("team"), data.get("username"), data.get("token")
