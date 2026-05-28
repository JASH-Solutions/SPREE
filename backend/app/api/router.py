from __future__ import annotations

from fastapi import APIRouter

from ..controllers import alerts_controller, interventions_controller, model_controller, reports_controller, risk_controller, students_controller

api_router = APIRouter(prefix="/api")

api_router.include_router(students_controller.router)
api_router.include_router(risk_controller.router)
api_router.include_router(alerts_controller.router)
api_router.include_router(interventions_controller.router)
api_router.include_router(model_controller.router)
api_router.include_router(reports_controller.router)
