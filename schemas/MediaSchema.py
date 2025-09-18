from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class MediaCreate(BaseModel):
    diary_entry_id: int
    description: Optional[str] = None

class MediaResponse(BaseModel):
    id: int
    diary_entry_id: int
    user_id: int
    filename: str
    original_filename: str
    file_type: str
    file_path: str
    file_size: Optional[int]
    description: Optional[str]
    created_at: datetime
    download_url: str  # URL para descargar el archivo
    
    class Config:
        from_attributes = True 

class DrawingData(BaseModel):
    diary_entry_id: int
    drawing_data: str  # Base64 encoded image data
    description: Optional[str] = None