import os
import uuid
import base64
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from models.media import MediaFile
from models.diary import DiaryEntry
from fastapi import UploadFile, HTTPException, status
from datetime import datetime
from typing import List
import aiofiles
from config import settings

# Configuración de directorios
UPLOAD_DIR = "uploads"
AUDIO_DIR = os.path.join(UPLOAD_DIR, "audio")
DRAWING_DIR = os.path.join(UPLOAD_DIR, "drawings")
IMAGES_DIR = os.path.join(UPLOAD_DIR, "images")

# Crear directorios si no existen
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(DRAWING_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

class MediaService:
    
    @staticmethod
    async def save_uploaded_file(file: UploadFile, file_type: str, user_id: int) -> dict:
        """Guardar archivo subido usando ORM"""
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        if file_type == 'audio':
            save_dir = AUDIO_DIR
        elif file_type == 'drawing':
            save_dir = DRAWING_DIR
        else:
            save_dir = IMAGES_DIR
        
        file_path = os.path.join(save_dir, unique_filename)
        
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        return {
            'filename': unique_filename,
            'original_filename': file.filename,
            'file_path': file_path,
            'file_size': len(content)
        }

    @staticmethod
    async def save_drawing(drawing_data: str, file_type: str, user_id: int) -> dict:
        """Guardar dibujo desde base64 usando ORM"""
        unique_filename = f"{uuid.uuid4()}.png"
        save_dir = DRAWING_DIR
        file_path = os.path.join(save_dir, unique_filename)
        
        try:
            if ',' in drawing_data:
                drawing_data = drawing_data.split(',')[1]
            
            image_data = base64.b64decode(drawing_data)
            async with aiofiles.open(file_path, 'wb') as out_file:
                await out_file.write(image_data)
            
            return {
                'filename': unique_filename,
                'original_filename': f"drawing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                'file_path': file_path,
                'file_size': len(image_data)
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al procesar el dibujo: {str(e)}"
            )

    @staticmethod
    def create_media_record(db: Session, user_id: int, diary_entry_id: int, 
                           file_info: dict, file_type: str, description: str = None) -> MediaFile:
        """Crear registro multimedia usando ORM"""
        # Verificar relación usando ORM
        diary_entry = db.query(DiaryEntry).filter(
            DiaryEntry.id == diary_entry_id,
            DiaryEntry.user_id == user_id
        ).first()
        
        if not diary_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entrada del diario no encontrada"
            )
        
        # Crear objeto MediaFile usando ORM
        media_file = MediaFile(
            diary_entry_id=diary_entry_id,
            user_id=user_id,
            filename=file_info['filename'],
            original_filename=file_info['original_filename'],
            file_type=file_type,
            file_path=file_info['file_path'],
            file_size=file_info['file_size'],
            description=description
        )
        
        db.add(media_file)
        db.commit()
        db.refresh(media_file)
        return media_file

    @staticmethod
    def get_media_files_by_entry(db: Session, user_id: int, diary_entry_id: int) -> List[MediaFile]:
        """Obtener archivos multimedia usando ORM con relaciones"""
        return db.query(MediaFile).filter(
            MediaFile.diary_entry_id == diary_entry_id,
            MediaFile.user_id == user_id
        ).options(joinedload(MediaFile.diary_entry)).all()

    @staticmethod
    def get_media_file(db: Session, user_id: int, media_id: int) -> MediaFile:
        """Obtener archivo multimedia específico usando ORM"""
        media_file = db.query(MediaFile).filter(
            MediaFile.id == media_id,
            MediaFile.user_id == user_id
        ).options(joinedload(MediaFile.diary_entry), joinedload(MediaFile.user)).first()
        
        if not media_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Archivo multimedia no encontrado"
            )
        
        return media_file

    @staticmethod
    def delete_media_file(db: Session, user_id: int, media_id: int) -> bool:
        """Eliminar archivo multimedia usando ORM"""
        media_file = MediaService.get_media_file(db, user_id, media_id)
        
        # Eliminar archivo físico
        if os.path.exists(media_file.file_path):
            os.remove(media_file.file_path)
        
        # Eliminar usando ORM
        db.delete(media_file)
        db.commit()
        
        return True

    @staticmethod
    def get_media_with_relations(db: Session, media_id: int, user_id: int):
        """Obtener multimedia con todas sus relaciones usando ORM"""
        return db.query(MediaFile).filter(
            MediaFile.id == media_id,
            MediaFile.user_id == user_id
        ).options(
            joinedload(MediaFile.diary_entry),
            joinedload(MediaFile.user)
        ).first()