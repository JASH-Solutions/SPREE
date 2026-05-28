"""
Búsqueda de hiperparámetros óptimos con GridSearchCV.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, Any

import pandas as pd
import numpy as np
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

from .metrics import calculate_metrics

logger = logging.getLogger("spree.hyperparameter_tuning")

# Features (causal only, no leakage)
CAUSAL_FEATURES = [
    "promedio_academico",
    "asistencia_clases",
    "horas_trabajo_semanales",
    "ingresos_familiares",
    "estrato",
    "rendimiento_periodo",
]

NUMERIC_FEATURES = [
    "promedio_academico",
    "asistencia_clases",
    "horas_trabajo_semanales",
    "ingresos_familiares",
    "rendimiento_periodo",
]

CATEGORICAL_FEATURES = ["estrato"]

# Rutas
TUNING_DIR = Path(__file__).parent.parent.parent / "models"
BEST_PARAMS_FILE = TUNING_DIR / "best_hyperparams.json"


class HyperparameterTuner:
    """Buscar hiperparámetros óptimos para RandomForest."""
    
    def __init__(self, df: pd.DataFrame, target_column: str = "estado_estudiante"):
        self.df = df.copy()
        self.target_column = target_column
        self.feature_columns = CAUSAL_FEATURES
        self.numeric_features = NUMERIC_FEATURES
        self.categorical_features = CATEGORICAL_FEATURES
        
        logger.info("🔧 Hiperparameter Tuner inicializado")
        logger.info(f"  Features: {len(self.feature_columns)} causales")
        logger.info(f"  Datos: {len(self.df)} registros")
    
    def _prepare_data(self) -> tuple:
        """Preparar datos para GridSearchCV."""
        # Preparar X, y
        x = self.df[self.feature_columns].copy()
        
        # Target: 1=desertor, 0=no desertor
        target_series = self.df[self.target_column].astype(str).str.lower()
        y = target_series.apply(lambda value: 1 if "desertor" in value else 0)
        
        logger.info(f"✅ Datos preparados:")
        logger.info(f"   Desertores (y=1): {(y == 1).sum()}")
        logger.info(f"   No desertores (y=0): {(y == 0).sum()}")
        
        return x, y
    
    def _build_pipeline(self, classifier_params: Dict[str, Any] = None) -> Pipeline:
        """Construir pipeline de preprocesamiento + clasificación."""
        numeric_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ])
        
        categorical_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ])
        
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", numeric_transformer, self.numeric_features),
                ("cat", categorical_transformer, self.categorical_features),
            ],
            remainder="drop",
        )
        
        if classifier_params is None:
            classifier_params = {}
        
        classifier = RandomForestClassifier(**classifier_params)
        
        return Pipeline(steps=[
            ("preprocess", preprocessor),
            ("classifier", classifier),
        ])
    
    def tune(self) -> Dict[str, Any]:
        """
        Ejecutar GridSearchCV para encontrar mejores hiperparámetros.
        
        Returns:
            Dict con best_params, best_score, cv_results
        """
        x, y = self._prepare_data()
        
        # Grid de búsqueda
        param_grid = {
            "classifier__n_estimators": [100, 150, 200],
            "classifier__max_depth": [8, 10, 12],
            "classifier__min_samples_leaf": [3, 4, 5],
            "classifier__min_samples_split": [5, 10],
            "classifier__class_weight": ["balanced", "balanced_subsample"],
        }
        
        logger.info("🔍 Iniciando GridSearchCV...")
        logger.info(f"  Combinaciones a probar: {np.prod([len(v) for v in param_grid.values()])}")
        logger.info(f"  CV: 5-fold")
        
        # Pipeline base sin params (params los agrega GridSearchCV)
        pipeline = self._build_pipeline({
            "n_estimators": 100,
            "random_state": 42,
        })
        
        # GridSearchCV
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        grid_search = GridSearchCV(
            pipeline,
            param_grid,
            cv=cv,
            scoring="f1_weighted",
            n_jobs=-1,
            verbose=2,
        )
        
        # Ejecutar búsqueda
        logger.info("⏳ Buscando mejores parámetros...")
        grid_search.fit(x, y)
        
        logger.info("✅ GridSearchCV completado")
        logger.info(f"  Best F1-Score: {grid_search.best_score_:.4f}")
        logger.info(f"  Best params:")
        for key, value in grid_search.best_params_.items():
            logger.info(f"    {key}: {value}")
        
        # Guardar resultados
        results = {
            "best_params": grid_search.best_params_,
            "best_score": float(grid_search.best_score_),
            "best_estimator_type": "RandomForestClassifier",
            "cv_results": {
                "mean_test_score": grid_search.cv_results_["mean_test_score"].tolist(),
                "std_test_score": grid_search.cv_results_["std_test_score"].tolist(),
            }
        }
        
        return results, grid_search.best_estimator_
    
    def save_best_params(self, results: Dict[str, Any]) -> None:
        """Guardar mejores parámetros a archivo."""
        TUNING_DIR.mkdir(parents=True, exist_ok=True)
        
        with open(BEST_PARAMS_FILE, "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"💾 Parámetros guardados en: {BEST_PARAMS_FILE}")
    
    @staticmethod
    def load_best_params() -> Dict[str, Any]:
        """Cargar mejores parámetros guardados."""
        if not BEST_PARAMS_FILE.exists():
            logger.warning(f"No se encontró: {BEST_PARAMS_FILE}")
            return None
        
        with open(BEST_PARAMS_FILE, "r") as f:
            return json.load(f)


def extract_rf_params(grid_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extraer parámetros de RandomForest del GridSearchCV result.
    
    Convierte "classifier__param" a "param"
    """
    rf_params = {}
    for key, value in grid_params.items():
        if key.startswith("classifier__"):
            param_name = key.replace("classifier__", "")
            rf_params[param_name] = value
    
    return rf_params
