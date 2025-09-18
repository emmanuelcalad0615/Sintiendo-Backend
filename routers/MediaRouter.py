from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from database import get_db
from schemas.MediaSchema import MediaResponse, DrawingData
from services.MediaService import MediaService
from services.UsersService import get_current_user
from models.user import User
from typing import List, Optional

router = APIRouter(prefix="/media", tags=["media"])

@router.post("/upload/audio", response_model=MediaResponse)
async def upload_audio(
    diary_entry_id: int = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Subir archivo de audio usando ORM"""
    if not file.content_type.startswith('audio/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser de audio"
        )
    
    file_info = await MediaService.save_uploaded_file(file, 'audio', current_user.id)
    media_file = MediaService.create_media_record(db, current_user.id, diary_entry_id, file_info, 'audio', description)
    
    return MediaResponse(**media_file.to_dict())

@router.post("/upload/drawing", response_model=MediaResponse)
async def upload_drawing(
    drawing_data: DrawingData,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Guardar dibujo usando ORM"""
    file_info = await MediaService.save_drawing(drawing_data.drawing_data, 'drawing', current_user.id)
    media_file = MediaService.create_media_record(
        db, current_user.id, drawing_data.diary_entry_id, 
        file_info, 'drawing', drawing_data.description
    )
    
    return MediaResponse(**media_file.to_dict())

@router.get("/entry/{diary_entry_id}", response_model=List[MediaResponse])
def get_entry_media(
    diary_entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener multimedia de entrada usando ORM"""
    media_files = MediaService.get_media_files_by_entry(db, current_user.id, diary_entry_id)
    return [MediaResponse(**media.to_dict()) for media in media_files]

@router.get("/{media_id}")
def get_media_info(
    media_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener información de archivo multimedia usando ORM"""
    media_file = MediaService.get_media_with_relations(db, media_id, current_user.id)
    if not media_file:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    return MediaResponse(**media_file.to_dict())