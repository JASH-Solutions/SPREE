from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    id: Optional[str] = Field(default=None)
    student: Optional[Dict[str, Any]] = Field(default=None)


class RiskResponse(BaseModel):
    riesgo_nivel: str
    riesgo_probabilidad: float


class RecommendationResponse(BaseModel):
    recomendacion: str
    riesgo_nivel: str
    riesgo_probabilidad: float
