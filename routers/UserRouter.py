from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas.UsersSchema import UserCreate, UserResponse
from services.UsersService import create_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user.username, user.email, user.password)
