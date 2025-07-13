# standdown/__main__.py

import argparse

from standdown.cli import (
    start_server,
    connect,
    create_team_cli,
    signup_cli,
    login_cli,
    send_message_cli,
)

from standdown.config import DEFAULT_PORT
from pathlib import Path


def main():
    # If the first argument is not a known subcommand, treat the entire
    # invocation as a message to post.
    known = {
        'server', 'conn', 'create', 'signup', 'login', 'msg', 'blockers', 'pin'
    }
    import sys
    if len(sys.argv) > 1 and sys.argv[1] not in known:
        message = ' '.join(sys.argv[1:])
        send_message_cli(message, None)
        return

    parser = argparse.ArgumentParser(prog='sd', description='standdown CLI')

    subparsers = parser.add_subparsers(dest='command')

    # Subcommand: sd server --port 8000
    server_parser = subparsers.add_parser('server', help='Run the standdown server')
    server_parser.add_argument('--port', type=int, default=DEFAULT_PORT,
                               help='Port to run the server on (default: %(default)s)')

    # Subcommand: sd conn <address>
    conn_parser = subparsers.add_parser('conn', help='Set the server address')
    conn_parser.add_argument('address', help='IP/domain optionally with :port')

    # Subcommand: sd create <team> <admin_password>
    create_parser = subparsers.add_parser('create', help='Create a team')
    create_parser.add_argument('teamname', help='Team name')
    create_parser.add_argument('adminpwd', help='Admin password')

    # Subcommand: sd signup <team> <adminpwd> <usernames...> <password>
    signup_parser = subparsers.add_parser('signup', help='Add users to a team')
    signup_parser.add_argument('teamname', help='Team name')
    signup_parser.add_argument('adminpwd', help='Admin password')
    signup_parser.add_argument('users', nargs='+', help='List of usernames followed by password (last arg)')


    # Subcommand: sd login <team> <username> <password>
    login_parser = subparsers.add_parser('login', help='Login as a user')
    login_parser.add_argument('teamname', help='Team name')
    login_parser.add_argument('username', help='Username')

    # Subcommand: sd msg <message>
    msg_parser = subparsers.add_parser('msg', help='Send a message')
    msg_parser.add_argument('message', help='Message text')

    # Subcommand: sd blockers <message>
    blockers_parser = subparsers.add_parser('blockers', help='Send a blockers message')
    blockers_parser.add_argument('message', help='Message text')

    # Subcommand: sd pin <message>
    pin_parser = subparsers.add_parser('pin', help='Send a pin message')
    pin_parser.add_argument('message', help='Message text')

    login_parser.add_argument('password', help='Password')


    args = parser.parse_args()

    if args.command == 'server':
        start_server(args.port)
    elif args.command == 'conn':
        connect(args.address)
    elif args.command == 'create':
        create_team_cli(args.teamname, args.adminpwd)

    elif args.command == 'signup':
        if len(args.users) < 2:
            print("[ERROR] Provide at least one username and a password")
            return
        usernames = args.users[:-1]
        password = args.users[-1]
        signup_cli(args.teamname, args.adminpwd, usernames, password)

    elif args.command == 'login':
        login_cli(args.teamname, args.username, args.password)

    elif args.command == 'msg':
        send_message_cli(args.message, None)
    elif args.command == 'blockers':
        send_message_cli(args.message, 'blockers')
    elif args.command == 'pin':
        send_message_cli(args.message, 'pin')

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
