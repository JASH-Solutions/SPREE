from __future__ import annotations

from collections import defaultdict

from fastapi import APIRouter, Request

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/risk-distribution")
async def get_risk_distribution(request: Request):
    service = request.app.state.student_service
    df = service.repository.data
    probs = service.risk_model.predict_proba(df)

    counts: dict[str, int] = {"Alto": 0, "Medio": 0, "Bajo": 0}
    for prob in probs:
        level = service.risk_model.risk_level(float(prob))
        counts[level] += 1

    total = len(probs)
    return {
        "total": total,
        "distribution": [
            {
                "level": level,
                "count": counts[level],
                "percentage": round(counts[level] / total * 100, 1) if total > 0 else 0,
            }
            for level in ["Alto", "Medio", "Bajo"]
        ],
    }


@router.get("/semester-evolution")
async def get_semester_evolution(request: Request):
    service = request.app.state.student_service
    df = service.repository.data

    if "semestre_cursado" not in df.columns:
        return {"semesters": []}

    probs = service.risk_model.predict_proba(df)
    semesters_col = df["semestre_cursado"].tolist()

    by_semester: dict = defaultdict(lambda: {"Alto": 0, "Medio": 0, "Bajo": 0})
    for sem, prob in zip(semesters_col, probs):
        try:
            key = int(sem)
        except (ValueError, TypeError):
            continue
        level = service.risk_model.risk_level(float(prob))
        by_semester[key][level] += 1

    return {
        "semesters": [
            {
                "semester": sem,
                "Alto": by_semester[sem]["Alto"],
                "Medio": by_semester[sem]["Medio"],
                "Bajo": by_semester[sem]["Bajo"],
            }
            for sem in sorted(by_semester.keys())
        ]
    }
