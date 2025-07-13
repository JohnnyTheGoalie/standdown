# standdown/server.py

from fastapi import FastAPI

from .database import init_db

app = FastAPI()


@app.on_event("startup")
def startup_event():
    """Initialize the SQLite database when the server starts."""
    init_db()

@app.get("/")
def read_root():
    return {"message": "Standdown server running"}
