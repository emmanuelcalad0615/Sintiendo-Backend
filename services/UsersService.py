from sqlalchemy.orm import Session
from models.user import User
from services.utils import hash_password

def create_user(db: Session, username: str, email: str, password: str):
    hashed_pw = hash_password(password)
    new_user = User(username=username, email=email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
