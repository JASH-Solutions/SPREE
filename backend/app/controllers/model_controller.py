"""
Controlador de métricas del modelo ML.
"""
from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/model", tags=["Model Metrics"])


class ModelMetricsResponse(BaseModel):
    """Respuesta con métricas del modelo."""
    version: str
    f1_score: float
    recall: float
    roc_auc: float
    accuracy: float
    timestamp: str
    description: str


class ModelListResponse(BaseModel):
    """Respuesta con lista de modelos."""
    total: int
    models: list


@router.get("/metrics", response_model=ModelMetricsResponse)
async def get_model_metrics(request: Request):
    """
    Obtener métricas del modelo actual.
    
    Returns:
        Métricas de F1-Score, Recall, ROC-AUC y Accuracy
    """
    persister = request.app.state.model_persister
    model_info = persister.get_model_info()
    
    if not model_info:
        return {"error": "No model found"}
    
    return {
        "version": model_info["version"],
        "f1_score": model_info["metrics"]["f1_score"],
        "recall": model_info["metrics"]["recall"],
        "roc_auc": model_info["metrics"]["roc_auc"],
        "accuracy": model_info["metrics"]["accuracy"],
        "timestamp": model_info["timestamp"],
        "description": model_info["description"],
    }


@router.get("/versions", response_model=ModelListResponse)
async def list_models(request: Request):
    """
    Listar todos los modelos entrenados.
    
    Returns:
        Lista de versiones de modelos con métricas
    """
    persister = request.app.state.model_persister
    models = persister.list_models()
    
    return {
        "total": len(models),
        "models": models,
    }


@router.get("/feature-importance")
async def get_feature_importance(request: Request):
    """
    Importancia de cada feature en el modelo Random Forest.
    """
    risk_model = request.app.state.risk_model
    pipeline = risk_model.pipeline
    feature_columns = risk_model.feature_columns

    LABELS = {
        "promedio_academico": "Promedio Académico",
        "asistencia_clases": "Asistencia a Clases",
        "horas_trabajo_semanales": "Horas Trabajo Semanales",
        "ingresos_familiares": "Ingresos Familiares",
        "estrato": "Estrato Socioeconómico",
        "rendimiento_periodo": "Rendimiento del Período",
    }

    try:
        preprocessor = pipeline.named_steps["preprocess"]
        classifier = pipeline.named_steps["classifier"]

        try:
            raw_names = preprocessor.get_feature_names_out()
            names = [n.split("__", 1)[-1] if "__" in n else n for n in raw_names]
        except Exception:
            names = list(feature_columns)

        importances = classifier.feature_importances_.tolist()

        result = sorted(
            [
                {
                    "feature": name,
                    "label": LABELS.get(name, name.replace("_", " ").title()),
                    "importance": round(float(imp), 4),
                }
                for name, imp in zip(names, importances)
            ],
            key=lambda x: x["importance"],
            reverse=True,
        )

        return {"features": result}

    except Exception as exc:
        return {"features": [], "error": str(exc)}


@router.get("/info")
async def get_model_info(request: Request):
    """
    Obtener información completa del modelo actual.
    
    Returns:
        Información detallada incluyendo path y configuración
    """
    persister = request.app.state.model_persister
    model_info = persister.get_model_info()
    
    if not model_info:
        return {"error": "No model found"}
    
    return {
        "version": model_info["version"],
        "timestamp": model_info["timestamp"],
        "description": model_info["description"],
        "metrics": model_info["metrics"],
        "test_samples": model_info.get("test_samples", "N/A"),
    }
