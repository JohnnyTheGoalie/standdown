import os
import json
import subprocess
from pathlib import Path

CONFIG_PATH = Path.home() / ".standdown" / "config.json"
REPOS_PATH = Path.home() / ".standdown" / "repos"

def run(cmd, cwd=None, silent=False):
    if not silent:
        print(f"$ {cmd}")
    subprocess.run(cmd, shell=True, cwd=cwd, check=True)

def git_repo_exists(repo_url):
    try:
        subprocess.run(
            f"git ls-remote {repo_url}",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False

def connect(repo_url):
    username = input("What is your standdown username? ").strip()
    project = repo_url.rstrip(".git").split("/")[-1]
    repo_path = REPOS_PATH / project

    if not git_repo_exists(repo_url):
        print("Remote repo does not exist. You're the first user.")
        repo_path.mkdir(parents=True, exist_ok=True)
        run("git init", cwd=repo_path)
        run("git branch -M main", cwd=repo_path)
        (repo_path / "logs").mkdir(exist_ok=True)
        (repo_path / "README.md").write_text("# Standdown logs\n")
        run("git add .", cwd=repo_path)
        run('git commit -m "init: project setup"', cwd=repo_path)
        run(f"git remote add origin {repo_url}", cwd=repo_path)
        run("git push -u origin main", cwd=repo_path)
    else:
        if not repo_path.exists():
            REPOS_PATH.mkdir(parents=True, exist_ok=True)
            run(f"git clone {repo_url} {repo_path}")
        else:
            print("Team already connected.")

    # Save config
    config = {
        "username": username,
        "repo": repo_url,
        "project": project
    }
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

    # Create empty log file
    user_log = repo_path / "logs" / f"{username}.json"
    if not user_log.exists():
        print(f"📝 Creating logs/{username}.json")
        user_log.parent.mkdir(parents=True, exist_ok=True)
        with open(user_log, "w") as f:
            json.dump([], f)
        run(f"git add logs/{username}.json", cwd=repo_path)
        run(f'git commit -m "log: create {username}.json"', cwd=repo_path)
        run("git push", cwd=repo_path)

    print("Connected. You're good to go.")
