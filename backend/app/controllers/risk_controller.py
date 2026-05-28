from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import get_student_service
from ..schemas import PredictRequest, RecommendationResponse, RiskResponse, StudentInferenceRequest
from ..services.student_service import StudentService

router = APIRouter(tags=["risk"])


@router.post("/predict-risk", response_model=RiskResponse)
def predict_risk(
    payload: PredictRequest,
    service: StudentService = Depends(get_student_service),
) -> Dict[str, Any]:
    try:
        prediction = service.predict_risk(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "riesgo_nivel": prediction.level,
        "riesgo_probabilidad": round(prediction.probability, 4),
    }


@router.post("/infer-risk", response_model=RiskResponse)
def infer_risk(
    payload: StudentInferenceRequest,
    service: StudentService = Depends(get_student_service),
) -> Dict[str, Any]:
    """
    Realizar inferencia de riesgo para un estudiante nuevo.
    
    Este endpoint acepta los datos completos de un estudiante en formato
    validado y retorna una predicción de riesgo de deserción.
    
    Args:
        payload: Datos del estudiante con todas las características requeridas
        service: Servicio de estudiantes (inyectado)
    
    Returns:
        Predicción de riesgo con nivel (Alto/Medio/Bajo) y probabilidad
    
    Raises:
        HTTPException: Si hay error en la predicción (400)
    """
    try:
        # Convertir payload a diccionario para compatibilidad con el servicio existente
        student_data = payload.model_dump()
        prediction = service.predict_risk({"student": student_data})
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error en la predicción: {str(exc)}") from exc
    
    return {
        "riesgo_nivel": prediction.level,
        "riesgo_probabilidad": round(prediction.probability, 4),
    }


@router.post("/recommendation", response_model=RecommendationResponse)
def recommendation(
    payload: PredictRequest,
    service: StudentService = Depends(get_student_service),
) -> Dict[str, Any]:
    try:
        return service.get_recommendation(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
