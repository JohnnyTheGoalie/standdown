import json
from pathlib import Path

DEFAULT_PORT = 8000
DEFAULT_SCHEME = "http"
CONFIG_PATH = Path.home() / ".standdown_config.json"


def _read() -> dict:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {}


def _write(data: dict):
    CONFIG_PATH.write_text(json.dumps(data))


def save_server(address: str, port: int = DEFAULT_PORT, scheme: str = DEFAULT_SCHEME):
    data = _read()
    data["address"] = address
    data["port"] = port
    data["scheme"] = scheme
    _write(data)


def load_server():
    data = _read()
    return (
        data.get("address"),
        data.get("port", DEFAULT_PORT),
        data.get("scheme", DEFAULT_SCHEME),
    )


def save_login(team: str, token: str, username: str):
    data = _read()
    data["team"] = team
    data["token"] = token
    data["username"] = username
    _write(data)


def load_login():
    data = _read()
    return data.get("team"), data.get("token"), data.get("username")
