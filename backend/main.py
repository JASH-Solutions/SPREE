from __future__ import annotations

import logging
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import CORS_ORIGINS, DATA_PATH
from app.ml.model_persister import ModelPersister
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
    
    # Cargar o entrenar modelo (con persistencia)
    logger.info("Initializing model persister...")
    persister = ModelPersister()
    
    start_time = time.time()
    pipeline = persister.load_or_train(
        repository.data,
        description="Production model - clean features (without leakage)"
    )
    load_time = time.time() - start_time
    
    # Crear wrapper para compatibilidad con RiskModel
    class PersistentRiskModel:
        def __init__(self, pipeline, persister):
            self.pipeline = pipeline
            self.persister = persister
            self.feature_columns = [
                "promedio_academico",
                "asistencia_clases",
                "horas_trabajo_semanales",
                "ingresos_familiares",
                "estrato",
                "rendimiento_periodo",
            ]
        
        def predict_proba(self, df):
            """Predecir probabilidades."""
            import numpy as np
            try:
                x = df[self.feature_columns].copy()
                return self.pipeline.predict_proba(x)[:, 1].tolist()
            except Exception as e:
                logger.error(f"Error in predict_proba: {e}")
                return [0.0] * len(df)
        
        def predict_proba_row(self, row):
            """Predecir probabilidad de una fila."""
            import pandas as pd
            df = pd.DataFrame([row])
            return self.predict_proba(df)[0]
        
        @staticmethod
        def risk_level(probability):
            """Clasificar nivel de riesgo."""
            if probability >= 0.66:
                return "Alto"
            if probability >= 0.33:
                return "Medio"
            return "Bajo"
        
        def predict(self, row):
            """Predecir riesgo de una fila."""
            from app.ml.risk_model import RiskPrediction
            probability = float(self.predict_proba_row(row))
            return RiskPrediction(level=self.risk_level(probability), probability=probability)
    
    risk_model = PersistentRiskModel(pipeline, persister)
    
    recommendation_service = RecommendationService()
    student_service = StudentService(repository, risk_model, recommendation_service)
    
    # Guardar en state para acceso desde endpoints
    app.state.student_service = student_service
    app.state.model_persister = persister
    app.state.risk_model = risk_model
    
    logger.info(f"Backend ready. Students loaded: {len(repository.data)}")
    logger.info(f"Model loaded in {load_time:.2f}s")
    
    # Info del modelo
    model_info = persister.get_model_info()
    if model_info:
        logger.info(f"Model version: {model_info['version']}")
        logger.info(f"Model F1-Score: {model_info['metrics']['f1_score']:.4f}")

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
