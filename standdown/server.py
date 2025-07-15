# standdown/server.py

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta


from .database import (
    init_db,
    get_db,
    get_team_by_name,
    create_team,
    hash_password,
    get_user_by_username,
    get_user_in_team,
    create_user,
    get_active_messages,
    create_token,
    get_user_for_login,
    get_user_by_token,
    create_message,
    deactivate_existing,
    change_user_password,
    get_messages_for_day,
    set_user_role,
    create_task,
    get_task_by_tag,
    assign_task_multiple,
)


app = FastAPI()


@app.on_event("startup")
def startup_event():
    """Initialize the SQLite database when the server starts."""
    init_db()

@app.get("/")
def read_root():
    return {"message": "Standdown server running"}


class TeamCreate(BaseModel):
    name: str
    admin_password: str



class UsersCreate(BaseModel):
    admin_password: str
    usernames: list[str]
    password: str



class LoginRequest(BaseModel):
    team_name: str
    username: str
    password: str


class MessagePost(BaseModel):
    team_name: str
    username: str
    token: str
    message: str
    flag: str | None = None


class DeactivateRequest(BaseModel):
    team_name: str
    username: str
    token: str
    flag: str | None = None


class PasswordChange(BaseModel):
    team_name: str
    username: str
    token: str
    old_password: str
    new_password: str


class PromoteRequest(BaseModel):
    admin_password: str
    username: str


class TaskCreate(BaseModel):
    team_name: str
    username: str
    token: str
    task: str


class TaskAssign(BaseModel):
    team_name: str
    username: str
    token: str
    tag: str
    assignees: list[str]



@app.post("/teams")
def create_team_endpoint(payload: TeamCreate, db: Session = Depends(get_db)):
    """Create a new team if it doesn't already exist."""
    existing = get_team_by_name(db, payload.name)
    if existing:
        raise HTTPException(status_code=400, detail="Team already exists")
    create_team(db, payload.name, payload.admin_password)
    return {"message": "Team created"}



@app.post("/teams/{team_name}/users")
def create_users_endpoint(team_name: str, payload: UsersCreate, db: Session = Depends(get_db)):
    """Add users to a team after verifying the admin password."""
    team = get_team_by_name(db, team_name)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    if team.admin_hash != hash_password(payload.admin_password):
        raise HTTPException(status_code=403, detail="Invalid admin password")

    created = []
    for username in payload.usernames:
        if get_user_in_team(db, team.id, username):
            continue
        user = create_user(db, username, payload.password, team.id)
        created.append(user.username)

    return {"message": "Users created", "users": created}


@app.post("/teams/{team_name}/manager")
def promote_user_endpoint(team_name: str, payload: PromoteRequest, db: Session = Depends(get_db)):
    """Promote an existing user to manager role."""
    team = get_team_by_name(db, team_name)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    if team.admin_hash != hash_password(payload.admin_password):
        raise HTTPException(status_code=403, detail="Invalid admin password")

    user = get_user_in_team(db, team.id, payload.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    set_user_role(db, user, "manager")
    return {"message": "User promoted"}



@app.post("/login")
def login_endpoint(payload: LoginRequest, db: Session = Depends(get_db)):
    """Validate credentials and return an auth token."""
    team = get_team_by_name(db, payload.team_name)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    user = get_user_for_login(db, team.id, payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid credentials")

    token = create_token(db, user.id)
    return {"token": token}


@app.post("/tasks")
def add_task_endpoint(payload: TaskCreate, db: Session = Depends(get_db)):
    """Create a task for a team if the user is a manager."""
    team = get_team_by_name(db, payload.team_name)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    user = get_user_in_team(db, team.id, payload.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token_user = get_user_by_token(db, payload.token)
    if not token_user or token_user.id != user.id:
        raise HTTPException(status_code=403, detail="Invalid token")

    if user.role != "manager":
        raise HTTPException(status_code=403, detail="Insufficient privileges")

    task = create_task(db, team.id, payload.task)
    return {"message": "Task added", "tag": task.tag}


@app.post("/tasks/assign")
def assign_task_endpoint(payload: TaskAssign, db: Session = Depends(get_db)):
    """Assign a task to a user if the requester is a manager."""
    team = get_team_by_name(db, payload.team_name)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    assigner = get_user_in_team(db, team.id, payload.username)
    if not assigner:
        raise HTTPException(status_code=404, detail="User not found")

    token_user = get_user_by_token(db, payload.token)
    if not token_user or token_user.id != assigner.id:
        raise HTTPException(status_code=403, detail="Invalid token")

    if assigner.role != "manager":
        raise HTTPException(status_code=403, detail="Insufficient privileges")

    assignee_ids = []
    for assignee_name in payload.assignees:
        user_obj = get_user_in_team(db, team.id, assignee_name)
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")
        assignee_ids.append(user_obj.id)

    task = get_task_by_tag(db, team.id, payload.tag)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    assign_task_multiple(db, task, assignee_ids)
    return {"message": "Task assigned"}


@app.post("/messages")
def post_message_endpoint(payload: MessagePost, db: Session = Depends(get_db)):
    """Create a message for a user after validating token."""
    team = get_team_by_name(db, payload.team_name)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")


    user = get_user_in_team(db, team.id, payload.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token_user = get_user_by_token(db, payload.token)
    if not token_user or token_user.id != user.id:
        raise HTTPException(status_code=403, detail="Invalid token")

    create_message(db, user.id, team.id, payload.message, payload.flag)
    return {"message": "Message posted"}


@app.post("/messages/done")
def deactivate_messages_endpoint(payload: DeactivateRequest, db: Session = Depends(get_db)):
    """Mark active messages of a given type as inactive for the user."""
    team = get_team_by_name(db, payload.team_name)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    user = get_user_in_team(db, team.id, payload.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token_user = get_user_by_token(db, payload.token)
    if not token_user or token_user.id != user.id:
        raise HTTPException(status_code=403, detail="Invalid token")

    deactivate_existing(db, user.id, payload.flag)
    return {"message": "Messages deactivated"}



@app.get("/teams/{team_name}/messages")
def get_messages_endpoint(
    team_name: str,
    username: str,
    token: str,
    db: Session = Depends(get_db),
):
    """Return active messages for a team.

    The optional ``msg_type`` query parameter can be ``None`` for regular
    messages, a specific flag like ``"pin"`` or ``"blockers"``, or ``"all``" to
    retrieve every active message regardless of flag.
    """

    team = get_team_by_name(db, team_name)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    user = get_user_in_team(db, team.id, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token_user = get_user_by_token(db, token)
    if not token_user or token_user.id != user.id:
        raise HTTPException(status_code=403, detail="Invalid token")

    messages = get_active_messages(db, team.id)
    result = [
        {
            "username": username,
            "content": content,
            "msg_type": mtype,
            "timestamp": ts.isoformat(),
        }
        for username, content, mtype, ts in messages
    ]
    return {"messages": result}


@app.get("/teams/{team_name}/logs")
def get_logs_endpoint(
    team_name: str,
    username: str,
    token: str,
    date: str,
    flag: str = "none",
    users: str | None = None,
    db: Session = Depends(get_db),
):
    """Return messages for a specific day filtered by flag and users."""

    team = get_team_by_name(db, team_name)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    user = get_user_in_team(db, team.id, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token_user = get_user_by_token(db, token)
    if not token_user or token_user.id != user.id:
        raise HTTPException(status_code=403, detail="Invalid token")

    if date == "today":
        target_day = datetime.utcnow().date()
    elif date == "yesterday":
        target_day = datetime.utcnow().date() - timedelta(days=1)
    else:
        raise HTTPException(status_code=400, detail="Invalid date")

    if flag == "none":
        flag_val = None
    else:
        flag_val = flag

    usernames = [u for u in users.split(",") if u] if users else None
    records = get_messages_for_day(db, team.id, target_day, flag_val, usernames)
    result = [
        {
            "username": uname,
            "content": content,
            "msg_type": mtype,
            "timestamp": ts.isoformat(),
        }
        for uname, content, mtype, ts in records
    ]
    return {"messages": result}


@app.post("/resetpwd")
def reset_password_endpoint(payload: PasswordChange, db: Session = Depends(get_db)):
    """Change a user's password after validating token and old password."""
    team = get_team_by_name(db, payload.team_name)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    user = get_user_in_team(db, team.id, payload.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token_user = get_user_by_token(db, payload.token)
    if not token_user or token_user.id != user.id:
        raise HTTPException(status_code=403, detail="Invalid token")

    if user.password_hash != hash_password(payload.old_password):
        raise HTTPException(status_code=403, detail="Invalid password")

    change_user_password(db, user, payload.new_password)
    return {"message": "Password updated"}

