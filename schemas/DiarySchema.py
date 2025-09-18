from pydantic import BaseModel, validator
from datetime import date, datetime
from typing import List, Optional
from schemas.MediaSchema import MediaResponse

class EmotionCreate(BaseModel):
    emotion_type: str
    intensity: int
    icon: Optional[str] = None
    notes: Optional[str] = None
    
    @validator('intensity')
    def validate_intensity(cls, v):
        if v < 1 or v > 5:
            raise ValueError('La intensidad debe estar entre 1 y 5')
        return v

class EmotionResponse(BaseModel):
    id: int
    diary_entry_id: int
    emotion_type: str
    intensity: int
    icon: Optional[str] = None
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True 

class DiaryEntryCreate(BaseModel):
    title: str
    content: str
    entry_date: date
    emotions: List[EmotionCreate] = []

class DiaryEntryResponse(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    entry_date: date
    created_at: datetime
    updated_at: datetime
    emotions: List[EmotionResponse] = []
    media_files: List[MediaResponse] = []  # Para incluir multimedia
    
    class Config:
        from_attributes = True 

class DiaryEntryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    entry_date: Optional[date] = None

class EmotionUpdate(BaseModel):
    emotion_type: Optional[str] = None
    intensity: Optional[int] = None
    icon: Optional[str] = None
    notes: Optional[str] = None
    
    @validator('intensity')
    def validate_intensity(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('La intensidad debe estar entre 1 y 5')
        return v
    

class EmotionSummaryResponse(BaseModel):
    emotion_type: str
    count: int
    average_intensity: float
    total_intensity: int
    icon: Optional[str] = None
    