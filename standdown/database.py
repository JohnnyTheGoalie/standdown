
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import hashlib


DATABASE_URL = "sqlite:///standdown.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()



class Team(Base):
    """Database model for a team."""

    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    admin_hash = Column(String, nullable=False)


def hash_password(password: str) -> str:
    """Return a SHA256 hash of the provided password."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def get_team_by_name(db: Session, name: str):
    """Retrieve a team by its name if it exists."""
    return db.query(Team).filter(Team.name == name).first()


def create_team(db: Session, name: str, admin_password: str) -> Team:
    """Create a new team with the hashed admin password."""
    team = Team(name=name, admin_hash=hash_password(admin_password))
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


def get_db():
    """Yield a database session for use with FastAPI dependencies."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



def init_db():
    """Create database tables."""
    Base.metadata.create_all(bind=engine)
