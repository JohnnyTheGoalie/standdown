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

User passwords are stored hashed in the server database.


Login as a user to receive an authentication token:

```bash
sd login <teamname> <username> <password>
```


The CLI stores the returned token along with the team name and username in the
configuration file for future requests.

