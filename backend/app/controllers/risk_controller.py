from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import get_student_service
from ..schemas import PredictRequest, RecommendationResponse, RiskResponse
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


@router.post("/recommendation", response_model=RecommendationResponse)
def recommendation(
    payload: PredictRequest,
    service: StudentService = Depends(get_student_service),
) -> Dict[str, Any]:
    try:
        return service.get_recommendation(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
