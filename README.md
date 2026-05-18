![logo_ironhack_blue 7](https://user-images.githubusercontent.com/23629340/40541063-a07a0a8a-601a-11e8-91b5-2f13e4e6b441.png)

# Lab | API de tareas con FastAPI y Pydantic

## Objetivo

Construir una API REST completa para gestionar un sistema de tareas (to-do), con autenticación básica, usando FastAPI y Pydantic.

## Setup

```bash
mkdir lab-fastapi-tareas
cd lab-fastapi-tareas
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install fastapi uvicorn python-dotenv pydantic[email]
pip freeze > requirements.txt
```

## Modelos a implementar

```python
# models/tarea.py
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
```

## Endpoints requeridos

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/tareas` | Listar todas (filtrar por `?completada=true/false&prioridad=alta`) |
| GET | `/tareas/{id}` | Obtener una tarea |
| POST | `/tareas` | Crear tarea |
| PATCH | `/tareas/{id}` | Actualizar campos concretos |
| DELETE | `/tareas/{id}` | Eliminar |
| POST | `/tareas/{id}/completar` | Marcar como completada (registrar timestamp) |
| GET | `/tareas/estadisticas` | Resumen: total, completadas, pendientes por prioridad |

## Bonus

- Añade ordenación: `?ordenar=prioridad&dir=desc`
- Añade paginación: `?limite=10&pagina=2`
- Implementa `POST /tareas/lote` para crear varias tareas a la vez