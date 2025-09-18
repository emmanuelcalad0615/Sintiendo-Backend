from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_
from models.diary import DiaryEntry, EmotionRecord
from models.media import MediaFile
from schemas.DiarySchema import DiaryEntryCreate, DiaryEntryUpdate, EmotionCreate
from datetime import date, datetime
from typing import List, Optional
from fastapi import HTTPException, status

class DiaryService:
    
    @staticmethod
    def create_diary_entry(db: Session, user_id: int, diary_data: DiaryEntryCreate) -> DiaryEntry:
        """Crear entrada de diario con emociones usando ORM"""
        # Verificar si ya existe una entrada para esta fecha
        existing_entry = db.query(DiaryEntry).filter(
            DiaryEntry.user_id == user_id,
            func.TRUNC(DiaryEntry.entry_date) == diary_data.entry_date
        ).first()
        
        if existing_entry:
            raise ValueError("Ya existe una entrada para esta fecha")
        
        # Crear la entrada del diario usando ORM
        diary_entry = DiaryEntry(
            user_id=user_id,
            title=diary_data.title,
            content=diary_data.content,
            entry_date=diary_data.entry_date
        )
        
        db.add(diary_entry)
        db.flush()  # Flush para obtener el ID sin commit
        
        # Crear registros de emociones usando ORM
        for emotion_data in diary_data.emotions:
            emotion = EmotionRecord(
                diary_entry_id=diary_entry.id,
                emotion_type=emotion_data.emotion_type,
                intensity=emotion_data.intensity,
                icon=emotion_data.icon,
                notes=emotion_data.notes
            )
            db.add(emotion)
        
        db.commit()
        db.refresh(diary_entry)
        return diary_entry

    @staticmethod
    def get_diary_entries(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[DiaryEntry]:
        """Obtener entradas de diario con relaciones usando ORM"""
        return db.query(DiaryEntry).filter(
            DiaryEntry.user_id == user_id
        ).options(
            joinedload(DiaryEntry.emotions),
            joinedload(DiaryEntry.media_files)
        ).order_by(
            DiaryEntry.entry_date.desc()
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_diary_entry_by_id(db: Session, user_id: int, entry_id: int) -> Optional[DiaryEntry]:
        """Obtener entrada específica con todas las relaciones usando ORM"""
        return db.query(DiaryEntry).filter(
            DiaryEntry.id == entry_id,
            DiaryEntry.user_id == user_id
        ).options(
            joinedload(DiaryEntry.emotions),
            joinedload(DiaryEntry.media_files),
            joinedload(DiaryEntry.user)
        ).first()

    @staticmethod
    def get_diary_entry_by_date(db: Session, user_id: int, entry_date: date) -> Optional[DiaryEntry]:
        """Obtener entrada por fecha con relaciones usando ORM"""
        return db.query(DiaryEntry).filter(
            DiaryEntry.user_id == user_id,
            func.TRUNC(DiaryEntry.entry_date) == entry_date
        ).options(
            joinedload(DiaryEntry.emotions),
            joinedload(DiaryEntry.media_files)
        ).first()

    @staticmethod
    def update_diary_entry(db: Session, user_id: int, entry_id: int, diary_data: DiaryEntryUpdate) -> Optional[DiaryEntry]:
        """Actualizar entrada de diario usando ORM"""
        diary_entry = DiaryService.get_diary_entry_by_id(db, user_id, entry_id)
        
        if not diary_entry:
            return None
        
        # Actualizar campos usando ORM
        if diary_data.title is not None:
            diary_entry.title = diary_data.title
        if diary_data.content is not None:
            diary_entry.content = diary_data.content
        if diary_data.entry_date is not None:
            diary_entry.entry_date = diary_data.entry_date
        
        diary_entry.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(diary_entry)
        return diary_entry

    @staticmethod
    def delete_diary_entry(db: Session, user_id: int, entry_id: int) -> bool:
        """Eliminar entrada de diario y sus relaciones usando ORM"""
        diary_entry = DiaryService.get_diary_entry_by_id(db, user_id, entry_id)
        
        if not diary_entry:
            return False
        
        # El ORM se encarga de eliminar las relaciones automáticamente
        # gracias a cascade="all, delete-orphan"
        db.delete(diary_entry)
        db.commit()
        return True

    @staticmethod
    def add_emotion_to_entry(db: Session, user_id: int, entry_id: int, emotion_data: EmotionCreate) -> EmotionRecord:
        """Añadir emoción a entrada existente usando ORM"""
        diary_entry = DiaryService.get_diary_entry_by_id(db, user_id, entry_id)
        
        if not diary_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entrada del diario no encontrada"
            )
        
        emotion = EmotionRecord(
            diary_entry_id=entry_id,
            emotion_type=emotion_data.emotion_type,
            intensity=emotion_data.intensity,
            icon=emotion_data.icon,
            notes=emotion_data.notes
        )
        
        db.add(emotion)
        db.commit()
        db.refresh(emotion)
        return emotion

    @staticmethod
    def update_emotion(db: Session, user_id: int, emotion_id: int, emotion_data: EmotionCreate) -> Optional[EmotionRecord]:
        """Actualizar emoción existente usando ORM"""
        emotion = db.query(EmotionRecord).join(DiaryEntry).filter(
            EmotionRecord.id == emotion_id,
            DiaryEntry.user_id == user_id
        ).first()
        
        if not emotion:
            return None
        
        emotion.emotion_type = emotion_data.emotion_type
        emotion.intensity = emotion_data.intensity
        emotion.icon = emotion_data.icon
        emotion.notes = emotion_data.notes
        
        db.commit()
        db.refresh(emotion)
        return emotion

    @staticmethod
    def delete_emotion(db: Session, user_id: int, emotion_id: int) -> bool:
        """Eliminar emoción usando ORM"""
        emotion = db.query(EmotionRecord).join(DiaryEntry).filter(
            EmotionRecord.id == emotion_id,
            DiaryEntry.user_id == user_id
        ).first()
        
        if not emotion:
            return False
        
        db.delete(emotion)
        db.commit()
        return True

    @staticmethod
    def get_emotion_summary(db: Session, user_id: int, start_date: date, end_date: date) -> dict:
        """Obtener resumen de emociones usando ORM con agregaciones"""
        from sqlalchemy import case
        
        # Consulta usando ORM con funciones de agregación
        emotion_stats = db.query(
            EmotionRecord.emotion_type,
            EmotionRecord.icon,
            func.count(EmotionRecord.id).label('count'),
            func.avg(EmotionRecord.intensity).label('average_intensity'),
            func.sum(EmotionRecord.intensity).label('total_intensity')
        ).join(DiaryEntry).filter(
            DiaryEntry.user_id == user_id,
            func.TRUNC(DiaryEntry.entry_date) >= start_date,
            func.TRUNC(DiaryEntry.entry_date) <= end_date
        ).group_by(
            EmotionRecord.emotion_type,
            EmotionRecord.icon
        ).all()
        
        # Convertir a diccionario
        summary = {}
        for stat in emotion_stats:
            summary[stat.emotion_type] = {
                "count": stat.count,
                "average_intensity": float(stat.average_intensity) if stat.average_intensity else 0,
                "total_intensity": stat.total_intensity,
                "icon": stat.icon
            }
        
        return summary

    @staticmethod
    def get_entries_with_emotions(db: Session, user_id: int, emotion_type: str = None) -> List[DiaryEntry]:
        """Obtener entradas filtradas por tipo de emoción usando ORM"""
        query = db.query(DiaryEntry).filter(
            DiaryEntry.user_id == user_id
        ).options(
            joinedload(DiaryEntry.emotions),
            joinedload(DiaryEntry.media_files)
        )
        
        if emotion_type:
            query = query.join(EmotionRecord).filter(
                EmotionRecord.emotion_type == emotion_type
            )
        
        return query.order_by(DiaryEntry.entry_date.desc()).all()

    @staticmethod
    def get_recent_emotions(db: Session, user_id: int, limit: int = 10) -> List[EmotionRecord]:
        """Obtener emociones recientes con información de la entrada usando ORM"""
        return db.query(EmotionRecord).join(DiaryEntry).filter(
            DiaryEntry.user_id == user_id
        ).options(
            joinedload(EmotionRecord.diary_entry)
        ).order_by(
            EmotionRecord.id.desc()
        ).limit(limit).all()