from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class StudentSummary(BaseModel):
    id_estudiante: str
    nombre: str
    programa_academico: Optional[str] = None
    promedio_academico: Optional[float] = None
    materias_perdidas: Optional[float] = None
    asistencia_clases: Optional[float] = None
    estado_pagos: Optional[str] = None
    mora_matricula: Optional[float] = None
    riesgo_nivel: str
    riesgo_probabilidad: float


class StudentListResponse(BaseModel):
    page: int
    size: int
    total: int
    items: List[StudentSummary]


class StudentDetailResponse(BaseModel):
    data: Dict[str, Any]
    riesgo_nivel: str
    riesgo_probabilidad: float
    recomendacion: str
