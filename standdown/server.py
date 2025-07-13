# standdown/server.py

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session


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



@app.get("/teams/{team_name}/messages")
def get_messages_endpoint(team_name: str, msg_type: str | None = None, db: Session = Depends(get_db)):
    """Return active messages for a team grouped by type."""
    team = get_team_by_name(db, team_name)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    messages = get_active_messages(db, team.id, msg_type)
    result = [
        {
            "username": username,
            "content": content,
            "timestamp": ts.isoformat(),
        }
        for username, content, ts in messages
    ]
    return {"messages": result}

