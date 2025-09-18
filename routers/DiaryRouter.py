from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.DiarySchema import (
    DiaryEntryCreate, DiaryEntryResponse, DiaryEntryUpdate,
    EmotionCreate, EmotionResponse, EmotionUpdate, EmotionSummaryResponse
)
from services.DiaryService import DiaryService
from services.UsersService import get_current_user
from models.user import User
from datetime import date
from typing import List, Dict

router = APIRouter(prefix="/diary", tags=["diary"])

@router.post("/entries", response_model=DiaryEntryResponse)
def create_entry(
    diary_data: DiaryEntryCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear nueva entrada de diario con emociones"""
    try:
        diary_entry = DiaryService.create_diary_entry(db, current_user.id, diary_data)
        return DiaryEntryResponse.from_orm(diary_entry)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/entries", response_model=List[DiaryEntryResponse])
def read_entries(
    skip: int = 0, 
    limit: int = 100, 
    emotion_type: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener entradas de diario, opcionalmente filtradas por emoción"""
    if emotion_type:
        entries = DiaryService.get_entries_with_emotions(db, current_user.id, emotion_type)
    else:
        entries = DiaryService.get_diary_entries(db, current_user.id, skip, limit)
    
    return [DiaryEntryResponse.from_orm(entry) for entry in entries]

@router.get("/entries/{entry_id}", response_model=DiaryEntryResponse)
def read_entry(
    entry_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener entrada específica del diario"""
    entry = DiaryService.get_diary_entry_by_id(db, current_user.id, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entrada no encontrada")
    return DiaryEntryResponse.from_orm(entry)

@router.get("/entries/date/{entry_date}", response_model=DiaryEntryResponse)
def read_entry_by_date(
    entry_date: date, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener entrada por fecha"""
    entry = DiaryService.get_diary_entry_by_date(db, current_user.id, entry_date)
    if not entry:
        raise HTTPException(status_code=404, detail="No hay entrada para esta fecha")
    return DiaryEntryResponse.from_orm(entry)

@router.put("/entries/{entry_id}", response_model=DiaryEntryResponse)
def update_entry(
    entry_id: int, 
    diary_data: DiaryEntryUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar entrada del diario"""
    entry = DiaryService.update_diary_entry(db, current_user.id, entry_id, diary_data)
    if not entry:
        raise HTTPException(status_code=404, detail="Entrada no encontrada")
    return DiaryEntryResponse.from_orm(entry)

@router.delete("/entries/{entry_id}")
def delete_entry(
    entry_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar entrada del diario"""
    success = DiaryService.delete_diary_entry(db, current_user.id, entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entrada no encontrada")
    return {"message": "Entrada eliminada correctamente"}

@router.post("/entries/{entry_id}/emotions", response_model=EmotionResponse)
def add_emotion(
    entry_id: int,
    emotion_data: EmotionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Añadir emoción a una entrada existente"""
    emotion = DiaryService.add_emotion_to_entry(db, current_user.id, entry_id, emotion_data)
    return EmotionResponse.from_orm(emotion)

@router.put("/emotions/{emotion_id}", response_model=EmotionResponse)
def update_emotion(
    emotion_id: int,
    emotion_data: EmotionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar emoción existente"""
    emotion = DiaryService.update_emotion(db, current_user.id, emotion_id, emotion_data)
    if not emotion:
        raise HTTPException(status_code=404, detail="Emoción no encontrada")
    return EmotionResponse.from_orm(emotion)

@router.delete("/emotions/{emotion_id}")
def delete_emotion(
    emotion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar emoción"""
    success = DiaryService.delete_emotion(db, current_user.id, emotion_id)
    if not success:
        raise HTTPException(status_code=404, detail="Emoción no encontrada")
    return {"message": "Emoción eliminada correctamente"}

@router.get("/emotion-summary", response_model=Dict[str, EmotionSummaryResponse])
def get_emotions_summary(
    start_date: date, 
    end_date: date, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener resumen estadístico de emociones"""
    summary = DiaryService.get_emotion_summary(db, current_user.id, start_date, end_date)
    return summary

@router.get("/recent-emotions", response_model=List[EmotionResponse])
def get_recent_emotions(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener emociones recientes"""
    emotions = DiaryService.get_recent_emotions(db, current_user.id, limit)
    return [EmotionResponse.from_orm(emotion) for emotion in emotions]