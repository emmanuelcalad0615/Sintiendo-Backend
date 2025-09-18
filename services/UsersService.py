from sqlalchemy.orm import Session
from models.user import User
from services.utils import hash_password, verify_password, create_access_token
from schemas.UsersSchema import TokenResponse
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from database import get_db
from config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def create_user(db: Session, username: str, email: str, password: str):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise ValueError("El usuario ya existe")
    hashed_pw = hash_password(password)
    new_user = User(username=username, email=email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def login_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None, "Usuario no encontrado"
    
    if not verify_password(password, user.hashed_password):
        return None, "Contraseña incorrecta"

    token = create_access_token({"sub": user.email})
    data_response = TokenResponse(access_token=token, token_type="bearer", username=user.username, email=user.email)
    
    return data_response, None

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user
