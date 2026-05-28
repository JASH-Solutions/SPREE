from __future__ import annotations

from typing import Any, Dict, List
import math

from ..ml.risk_model import RiskModel, RiskPrediction
from ..repositories.student_repository import StudentRepository
from .recommendation_service import RecommendationService


class StudentService:
    def __init__(
        self,
        repository: StudentRepository,
        risk_model: RiskModel,
        recommendation_service: RecommendationService,
    ) -> None:
        self.repository = repository
        self.risk_model = risk_model
        self.recommendation_service = recommendation_service

    def list_students(self, page: int, size: int) -> Dict[str, Any]:
        page = max(page, 1)
        size = max(min(size, 500), 1)
        df_page, total = self.repository.get_students_page(page, size)
        risk_probs = self.risk_model.predict_proba(df_page)
        items: List[Dict[str, Any]] = []
        for row, prob in zip(df_page.to_dict(orient="records"), risk_probs):
            risk_level = self.risk_model.risk_level(prob)
            items.append(
                {
                    "id_estudiante": row.get("id_estudiante"),
                    "nombre": self._build_name(row),
                    "programa_academico": row.get("programa_academico"),
                    "promedio_academico": row.get("promedio_academico"),
                    "materias_perdidas": row.get("materias_perdidas"),
                    "asistencia_clases": row.get("asistencia_clases"),
                    "estado_pagos": row.get("estado_pagos"),
                    "mora_matricula": row.get("mora_matricula"),
                    "riesgo_nivel": risk_level,
                    "riesgo_probabilidad": round(float(prob), 4),
                }
            )
        return {"page": page, "size": size, "total": total, "items": items}

    def get_student_detail(self, student_id: str) -> Dict[str, Any] | None:
        row = self.repository.get_student_by_id(student_id)
        if row is None:
            return None
        prediction = self.risk_model.predict(row)
        recommendation = self.recommendation_service.recommend(row, prediction.level)
        return {
            "data": row,
            "riesgo_nivel": prediction.level,
            "riesgo_probabilidad": round(prediction.probability, 4),
            "recomendacion": recommendation,
        }

    def predict_risk(self, payload: Dict[str, Any]) -> RiskPrediction:
        if payload.get("id"):
            row = self.repository.get_student_by_id(payload["id"])
            if row is None:
                raise ValueError("Student not found")
            return self.risk_model.predict(row)
        if payload.get("student"):
            raw_row = payload["student"]
            row = self.repository.merge_with_defaults(raw_row)
            return self.risk_model.predict(row)
        raise ValueError("Missing id or student data")

    def get_recommendation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        prediction = self.predict_risk(payload)
        if payload.get("id"):
            row = self.repository.get_student_by_id(payload["id"])
            if row is None:
                raise ValueError("Student not found")
        else:
            row = self.repository.merge_with_defaults(payload.get("student", {}))
        recommendation = self.recommendation_service.recommend(row, prediction.level)
        return {
            "recomendacion": recommendation,
            "riesgo_nivel": prediction.level,
            "riesgo_probabilidad": round(prediction.probability, 4),
        }

    def get_alerts(self, threshold: float = 0.7) -> List[Dict[str, Any]]:
        df = self.repository.data
        probs = self.risk_model.predict_proba(df)
        alerts: List[Dict[str, Any]] = []
        for row, prob in zip(df.to_dict(orient="records"), probs):
            if prob >= threshold:
                level = self.risk_model.risk_level(prob)
                recommendation = self.recommendation_service.recommend(row, level)
                alerts.append(
                    {
                        "id_estudiante": row.get("id_estudiante"),
                        "nombre": self._build_name(row),
                        "programa_academico": row.get("programa_academico"),
                        "riesgo_nivel": level,
                        "riesgo_probabilidad": round(float(prob), 4),
                        "recomendacion": recommendation,
                    }
                )
        alerts.sort(key=lambda item: item["riesgo_probabilidad"], reverse=True)
        return alerts

    @staticmethod
    def _build_name(row: Dict[str, Any]) -> str:
        def clean_part(part: Any) -> str | None:
            if part is None:
                return None
            if isinstance(part, float) and math.isnan(part):
                return None
            text = str(part).strip()
            if not text or text.lower() == "nan":
                return None
            return text

        parts = [
            clean_part(row.get("primer_nombre")),
            clean_part(row.get("segundo_nombre")),
            clean_part(row.get("primer_apellido")),
            clean_part(row.get("segundo_apellido")),
        ]
        return " ".join([part for part in parts if part])
