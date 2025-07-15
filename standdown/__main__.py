# standdown/__main__.py

import argparse

from standdown.cli import (
    start_server,
    connect,
    create_team_cli,
    show_team_cli,
    show_logs_cli,
    signup_cli,
    login_cli,
    promote_cli,
    send_message_cli,
    deactivate_messages_cli,
    reset_password_cli,
    add_task_cli,
    assign_task_cli,
    list_tasks_cli,
    list_all_tasks_cli,
)

from standdown.config import DEFAULT_PORT
from pathlib import Path


def main():
    # If the first argument is not a known subcommand, treat the entire
    # invocation as a message to post.
    known = {
        'server', 'conn', 'create', 'signup', 'login', 'msg',
        'blockers', 'pin', 'team', 'resetpwd', 'done',
        'today', 'yesterday', 'manager', 'add', 'assign', 'tasks', 'list'
    }
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == '.':
            message = ' '.join(sys.argv[2:])
            send_message_cli(message, None)
            return
        if sys.argv[1] not in known:
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

    # Subcommand: sd manager <team> <adminpwd> <username>
    manager_parser = subparsers.add_parser('manager', help='Promote a user to manager')
    manager_parser.add_argument('teamname', help='Team name')
    manager_parser.add_argument('adminpwd', help='Admin password')
    manager_parser.add_argument('username', help='Username to promote')


    # Subcommand: sd login <team> <username> <password>
    login_parser = subparsers.add_parser('login', help='Login as a user')
    login_parser.add_argument('teamname', help='Team name')
    login_parser.add_argument('username', help='Username')

    # Subcommand: sd resetpwd <old> <new> <new>
    reset_parser = subparsers.add_parser('resetpwd', help='Change your password')
    reset_parser.add_argument('old', help='Current password')
    reset_parser.add_argument('new', help='New password')
    reset_parser.add_argument('new2', help='Repeat new password')

    # Subcommand: sd msg <message>
    msg_parser = subparsers.add_parser('msg', help='Send a message')
    msg_parser.add_argument('message', help='Message text')

    # Subcommand: sd blockers <message> or logs
    blockers_parser = subparsers.add_parser('blockers', help='Send a blockers message or view logs')
    blockers_parser.add_argument('params', nargs=argparse.REMAINDER, help="Message text or 'today'/'yesterday'")

    # Subcommand: sd pin <message> or logs
    pin_parser = subparsers.add_parser('pin', help='Send a pin message or view logs')
    pin_parser.add_argument('params', nargs=argparse.REMAINDER, help="Message text or 'today'/'yesterday'")

    # Subcommand: sd today [user...]
    today_parser = subparsers.add_parser('today', help='Show today\'s standup logs')
    today_parser.add_argument('users', nargs='*', help='Optional usernames')

    # Subcommand: sd yesterday [user...]
    yest_parser = subparsers.add_parser('yesterday', help='Show yesterday\'s standup logs')
    yest_parser.add_argument('users', nargs='*', help='Optional usernames')
    # Subcommand: sd add <task>
    add_parser = subparsers.add_parser('add', help='Add a task')
    add_parser.add_argument('taskname', help='Task name')
    # Subcommand: sd assign <tag> <username>
    assign_parser = subparsers.add_parser('assign', help='Assign a task to users')
    assign_parser.add_argument('tag', help='Task tag')
    assign_parser.add_argument('usernames', nargs='+', help='Users to assign to')
    # Subcommand: sd tasks
    tasks_parser = subparsers.add_parser('tasks', help='List tasks assigned to you')
    # Subcommand: sd list
    list_parser = subparsers.add_parser('list', help='List all tasks for the team')
    # Subcommand: sd team
    team_parser = subparsers.add_parser("team", help="Show team standup")

    # Subcommand: sd done
    done_parser = subparsers.add_parser('done', help='Clear your standup message')

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

    elif args.command == 'manager':
        promote_cli(args.teamname, args.adminpwd, args.username)

    elif args.command == 'login':
        login_cli(args.teamname, args.username, args.password)

    elif args.command == 'resetpwd':
        reset_password_cli(args.old, args.new, args.new2)

    elif args.command == 'msg':
        send_message_cli(args.message, 'msg')
    elif args.command == 'blockers':
        if not args.params:
            print("[ERROR] Provide a message or 'today'/'yesterday'")
        else:
            action = args.params[0]
            rest = args.params[1:]
            if action in ('today', 'yesterday'):
                show_logs_cli(action, 'blockers', rest)
            elif action == 'done':
                deactivate_messages_cli('blockers')
            else:
                send_message_cli(' '.join(args.params), 'blockers')
    elif args.command == 'pin':
        if not args.params:
            print("[ERROR] Provide a message or 'today'/'yesterday'")
        else:
            action = args.params[0]
            rest = args.params[1:]
            if action in ('today', 'yesterday'):
                show_logs_cli(action, 'pin', rest)
            elif action == 'done':
                deactivate_messages_cli('pin')
            else:
                send_message_cli(' '.join(args.params), 'pin')
    elif args.command == 'add':
        add_task_cli(args.taskname)
    elif args.command == 'assign':
        assign_task_cli(args.tag, args.usernames)
    elif args.command == 'tasks':
        list_tasks_cli()
    elif args.command == 'list':
        list_all_tasks_cli()
    elif args.command == 'done':
        deactivate_messages_cli(None)
    elif args.command == 'team':
        show_team_cli()
    elif args.command == 'today':
        show_logs_cli('today', None, args.users)
    elif args.command == 'yesterday':
        show_logs_cli('yesterday', None, args.users)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
