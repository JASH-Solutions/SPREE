from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    id: Optional[str] = Field(default=None)
    student: Optional[Dict[str, Any]] = Field(default=None)


class StudentInferenceRequest(BaseModel):
    """Schema para inferencia de riesgo de nuevo estudiante"""
    promedio_academico: float = Field(..., ge=0, le=5, description="Promedio académico 0-5")
    materias_perdidas: int = Field(..., ge=0, description="Número de materias perdidas")
    asistencia_clases: float = Field(..., ge=0, le=100, description="Porcentaje de asistencia 0-100")
    rendimiento_periodo: float = Field(..., ge=0, le=100, description="Rendimiento del período 0-100")
    estado_pagos: str = Field(..., description="Estado de pagos: Al Día, Atraso, Embargo")
    mora_matricula: int = Field(..., ge=0, le=1, description="Mora en matrícula: 0 o 1")
    estrato: int = Field(..., ge=1, le=6, description="Estrato socioeconómico 1-6")
    ingresos_familiares: float = Field(..., ge=0, description="Ingresos familiares en COP")
    horas_trabajo_semanales: float = Field(..., ge=0, le=168, description="Horas de trabajo por semana")
    casos_riesgo: int = Field(..., ge=0, le=1, description="Casos de riesgo: 0 o 1")


class RiskResponse(BaseModel):
    riesgo_nivel: str
    riesgo_probabilidad: float


class RecommendationResponse(BaseModel):
    recomendacion: str
    riesgo_nivel: str
    riesgo_probabilidad: float
