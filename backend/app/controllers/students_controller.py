from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import get_student_service
from ..schemas import StudentDetailResponse, StudentListResponse
from ..services.student_service import StudentService

router = APIRouter(prefix="/students", tags=["students"])


@router.get("", response_model=StudentListResponse)
def list_students(
    page: int = 1,
    size: int = 25,
    service: StudentService = Depends(get_student_service),
) -> Dict[str, Any]:
    return service.list_students(page=page, size=size)


@router.get("/{student_id}", response_model=StudentDetailResponse)
def get_student_detail(
    student_id: str,
    service: StudentService = Depends(get_student_service),
) -> Dict[str, Any]:
    result = service.get_student_detail(student_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return result
