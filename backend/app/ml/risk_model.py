from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from ..repositories.student_repository import (
    CATEGORICAL_COLUMNS,
    FEATURE_COLUMNS,
    NUMERIC_COLUMNS,
)


@dataclass
class RiskPrediction:
    level: str
    probability: float


class RiskModel:
    def __init__(self, df: pd.DataFrame, target_column: str = "estado_estudiante") -> None:
        self.target_column = target_column
        self.feature_columns = [col for col in FEATURE_COLUMNS if col in df.columns]
        if not self.feature_columns:
            raise ValueError("No valid feature columns available for training.")
        self.numeric_columns = [
            col for col in NUMERIC_COLUMNS if col in self.feature_columns
        ]
        self.categorical_columns = [
            col for col in CATEGORICAL_COLUMNS if col in self.feature_columns
        ]
        self.pipeline = self._build_pipeline()
        self._fit(df)

    def _build_pipeline(self) -> Pipeline:
        numeric_transformer = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]
        )
        categorical_transformer = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore")),
            ]
        )
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", numeric_transformer, self.numeric_columns),
                ("cat", categorical_transformer, self.categorical_columns),
            ],
            remainder="drop",
        )
        classifier = RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            class_weight="balanced",
        )
        return Pipeline(
            steps=[
                ("preprocess", preprocessor),
                ("classifier", classifier),
            ]
        )

    def _fit(self, df: pd.DataFrame) -> None:
        if self.target_column not in df.columns:
            raise ValueError("Target column not found in dataset.")
        target_series = df[self.target_column].astype(str).str.lower()
        y = target_series.apply(lambda value: 1 if "desertor" in value else 0)
        x = df[self.feature_columns].copy()
        self.pipeline.fit(x, y)

    def predict_proba(self, df: pd.DataFrame) -> List[float]:
        x = df[self.feature_columns].copy()
        probs = self.pipeline.predict_proba(x)
        return probs[:, 1].tolist()

    def predict_proba_row(self, row: Dict[str, Any]) -> float:
        df = pd.DataFrame([row])
        return self.predict_proba(df)[0]

    @staticmethod
    def risk_level(probability: float) -> str:
        if probability >= 0.66:
            return "Alto"
        if probability >= 0.33:
            return "Medio"
        return "Bajo"

    def predict(self, row: Dict[str, Any]) -> RiskPrediction:
        probability = float(self.predict_proba_row(row))
        return RiskPrediction(level=self.risk_level(probability), probability=probability)
