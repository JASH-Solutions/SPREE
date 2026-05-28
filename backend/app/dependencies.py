from __future__ import annotations

from fastapi import Request

from .services.student_service import StudentService


def get_student_service(request: Request) -> StudentService:
    return request.app.state.student_service
