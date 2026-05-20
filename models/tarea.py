from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class TareaEntrada(BaseModel):
    titulo: str = Field(min_length=1, max_length=100)
    descripcion: Optional[str] = None
    prioridad: Literal["baja", "media", "alta"] = "media"
    fecha_limite: Optional[datetime] = None

class TareaActualizacion(BaseModel):
    titulo: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = None
    prioridad: Optional[Literal["baja", "media", "alta"]] = None
    completada: Optional[bool] = None
    fecha_limite: Optional[datetime] = None

class TareaSalida(BaseModel):
    id: int
    titulo: str
    descripcion: Optional[str]
    prioridad: str
    completada: bool
    creada_en: datetime
    completada_en: Optional[datetime]
    fecha_limite: Optional[datetime]