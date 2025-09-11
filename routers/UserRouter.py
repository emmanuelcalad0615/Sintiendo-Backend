from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.UsersSchema import UserCreate, UserResponse, LoginRequest, TokenResponse
from services.UsersService import create_user, login_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/singup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    try:
        return create_user(db, user.username, user.email, user.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=TokenResponse)
def login(user_data: LoginRequest, db: Session = Depends(get_db)):
    data_response, error = login_user(db, user_data.email, user_data.password)
    
    if error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error)
    
    return {"access_token": data_response.access_token, "token_type": data_response.token_type, "username": data_response.username, "email": data_response.email}