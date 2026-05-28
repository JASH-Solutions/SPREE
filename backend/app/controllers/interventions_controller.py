"""
Controlador para gestionar intervenciones de estudiantes.
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import json
import os
from datetime import datetime
from uuid import uuid4

from ..schemas import InterventionRequest, InterventionResponse, InterventionListResponse

router = APIRouter(prefix="/interventions", tags=["Interventions"])

# Archivo para almacenar intervenciones
INTERVENTIONS_FILE = "data/interventions.json"


def _ensure_interventions_file():
    """Asegura que el archivo de intervenciones existe"""
    os.makedirs(os.path.dirname(INTERVENTIONS_FILE), exist_ok=True)
    if not os.path.exists(INTERVENTIONS_FILE):
        with open(INTERVENTIONS_FILE, "w") as f:
            json.dump({"interventions": []}, f)


def _load_interventions():
    """Carga intervenciones del archivo"""
    _ensure_interventions_file()
    try:
        with open(INTERVENTIONS_FILE, "r") as f:
            data = json.load(f)
            return data.get("interventions", [])
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def _save_interventions(interventions):
    """Guarda intervenciones al archivo"""
    _ensure_interventions_file()
    with open(INTERVENTIONS_FILE, "w") as f:
        json.dump({"interventions": interventions}, f, indent=2)


@router.post("/register", response_model=InterventionResponse)
async def register_intervention(payload: InterventionRequest):
    """
    Registrar una nueva intervención para un estudiante.
    
    Args:
        payload: Datos de la intervención
    
    Returns:
        InterventionResponse con ID y detalles de la intervención creada
    
    Raises:
        HTTPException: Si hay error al registrar
    """
    try:
        # Validar que el tipo sea válido
        tipos_validos = ["Académica", "Financiera", "Personal", "Emocional", "Familiar"]
        if payload.tipo not in tipos_validos:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de intervención inválido. Tipos válidos: {', '.join(tipos_validos)}"
            )
        
        # Validar estado
        estados_validos = ["Planeada", "En progreso", "Completada", "Cancelada"]
        if payload.estado not in estados_validos:
            raise HTTPException(
                status_code=400,
                detail=f"Estado inválido. Estados válidos: {', '.join(estados_validos)}"
            )
        
        # Crear intervención
        intervention_id = str(uuid4())
        fecha_creacion = datetime.now().isoformat()
        
        intervention = {
            "intervention_id": intervention_id,
            "student_id": payload.student_id,
            "tipo": payload.tipo,
            "descripcion": payload.descripcion,
            "responsable": payload.responsable,
            "resultado_esperado": payload.resultado_esperado,
            "estado": payload.estado,
            "notas_adicionales": payload.notas_adicionales,
            "fecha_creacion": fecha_creacion,
        }
        
        # Guardar intervención
        intervenciones = _load_interventions()
        intervenciones.append(intervention)
        _save_interventions(intervenciones)
        
        return {
            "intervention_id": intervention_id,
            "student_id": payload.student_id,
            "tipo": payload.tipo,
            "descripcion": payload.descripcion,
            "responsable": payload.responsable,
            "resultado_esperado": payload.resultado_esperado,
            "estado": payload.estado,
            "fecha_creacion": fecha_creacion,
            "mensaje": "Intervención registrada exitosamente",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al registrar intervención: {str(e)}") from e


@router.get("/student/{student_id}", response_model=InterventionListResponse)
async def get_student_interventions(student_id: str):
    """
    Obtener todas las intervenciones de un estudiante.
    
    Args:
        student_id: ID del estudiante
    
    Returns:
        Lista de intervenciones del estudiante
    """
    try:
        intervenciones = _load_interventions()
        student_interventions = [
            i for i in intervenciones if i.get("student_id") == student_id
        ]
        return {
            "total": len(student_interventions),
            "intervenciones": student_interventions,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener intervenciones: {str(e)}") from e


@router.get("/all", response_model=InterventionListResponse)
async def get_all_interventions():
    """
    Obtener todas las intervenciones registradas.
    
    Returns:
        Lista de todas las intervenciones
    """
    try:
        intervenciones = _load_interventions()
        return {
            "total": len(intervenciones),
            "intervenciones": intervenciones,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener intervenciones: {str(e)}") from e


@router.put("/{intervention_id}")
async def update_intervention(intervention_id: str, payload: InterventionRequest):
    """
    Actualizar estado o detalles de una intervención.
    
    Args:
        intervention_id: ID de la intervención
        payload: Nuevos datos
    
    Returns:
        Intervención actualizada
    """
    try:
        intervenciones = _load_interventions()
        
        intervention_index = None
        for idx, i in enumerate(intervenciones):
            if i.get("intervention_id") == intervention_id:
                intervention_index = idx
                break
        
        if intervention_index is None:
            raise HTTPException(status_code=404, detail="Intervención no encontrada")
        
        # Actualizar intervención
        intervenciones[intervention_index].update({
            "tipo": payload.tipo,
            "descripcion": payload.descripcion,
            "responsable": payload.responsable,
            "resultado_esperado": payload.resultado_esperado,
            "estado": payload.estado,
            "notas_adicionales": payload.notas_adicionales,
        })
        
        _save_interventions(intervenciones)
        
        return {
            "mensaje": "Intervención actualizada exitosamente",
            "intervención": intervenciones[intervention_index],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar intervención: {str(e)}") from e
