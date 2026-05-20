from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated, List, Optional, Literal, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from models.tarea import TareaEntrada, TareaActualizacion, TareaSalida
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="API de Tareas")

# Autenticación básica HTTP (usuario y contraseña)
security = HTTPBasic()

# Lista simulando base de datos en memoria
db_tareas = []
_next_id = 1  # Autoincremental para ID de tareas


# Verifica usuario y contraseña del .env
def get_current_user(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    correct_username = os.getenv("USERNAME")
    correct_password = os.getenv("PASSWORD")
    if credentials.username != correct_username or credentials.password != correct_password:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return credentials.username


# Busca tarea por ID, si no existe lanza 404
def tarea_en_db(id: int) -> TareaSalida:
    for t in db_tareas:
        if t.id == id:
            return t
    raise HTTPException(status_code=404, detail="Tarea no encontrada")


# GET /tareas → lista tareas con filtros y paginación
@app.get("/tareas", response_model=List[TareaSalida])
def listar_tareas(
    completada: Optional[bool] = None,
    prioridad: Optional[Literal["baja", "media", "alta"]] = None,
    ordenar: Optional[Literal["prioridad", "creada_en"]] = None,
    dir: Literal["asc", "desc"] = "asc",
    limite: int = 10,
    pagina: int = 1,
    current_user: Annotated[Optional[str], Depends(get_current_user)] = None,
):
    tareas = db_tareas

    # Filtrar por completada si viene
    if completada is not None:
        tareas = [t for t in tareas if t.completada == completada]

    # Filtrar por prioridad si viene
    if prioridad is not None:
        tareas = [t for t in tareas if t.prioridad == prioridad]

    # Ordenar por prioridad o fecha de creación
    if ordenar:
        reverse = dir == "desc"
        if ordenar == "prioridad":
            tareas = sorted(tareas, key=lambda t: t.prioridad, reverse=reverse)
        elif ordenar == "creada_en":
            tareas = sorted(tareas, key=lambda t: t.creada_en, reverse=reverse)

    # Paginación: start = inicio, end = fin del slice
    start = (pagina - 1) * limite
    end = start + limite
    return tareas[start:end]


# GET /tareas/{id} → devolver una tarea concreta
@app.get("/tareas/{id}", response_model=TareaSalida)
def obtener_tarea(
    id: int,
    current_user: Annotated[Optional[str], Depends(get_current_user)] = None,
):
    return tarea_en_db(id)


# POST /tareas → crear nueva tarea
@app.post("/tareas", response_model=TareaSalida)
def crear_tarea(
    entrada: TareaEntrada,
    current_user: Annotated[Optional[str], Depends(get_current_user)] = None,
):
    global _next_id
    tarea = TareaSalida(
        id=_next_id,
        titulo=entrada.titulo,
        descripcion=entrada.descripcion,
        prioridad=entrada.prioridad,
        fecha_limite=entrada.fecha_limite,
        completada=False,
        creada_en=datetime.utcnow(),
        completada_en=None,
    )
    db_tareas.append(tarea)
    _next_id += 1
    return tarea


# PATCH /tareas/{id} → actualizar solo campos enviados
@app.patch("/tareas/{id}", response_model=TareaSalida)
def actualizar_tarea(
    id: int,
    patch: TareaActualizacion,
    current_user: Annotated[Optional[str], Depends(get_current_user)] = None,
):
    tarea = tarea_en_db(id)
    update_data = patch.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(tarea, key, value)
    return tarea


# DELETE /tareas/{id} → borrar una tarea
@app.delete("/tareas/{id}")
def borrar_tarea(
    id: int,
    current_user: Annotated[Optional[str], Depends(get_current_user)] = None,
):
    tarea = tarea_en_db(id)
    db_tareas.remove(tarea)
    return {"mensaje": "Tarea eliminada"}


# POST /tareas/{id}/completar → marcar como completada
@app.post("/tareas/{id}/completar", response_model=TareaSalida)
def completar_tarea(
    id: int,
    current_user: Annotated[Optional[str], Depends(get_current_user)] = None,
):
    tarea = tarea_en_db(id)
    if tarea.completada:
        raise HTTPException(status_code=400, detail="La tarea ya está completada")
    tarea.completada = True
    tarea.completada_en = datetime.utcnow()
    return tarea


# Modelo para crear varias tareas a la vez (lote)
class TareaEntradaLote(BaseModel):
    tareas: List[TareaEntrada]


# POST /tareas/lote → crear múltiples tareas de una vez
@app.post("/tareas/lote", response_model=Dict[str, List[TareaSalida]]])
def crear_tareas_lote(
    lote: TareaEntradaLote,
    current_user: Annotated[Optional[str], Depends(get_current_user)] = None,
):
    global _next_id
    creadas = []
    for entrada in lote.tareas:
        tarea = TareaSalida(
            id=_next_id,
            titulo=entrada.titulo,
            descripcion=entrada.descripcion,
            prioridad=entrada.prioridad,
            fecha_limite=entrada.fecha_limite,
            completada=False,
            creada_en=datetime.utcnow(),
            completada_en=None,
        )
        db_tareas.append(tarea)
        creadas.append(tarea)
        _next_id += 1
    return {"tareas_creadas": creadas}


# GET /tareas/estadisticas → estadísticas generales
@app.get("/tareas/estadisticas")
def estadisticas_tareas(
    current_user: Annotated[Optional[str], Depends(get_current_user)] = None,
) -> Dict[str, Any]:
    total = len(db_tareas)
    completadas = len([t for t in db_tareas if t.completada])
    pendientes = total - completadas

    # Pendientes por prioridad
    pendientes_por_prioridad = {}
    for p in ["baja", "media", "alta"]:
        pendientes_por_prioridad[p] = len(
            [t for t in db_tareas if not t.completada and t.prioridad == p]
        )

    return {
        "total": total,
        "completadas": completadas,
        "pendientes": pendientes,
        "pendientes_por_prioridad": pendientes_por_prioridad,
    }


# Arrancar el servidor si ejecutamos python main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)