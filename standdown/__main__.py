# standdown/__main__.py

import argparse
from standdown.cli import start_server

def main():
    parser = argparse.ArgumentParser(prog='sd', description='standdown CLI')

    subparsers = parser.add_subparsers(dest='command')

    # Subcommand: sd server port 8000
    server_parser = subparsers.add_parser('server', help='Run the standdown server')
    server_parser.add_argument('port', type=int, help='Port to run the server on')

    args = parser.parse_args()

    if args.command == 'server':
        start_server(args.port)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
