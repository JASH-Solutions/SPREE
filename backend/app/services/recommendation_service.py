from __future__ import annotations

from typing import Any, Dict


class RecommendationService:
    def recommend(self, row: Dict[str, Any], risk_level: str) -> str:
        promedio = row.get("promedio_academico")
        materias = row.get("materias_perdidas")
        asistencia = row.get("asistencia_clases")
        estado_pagos = str(row.get("estado_pagos") or "").lower()
        mora = row.get("mora_matricula")
        horas = row.get("horas_trabajo_semanales")

        if mora == 1 or "mora" in estado_pagos or "parcial" in estado_pagos:
            return "Apoyo financiero y plan de pagos"
        if (promedio is not None and promedio < 3.0) or (
            materias is not None and materias >= 5
        ):
            return "Tutoria academica y refuerzo"
        if asistencia is not None and asistencia < 70:
            return "Seguimiento con bienestar y acompanamiento"
        if horas is not None and horas > 30:
            return "Flexibilidad horaria y consejeria"
        if risk_level == "Alto":
            return "Intervencion integral prioritaria"
        if risk_level == "Medio":
            return "Plan preventivo de seguimiento"
        return "Seguimiento regular"
