from sqlalchemy import Column, Integer, String, Sequence, Enum
from database import Base
import enum

class RoleEnum(enum.Enum):
    NINO_ADOLESCENTE = "nino_adolescente"
    ADULTO = "adulto"

id_seq = Sequence('user_id_seq', schema='SINTIENDO', start=1, increment=1)

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "SINTIENDO"}

    id = Column(Integer, id_seq, primary_key=True, index=False)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
