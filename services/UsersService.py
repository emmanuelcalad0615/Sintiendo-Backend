from sqlalchemy.orm import Session
from models.user import User
from services.utils import hash_password, verify_password, create_access_token

def create_user(db: Session, username: str, email: str, password: str):
    hashed_pw = hash_password(password)
    new_user = User(username=username, email=email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def login_user(db: Session, email: str, password: str):
    # Buscar usuario por email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None, "Usuario no encontrado"
    
    # Verificar contraseña
    if not verify_password(password, user.hashed_password):
        return None, "Contraseña incorrecta"
    
    # Crear token
    token = create_access_token({"sub": user.email})
    return token, None
