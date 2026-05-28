from __future__ import annotations

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import CORS_ORIGINS, DATA_PATH
from app.ml.risk_model import RiskModel
from app.repositories.student_repository import StudentRepository
from app.services.recommendation_service import RecommendationService
from app.services.student_service import StudentService


def create_app() -> FastAPI:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
    )
    logger = logging.getLogger("spree.backend")

    app = FastAPI(title="SPREE Backend", version="0.2.0")

    if not DATA_PATH.exists():
        raise RuntimeError(
            f"Dataset not found at {DATA_PATH}. Set SPREE_DATA_PATH to override."
        )

    logger.info("Loading dataset from %s", DATA_PATH)
    repository = StudentRepository(str(DATA_PATH))
    risk_model = RiskModel(repository.data)
    recommendation_service = RecommendationService()
    student_service = StudentService(repository, risk_model, recommendation_service)
    app.state.student_service = student_service
    logger.info("Backend ready. Students loaded: %s", len(repository.data))

    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        logger.info("Request %s %s", request.method, request.url.path)
        response = await call_next(request)
        logger.info("Response %s %s", response.status_code, request.url.path)
        return response

    return app


app = create_app()
