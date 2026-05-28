from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends

from ..dependencies import get_student_service
from ..schemas import AlertsResponse
from ..services.student_service import StudentService

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=AlertsResponse)
def alerts(
    service: StudentService = Depends(get_student_service),
) -> Dict[str, Any]:
    return {"items": service.get_alerts()}
