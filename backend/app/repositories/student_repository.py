from __future__ import annotations

from typing import Any, Dict, Tuple
import unicodedata

import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "promedio_academico",
    "materias_perdidas",
    "asistencia_clases",
    "rendimiento_periodo",
    "estado_pagos",
    "mora_matricula",
    "estrato",
    "ingresos_familiares",
    "horas_trabajo_semanales",
    "casos_riesgo",
]

NUMERIC_COLUMNS = [
    "promedio_academico",
    "materias_perdidas",
    "asistencia_clases",
    "rendimiento_periodo",
    "estrato",
    "ingresos_familiares",
    "horas_trabajo_semanales",
    "mora_matricula",
    "casos_riesgo",
]

CATEGORICAL_COLUMNS = ["estado_pagos"]
BOOLEAN_COLUMNS = ["mora_matricula", "casos_riesgo"]


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    return text.lower()


def _to_float(value: Any) -> float:
    if value is None:
        return float("nan")
    if isinstance(value, (int, float, np.number)):
        return float(value)
    try:
        return float(str(value).strip())
    except (ValueError, TypeError):
        return float("nan")


def _coerce_bool(value: Any) -> bool | None:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    if isinstance(value, bool):
        return value
    normalized = _normalize_text(value)
    if normalized in {"true", "1", "si", "s", "yes", "y"}:
        return True
    if normalized in {"false", "0", "no", "n"}:
        return False
    return None


class StudentRepository:
    def __init__(self, csv_path: str) -> None:
        self.csv_path = csv_path
        self._raw_df = pd.read_csv(csv_path)
        self._df = self._clean_dataframe(self._raw_df.copy())
        self._feature_defaults = self._compute_feature_defaults(self._df)

    @property
    def data(self) -> pd.DataFrame:
        return self._df

    def get_students_page(self, page: int, size: int) -> Tuple[pd.DataFrame, int]:
        total = len(self._df)
        start = (page - 1) * size
        end = start + size
        return self._df.iloc[start:end].copy(), total

    def get_student_by_id(self, student_id: str) -> Dict[str, Any] | None:
        if "id_estudiante" not in self._df.columns:
            return None
        match = self._df[self._df["id_estudiante"] == student_id]
        if match.empty:
            return None
        return match.iloc[0].to_dict()

    def feature_defaults(self) -> Dict[str, Any]:
        return dict(self._feature_defaults)

    def prepare_feature_row(self, data: Dict[str, Any]) -> Dict[str, Any]:
        row: Dict[str, Any] = {}
        for column in FEATURE_COLUMNS:
            value = data.get(column)
            if column in BOOLEAN_COLUMNS:
                coerced = _coerce_bool(value)
                if coerced is True:
                    row[column] = 1
                elif coerced is False:
                    row[column] = 0
                else:
                    row[column] = float("nan")
            elif column in NUMERIC_COLUMNS:
                row[column] = _to_float(value)
            else:
                row[column] = value
        return row

    def merge_with_defaults(self, data: Dict[str, Any]) -> Dict[str, Any]:
        merged = dict(self._feature_defaults)
        merged.update(self.prepare_feature_row(data))
        return merged

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        df.columns = [col.strip().lower() for col in df.columns]
        for column in NUMERIC_COLUMNS:
            if column in df.columns:
                df[column] = pd.to_numeric(df[column], errors="coerce")
        for column in BOOLEAN_COLUMNS:
            if column in df.columns:
                df[column] = df[column].apply(_coerce_bool)
                df[column] = df[column].map(
                    lambda value: 1 if value is True else 0 if value is False else np.nan
                )
        if "id_estudiante" in df.columns:
            df["id_estudiante"] = df["id_estudiante"].astype(str)
        if "estado_estudiante" in df.columns:
            df["estado_estudiante"] = df["estado_estudiante"].astype(str)
        return df

    def _compute_feature_defaults(self, df: pd.DataFrame) -> Dict[str, Any]:
        defaults: Dict[str, Any] = {}
        for column in FEATURE_COLUMNS:
            if column not in df.columns:
                defaults[column] = None
                continue
            if column in NUMERIC_COLUMNS:
                defaults[column] = float(df[column].median(skipna=True))
            else:
                mode = df[column].mode(dropna=True)
                defaults[column] = mode.iloc[0] if not mode.empty else None
        return defaults
