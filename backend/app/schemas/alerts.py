from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class AlertItem(BaseModel):
    id_estudiante: str
    nombre: str
    programa_academico: Optional[str] = None
    riesgo_nivel: str
    riesgo_probabilidad: float
    recomendacion: str


class AlertsResponse(BaseModel):
    items: List[AlertItem]
