import sys

def main():
    args = sys.argv[1:]

    if not args:
        print("Usage: sd <command>")
        return

    if args[0] in ("conn", "connect"):
        if len(args) != 2:
            print("Usage: sd conn <git-repo-url>")
            return

        from standdown.connect import connect
        connect(args[1])
    else:
        print(f"Unknown command: {args[0]}")
