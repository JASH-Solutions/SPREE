from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = PROJECT_ROOT / "data" / "raw"
DEFAULT_MODELS_DIR = PROJECT_ROOT / "models"
DEFAULT_MODEL_PATH = DEFAULT_MODELS_DIR / "risk_model.pkl"
DEFAULT_METADATA_PATH = DEFAULT_MODELS_DIR / "risk_model_metadata.json"

TARGET_COLUMN = "target_desercion"
TARGET_RATIO = 0.30
RANDOM_STATE = 42

CANDIDATE_FEATURES = [
    "edad",
    "genero",
    "programa_academico",
    "ciudad_origen",
    "estrato",
    "ingresos_familiares",
    "num_dependientes",
    "situacion_laboral",
    "horas_trabajo_semanales",
    "lugar_residencia",
    "tipo_vivienda",
    "promedio_academico",
    "materias_perdidas",
    "semestre_cursado",
    "creditos_matriculados",
    "creditos_aprobados",
    "asistencia_clases",
    "rendimiento_periodo",
    "estado_pagos",
    "mora_matricula",
    "becas_apoyos",
    "atenciones_psicologicas",
    "seguimientos_realizados",
    "casos_riesgo",
    "participacion_institucional",
    "evaluacion_docente",
]


def _extract_student_order(student_ids: pd.Series) -> pd.Series:
    order = student_ids.astype(str).str.extract(r"(\d+)$", expand=False)
    return pd.to_numeric(order, errors="coerce")


def _load_and_merge_raw_data(data_dir: Path) -> tuple[pd.DataFrame, list[str]]:
    csv_files = sorted(path for path in data_dir.glob("*.csv") if path.is_file())
    if not csv_files:
        raise FileNotFoundError(f"No se encontraron archivos CSV en {data_dir}")

    frames: list[pd.DataFrame] = []
    loaded_files: list[str] = []
    for csv_file in csv_files:
        frame = pd.read_csv(csv_file)
        if "id_estudiante" not in frame.columns:
            raise ValueError(f"El archivo {csv_file.name} no contiene la columna id_estudiante")
        frames.append(frame)
        loaded_files.append(csv_file.name)

    merged = frames[0]
    for frame in frames[1:]:
        merged = merged.merge(frame, on="id_estudiante", how="inner")

    if merged.empty:
        raise ValueError("La unión de los archivos raw no produjo filas")

    merged = merged.copy()
    merged["_student_order"] = _extract_student_order(merged["id_estudiante"])
    if merged["_student_order"].isna().any():
        merged["_student_order"] = np.arange(len(merged))

    merged = merged.sort_values("_student_order", kind="mergesort").reset_index(drop=True)
    merged = merged.drop(columns=["_student_order"])
    return merged, loaded_files


def _build_target_frame(frame: pd.DataFrame) -> pd.DataFrame:
    ordered = frame.copy()
    n_rows = len(ordered)
    n_positive = max(1, int(round(n_rows * TARGET_RATIO)))

    target = np.zeros(n_rows, dtype=int)
    target[:n_positive] = 1
    rng = np.random.default_rng(RANDOM_STATE)
    rng.shuffle(target)

    ordered[TARGET_COLUMN] = target
    return ordered


def _select_feature_columns(frame: pd.DataFrame) -> list[str]:
    available = [column for column in CANDIDATE_FEATURES if column in frame.columns]
    if not available:
        raise ValueError("No hay columnas disponibles para entrenar el modelo")
    return available


def _build_pipeline(feature_frame: pd.DataFrame, random_state: int) -> tuple[Pipeline, list[str], list[str]]:
    numeric_features = [
        column
        for column in feature_frame.columns
        if pd.api.types.is_numeric_dtype(feature_frame[column]) or pd.api.types.is_bool_dtype(feature_frame[column])
    ]
    categorical_features = [column for column in feature_frame.columns if column not in numeric_features]

    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_transformer, numeric_features),
            ("categorical", categorical_transformer, categorical_features),
        ]
    )

    model = LogisticRegression(max_iter=1000, random_state=random_state)

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", model),
        ]
    )

    return pipeline, numeric_features, categorical_features


def train_and_persist_risk_model(
    data_dir: Path | str = DEFAULT_DATA_DIR,
    model_dir: Path | str = DEFAULT_MODELS_DIR,
    random_state: int = RANDOM_STATE,
) -> dict[str, Any]:
    data_path = Path(data_dir)
    model_path = Path(model_dir) / "risk_model.pkl"
    metadata_path = Path(model_dir) / "risk_model_metadata.json"

    merged_data, source_files = _load_and_merge_raw_data(data_path)
    labeled_data = _build_target_frame(merged_data)

    feature_columns = _select_feature_columns(labeled_data)
    feature_frame = labeled_data[feature_columns].copy()
    target = labeled_data[TARGET_COLUMN].astype(int)

    if target.nunique() < 2:
        raise ValueError("Se requieren al menos dos clases para entrenar el modelo")

    pipeline, numeric_features, categorical_features = _build_pipeline(feature_frame, random_state)

    x_train, x_test, y_train, y_test = train_test_split(
        feature_frame,
        target,
        test_size=0.2,
        random_state=random_state,
        stratify=target,
    )

    pipeline.fit(x_train, y_train)
    y_pred = pipeline.predict(x_test)
    y_proba = pipeline.predict_proba(x_test)[:, 1]

    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
    }

    try:
        metrics["roc_auc"] = float(roc_auc_score(y_test, y_proba))
    except ValueError:
        metrics["roc_auc"] = None

    # Reentrenar con todos los datos antes de persistir el artefacto final.
    pipeline.fit(feature_frame, target)

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, model_path)

    metadata = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model_type": "LogisticRegression",
        "artifact": model_path.name,
        "source_files": source_files,
        "rows": int(len(labeled_data)),
        "features": feature_columns,
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "metrics": metrics,
        "random_state": random_state,
    }

    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "model_path": model_path,
        "metadata_path": metadata_path,
        "metadata": metadata,
    }


def load_risk_model(model_path: Path | str = DEFAULT_MODEL_PATH) -> Pipeline:
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(f"No existe el modelo persistido en {path}")
    return joblib.load(path)


def load_risk_model_metadata(metadata_path: Path | str = DEFAULT_METADATA_PATH) -> dict[str, Any]:
    path = Path(metadata_path)
    if not path.exists():
        raise FileNotFoundError(f"No existe la metadata del modelo en {path}")
    return json.loads(path.read_text(encoding="utf-8"))
