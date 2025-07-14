# standdown/cli.py

import json
from urllib import request, parse

from colorama import init as colorama_init

# Initialize color support on all platforms
colorama_init(autoreset=True)

import uvicorn
from standdown import server

from .config import (
    save_server,
    load_server,
    save_login,
    load_login,
    DEFAULT_PORT,
)



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
    if port == DEFAULT_PORT:
        print(f"[CLIENT] Routing requests to {host}")
    else:
        print(f"[CLIENT] Routing requests to {host}:{port}")

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



def signup_cli(teamname: str, admin_password: str, usernames: list[str], password: str):
    """Send a request to add users to a team."""
    address, port = load_server()
    if not address:
        print("[ERROR] No server configured. Use 'sd conn <address>' first.")
        return

    url = f"http://{address}:{port}/teams/{teamname}/users"
    data = json.dumps({
        "admin_password": admin_password,
        "usernames": usernames,
        "password": password,
    }).encode("utf-8")
    req = request.Request(url, data=data, headers={"Content-Type": "application/json"})

    try:
        with request.urlopen(req) as resp:
            if 200 <= resp.status < 300:
                print("[CLIENT] Users created")
            else:
                print(f"[ERROR] Server responded with status {resp.status}")
    except Exception as exc:
        try:
            body = exc.read().decode()
            print(f"[ERROR] {body}")
        except Exception:
            print(f"[ERROR] {exc}")



def login_cli(teamname: str, username: str, password: str):
    """Login a user and store the returned token."""
    address, port = load_server()
    if not address:
        print("[ERROR] No server configured. Use 'sd conn <address>' first.")
        return

    url = f"http://{address}:{port}/login"
    data = json.dumps({
        "team_name": teamname,
        "username": username,
        "password": password,
    }).encode("utf-8")
    req = request.Request(url, data=data, headers={"Content-Type": "application/json"})

    try:
        with request.urlopen(req) as resp:
            body = resp.read().decode()
            if 200 <= resp.status < 300:
                token = json.loads(body).get("token")
                if token:
                    save_login(teamname, token, username)
                    print("[CLIENT] Logged in")
                else:
                    print("[ERROR] Invalid response from server")
            else:
                print(f"[ERROR] Server responded with status {resp.status}: {body}")
    except Exception as exc:
        try:
            body = exc.read().decode()
            print(f"[ERROR] {body}")
        except Exception:
            print(f"[ERROR] {exc}")


def send_message_cli(message: str, flag: str | None):
    """Send a message to the server with optional flag."""
    address, port = load_server()
    if not address:
        print("[ERROR] No server configured. Use 'sd conn <address>' first.")
        return

    team, token, username = load_login()
    if not team or not token or not username:
        print("[ERROR] Not logged in. Use 'sd login <team> <username> <password>' first.")
        return

    url = f"http://{address}:{port}/messages"
    data = json.dumps({
        "team_name": team,
        "username": username,
        "token": token,
        "message": message,
        "flag": flag,
    }).encode("utf-8")

    req = request.Request(url, data=data, headers={"Content-Type": "application/json"})

    try:
        with request.urlopen(req) as resp:
            body = resp.read().decode()
            if 200 <= resp.status < 300:
                print("[CLIENT] Message sent")
            else:
                print(f"[ERROR] Server responded with status {resp.status}: {body}")
    except Exception as exc:
        try:
            body = exc.read().decode()
            print(f"[ERROR] {body}")
        except Exception:
            print(f"[ERROR] {exc}")


from datetime import datetime


COLOR_CODES = [
    "\033[31m",  # red
    "\033[32m",  # green
    "\033[33m",  # yellow
    "\033[34m",  # blue
    "\033[35m",  # magenta
    "\033[36m",  # cyan
]

_user_colors: dict[str, str] = {}


def _color_for_user(username: str) -> str:
    if username not in _user_colors:
        index = len(_user_colors) % len(COLOR_CODES)
        _user_colors[username] = COLOR_CODES[index]
    return _user_colors[username]


def _fetch_messages(url: str) -> list[dict]:
    req = request.Request(url)
    try:
        with request.urlopen(req) as resp:
            body = resp.read().decode()
            if 200 <= resp.status < 300:
                data = json.loads(body)
                msgs = data.get("messages", [])
                msgs.sort(key=lambda m: m.get("username", ""))
                return msgs
            else:
                print(f"[ERROR] Server responded with status {resp.status}: {body}")
    except Exception as exc:
        try:
            body = exc.read().decode()
            print(f"[ERROR] {body}")
        except Exception:
            print(f"[ERROR] {exc}")
    return []


def show_team_cli():
    """Display the team's pinned messages, standup messages and blockers."""
    address, port = load_server()
    if not address:
        print("[ERROR] No server configured. Use 'sd conn <address>' first.")
        return

    team, token, username = load_login()
    if not team or not token or not username:
        print("[ERROR] Not logged in. Use 'sd login <team> <username> <password>' first.")
        return

    base_url = f"http://{address}:{port}/teams/{team}/messages"
    params = parse.urlencode({"username": username, "token": token})

    all_msgs = _fetch_messages(f"{base_url}?{params}")
    pinned = [m for m in all_msgs if m.get("msg_type") == "pin"]
    blockers = [m for m in all_msgs if m.get("msg_type") == "blockers"]
    messages = [m for m in all_msgs if m.get("msg_type") is None]
    

    def _print_section(title: str, items: list[dict]):
        if not items:
            return
        print(f"//{title}")
        for msg in items:
            ts = datetime.fromisoformat(msg["timestamp"])
            delta = datetime.utcnow() - ts
            hours, rem = divmod(int(delta.total_seconds()), 3600)
            minutes = rem // 60
            color = _color_for_user(msg["username"])
            reset = "\033[0m"
            print(f"{color}{msg['username']}{reset}: {msg['content']} ({hours:02d}:{minutes:02d} ago)")
        print()

    if pinned:
        _print_section("Pinned", pinned)
    if messages:
        _print_section("Messages", messages)
    if blockers:
        _print_section("Blockers", blockers)
