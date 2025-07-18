# Standdown

A minimal CLI and server prototype.

## Usage

Run the server (default port 8000):

```bash
sd server --port 8000
```

The server uses an SQLite database located in the current working
directory. The database file is created automatically on startup.

Set the target server for API requests:

```bash
sd conn 127.0.0.1:8000
```

If no port is given, `sd conn` uses 8000 by default.

Create a new team on the server:

```bash
sd create <teamname> <adminpwd>
```

The admin password is stored hashed in the server database. Attempting
to create a team that already exists will result in an error message.

Add users to a team (the last argument is the password for all users):

```bash
sd signup <teamname> <adminpwd> <user1> [<user2> ...] <password>
```

User passwords are stored hashed with a unique salt in the server database.

Promote an existing user to manager:

```bash
sd manager <teamname> <adminpwd> <username>
```

Login as a user to receive an authentication token:

```bash
sd login <teamname> <username> <password>
```

The CLI stores the returned token and team name in the configuration file for
future requests.

Logout from the app:

```bash
sd logout
```

Change your password after logging in:

```bash
sd resetpwd <old_password> <new_password> <new_password>
```

The CLI sends your stored username and token with the request so the server
can verify your identity.

Retrieve the current standup messages for your team:

```bash
sd team
```

This command requires that you are logged in. The CLI sends your stored
username and token with the request so that only authenticated team members can
view the messages.

### Sending standup messages

To post a message, simply run `sd <message>`. If your text begins with a word
that matches a subcommand (for example `team`), prefix the message with a dot:

```bash
sd . team is on track
```

The prefix prevents the CLI from interpreting the word as a command. You can
also use `sd msg <message>` explicitly.

Clear your standup messages when they no longer apply:

```bash
sd done
sd pin done
sd blockers done
```

Each command deactivates the corresponding message type for the logged in user.

### Managing tasks

Managers can create tasks for the team:

```bash
sd add <task>
```

The server responds with the hexadecimal tag for the new task, which is also displayed by the CLI.

Managers can assign tasks to multiple team members using the tag:

```bash
sd assign <tag> <user1> [<user2> ...]
```

To assign a task to everyone on the team, use a single dot as the username:

```bash
sd assign <tag> .
```

Team members can view their assigned tasks:

```bash
sd tasks
```

Managers can list every task for the team:

```bash
sd list
```

Managers can remove a task by tag:

```bash
sd remove <tag>
```

Start working on a task you are assigned to:

```bash
sd start <tag>
```

Mark the task as finished when you're done:

```bash
sd end <tag>
```

### Viewing logs

Display today's standup messages:

```bash
sd today
```

Display yesterday's messages for specific users:

```bash
sd yesterday alice bob
```

You can also view only blocker or pinned messages using the corresponding
subcommands:

```bash
sd blockers today
sd blockers yesterday alice
sd pin today
```
