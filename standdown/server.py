# standdown/server.py

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .database import init_db, get_db, get_team_by_name, create_team

from .database import init_db

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


@app.post("/teams")
def create_team_endpoint(payload: TeamCreate, db: Session = Depends(get_db)):
    """Create a new team if it doesn't already exist."""
    existing = get_team_by_name(db, payload.name)
    if existing:
        raise HTTPException(status_code=400, detail="Team already exists")
    create_team(db, payload.name, payload.admin_password)
    return {"message": "Team created"}
