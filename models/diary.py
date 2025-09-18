from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, DateTime, Sequence
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

# Secuencias para Oracle
diary_id_seq = Sequence('diary_id_seq', schema='SINTIENDO')
emotion_id_seq = Sequence('emotion_id_seq', schema='SINTIENDO')

class DiaryEntry(Base):
    __tablename__ = "diary_entries"
    __table_args__ = {"schema": "SINTIENDO"}
    
    id = Column(Integer, diary_id_seq, primary_key=True, server_default=diary_id_seq.next_value())
    user_id = Column(Integer, ForeignKey('SINTIENDO.users.id'), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    entry_date = Column(Date, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones usando ORM
    emotions = relationship("EmotionRecord", back_populates="diary_entry", cascade="all, delete-orphan")
    media_files = relationship("MediaFile", back_populates="diary_entry", cascade="all, delete-orphan")
    user = relationship("User")
    
    def to_dict(self):
        """Convertir objeto a diccionario con relaciones"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "content": self.content,
            "entry_date": self.entry_date,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "emotions": [emotion.to_dict() for emotion in self.emotions],
            "media_files": [media.to_dict() for media in self.media_files]
        }

class EmotionRecord(Base):
    __tablename__ = "emotion_records"
    __table_args__ = {"schema": "SINTIENDO"}
    
    id = Column(Integer, emotion_id_seq, primary_key=True, server_default=emotion_id_seq.next_value())
    diary_entry_id = Column(Integer, ForeignKey('SINTIENDO.diary_entries.id'), nullable=False)
    emotion_type = Column(String(50), nullable=False)
    intensity = Column(Integer, nullable=False)
    icon = Column(String(100))
    notes = Column(Text)
    
    # Relación usando ORM
    diary_entry = relationship("DiaryEntry", back_populates="emotions")
    
    def to_dict(self):
        """Convertir objeto a diccionario"""
        return {
            "id": self.id,
            "diary_entry_id": self.diary_entry_id,
            "emotion_type": self.emotion_type,
            "intensity": self.intensity,
            "icon": self.icon,
            "notes": self.notes
        }