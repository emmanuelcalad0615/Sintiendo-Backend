from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.UsersSchema import UserCreate, UserResponse, LoginRequest, TokenResponse
from services.UsersService import create_user, login_user

router = APIRouter(prefix="/auth", tags=["auth"])


def http_error(code:int, message:str, detail:str=None):
    """
    Helper para enviar errores con un formato consistente
    """
    raise HTTPException(
        status_code=code,
        detail={
            "status": code,
            "message": message,
            "detail": detail or message
        }
    )


@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    try:
        return create_user(
            db=db,
            username=user.username,
            email=user.email,
            password=user.password,
            role=user.role
        )
    except ValueError as e:
        http_error(400, "Error de validación", str(e))
    except Exception as e:
        http_error(500, "Error interno del servidor", str(e))


@router.post("/login", response_model=TokenResponse)
def login(user_data: LoginRequest, db: Session = Depends(get_db)):
    try:
        data_response, error = login_user(db, user_data.email, user_data.password)
        
        if error:
            http_error(status.HTTP_401_UNAUTHORIZED, "Credenciales inválidas", error)

        return data_response

    except HTTPException:
        raise
    except Exception as e:
        http_error(500, "Error interno del servidor", str(e))
