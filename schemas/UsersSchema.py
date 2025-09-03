from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr  
    password: str

# Para devolver datos al cliente (sin contraseña)
class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True  # Esto permite devolver objetos SQLAlchemy directamente
