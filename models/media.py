from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Sequence
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

# Secuencias para Oracle
media_id_seq = Sequence('media_id_seq', schema='SINTIENDO')

class MediaFile(Base):
    __tablename__ = "media_files"
    __table_args__ = {"schema": "SINTIENDO"}
    
    id = Column(Integer, media_id_seq, primary_key=True, server_default=media_id_seq.next_value())
    diary_entry_id = Column(Integer, ForeignKey('SINTIENDO.diary_entries.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('SINTIENDO.users.id'), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones usando ORM
    diary_entry = relationship("DiaryEntry", back_populates="media_files")
    user = relationship("User")

    @property
    def download_url(self):
        """Método de instancia para obtener URL de descarga"""
        return f"/media/{self.id}/download"
    
    def to_dict(self):
        """Convertir objeto a diccionario para respuesta"""
        return {
            "id": self.id,
            "diary_entry_id": self.diary_entry_id,
            "user_id": self.user_id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_type": self.file_type,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "description": self.description,
            "created_at": self.created_at,
            "download_url": self.get_download_url()
        }