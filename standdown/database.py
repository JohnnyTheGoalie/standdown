
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
    DateTime,
    Text,
)
from datetime import datetime
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import hashlib
import secrets


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



class User(Base):
    """Database model for a user belonging to a team."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)



class Token(Base):
    """Authentication token for a user."""

    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)


class Message(Base):
    """Message posted by a user."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    content = Column(Text, nullable=False)
    msg_type = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)



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



def get_user_by_username(db: Session, username: str):
    """Retrieve a user by username if it exists."""
    return db.query(User).filter(User.username == username).first()


def get_user_in_team(db: Session, team_id: int, username: str):
    """Retrieve a user by username within the given team."""
    return (
        db.query(User)
        .filter(User.username == username, User.team_id == team_id)
        .first()
    )


def create_user(db: Session, username: str, password: str, team_id: int) -> User:
    """Create a user belonging to the given team."""
    user = User(username=username,
                password_hash=hash_password(password),
                team_id=team_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user



def create_token(db: Session, user_id: int) -> str:
    """Create and store an authentication token for the user."""
    token_str = secrets.token_hex(16)
    token = Token(token=token_str, user_id=user_id)
    db.add(token)
    db.commit()
    db.refresh(token)
    return token.token


def get_user_for_login(db: Session, team_id: int, username: str, password: str):
    """Return the user if the credentials are valid."""
    user = (
        db.query(User)
        .filter(User.username == username, User.team_id == team_id)
        .first()
    )
    if user and user.password_hash == hash_password(password):
        return user
    return None


def get_user_by_token(db: Session, token_str: str):
    """Return the user associated with the given token string."""
    tok = db.query(Token).filter(Token.token == token_str).first()
    if tok:
        return db.query(User).filter(User.id == tok.user_id).first()
    return None


def deactivate_existing(db: Session, user_id: int, msg_type: str | None):
    """Mark previous active messages of this type as inactive."""
    query = db.query(Message).filter(Message.user_id == user_id, Message.active == True)
    if msg_type is None:
        query = query.filter(Message.msg_type.is_(None))
    else:
        query = query.filter(Message.msg_type == msg_type)
    for msg in query.all():
        msg.active = False
    db.commit()


def create_message(
    db: Session,
    user_id: int,
    team_id: int,
    content: str,
    msg_type: str | None,
) -> Message:
    """Create a message and mark previous ones inactive."""
    deactivate_existing(db, user_id, msg_type)
    msg = Message(
        user_id=user_id,
        team_id=team_id,
        content=content,
        msg_type=msg_type,
        active=True,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg
def get_active_messages(db: Session, team_id: int, msg_type: str | None):
    """Return active messages for the given team and type."""
    query = (
        db.query(User.username, Message.content, Message.timestamp)
        .join(Message, User.id == Message.user_id)
        .filter(Message.team_id == team_id, Message.active == True)
    )
    if msg_type is None:
        query = query.filter(Message.msg_type.is_(None))
    else:
        query = query.filter(Message.msg_type == msg_type)
    return query.order_by(User.username.asc()).all()





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
