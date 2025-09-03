from sqlalchemy import Column, Integer, String, Sequence
from database import Base
id_seq = Sequence('user_id_seq', schema='ECCGOAT')

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "ECCGOAT"}

    id = Column(Integer, id_seq,primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
