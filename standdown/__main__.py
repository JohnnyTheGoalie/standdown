# standdown/__main__.py

import argparse
from standdown.cli import start_server, connect
from standdown.config import DEFAULT_PORT
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(prog='sd', description='standdown CLI')

    subparsers = parser.add_subparsers(dest='command')

    # Subcommand: sd server --port 8000
    server_parser = subparsers.add_parser('server', help='Run the standdown server')
    server_parser.add_argument('--port', type=int, default=DEFAULT_PORT,
                               help='Port to run the server on (default: %(default)s)')

    # Subcommand: sd conn <address>
    conn_parser = subparsers.add_parser('conn', help='Set the server address')
    conn_parser.add_argument('address', help='IP/domain optionally with :port')


    args = parser.parse_args()

    if args.command == 'server':
        start_server(args.port)
    elif args.command == 'conn':
        connect(args.address)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
