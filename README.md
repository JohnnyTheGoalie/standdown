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
