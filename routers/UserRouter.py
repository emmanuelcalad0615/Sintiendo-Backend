from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.UsersSchema import UserCreate, UserResponse, LoginRequest, TokenResponse
from services.UsersService import create_user, login_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user.username, user.email, user.password)

@router.post("/login", response_model=TokenResponse)
def login(user_data: LoginRequest, db: Session = Depends(get_db)):
    token, error = login_user(db, user_data.email, user_data.password)
    
    if error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error)
    
    return {"access_token": token, "token_type": "bearer"}