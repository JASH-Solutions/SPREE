from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime

from pydantic import BaseModel, Field


class InterventionRequest(BaseModel):
    """Schema para crear/registrar una intervención"""
    student_id: str = Field(..., description="ID del estudiante")
    tipo: str = Field(..., description="Tipo: Académica, Financiera, Personal, Emocional, Familiar")
    descripcion: str = Field(..., description="Descripción detallada de la intervención")
    responsable: str = Field(..., description="Persona responsable de la intervención")
    resultado_esperado: str = Field(..., description="Resultado esperado de la intervención")
    estado: str = Field(default="Planeada", description="Planeada, En progreso, Completada, Cancelada")
    notas_adicionales: Optional[str] = Field(default=None, description="Notas adicionales")


class InterventionResponse(BaseModel):
    """Respuesta de intervención creada"""
    intervention_id: str
    student_id: str
    tipo: str
    descripcion: str
    responsable: str
    resultado_esperado: str
    estado: str
    fecha_creacion: str
    mensaje: str


class InterventionListResponse(BaseModel):
    """Respuesta con lista de intervenciones"""
    total: int
    intervenciones: List[Dict[str, Any]]
