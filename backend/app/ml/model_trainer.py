from __future__ import annotations

from typing import Tuple
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
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
from .metrics import ModelMetrics, calculate_metrics


class ModelTrainer:
    """
    Entrena el modelo con validación adecuada train/test/validation split.
    """
    
    def __init__(
        self,
        df: pd.DataFrame,
        target_column: str = "estado_estudiante",
        test_size: float = 0.15,
        val_size: float = 0.15,
        random_state: int = 42,
    ):
        """
        Inicializar trainer.
        
        Args:
            df: DataFrame con todos los datos
            target_column: Nombre de la columna objetivo
            test_size: Proporción para conjunto de test (0.15 = 15%)
            val_size: Proporción para validación (0.15 = 15%)
            random_state: Seed para reproducibilidad
        """
        self.df = df
        self.target_column = target_column
        self.test_size = test_size
        self.val_size = val_size
        self.random_state = random_state
        
        self.feature_columns = [col for col in FEATURE_COLUMNS if col in df.columns]
        if not self.feature_columns:
            raise ValueError("No valid feature columns available for training.")
        
        self.numeric_columns = [
            col for col in NUMERIC_COLUMNS if col in self.feature_columns
        ]
        self.categorical_columns = [
            col for col in CATEGORICAL_COLUMNS if col in self.feature_columns
        ]
        
        # Conjuntos de datos
        self.X_train: pd.DataFrame | None = None
        self.X_val: pd.DataFrame | None = None
        self.X_test: pd.DataFrame | None = None
        self.y_train: np.ndarray | None = None
        self.y_val: np.ndarray | None = None
        self.y_test: np.ndarray | None = None
        
        # Modelo
        self.pipeline: Pipeline | None = None
        
        # Métricas
        self.train_metrics: ModelMetrics | None = None
        self.val_metrics: ModelMetrics | None = None
        self.test_metrics: ModelMetrics | None = None
    
    def _prepare_data(self) -> None:
        """Preparar y dividir datos."""
        if self.target_column not in self.df.columns:
            raise ValueError("Target column not found in dataset.")
        
        # Preparar target
        target_series = self.df[self.target_column].astype(str).str.lower()
        y = target_series.apply(lambda value: 1 if "desertor" in value else 0).values
        
        # Preparar features
        X = self.df[self.feature_columns].copy()
        
        # Split: 70% train, 15% val, 15% test
        X_temp, self.X_test, y_temp, self.y_test = train_test_split(
            X, y,
            test_size=self.test_size,
            random_state=self.random_state,
            stratify=y
        )
        
        # De los datos temporales, dividir en train y val
        val_size_adjusted = self.val_size / (1 - self.test_size)
        self.X_train, self.X_val, self.y_train, self.y_val = train_test_split(
            X_temp, y_temp,
            test_size=val_size_adjusted,
            random_state=self.random_state,
            stratify=y_temp
        )
        
        print(f"\n📊 DIVISIÓN DE DATOS:")
        print(f"  Train: {len(self.X_train)} ({len(self.X_train)/len(X)*100:.1f}%)")
        print(f"  Val:   {len(self.X_val)} ({len(self.X_val)/len(X)*100:.1f}%)")
        print(f"  Test:  {len(self.X_test)} ({len(self.X_test)/len(X)*100:.1f}%)")
        
        # Mostrar distribución de clases
        print(f"\n⚖️ DISTRIBUCIÓN DE CLASES:")
        for set_name, y_set in [("Train", self.y_train), ("Val", self.y_val), ("Test", self.y_test)]:
            no_desertores = np.sum(y_set == 0)
            desertores = np.sum(y_set == 1)
            print(f"  {set_name}: {desertores}/{len(y_set)} desertores ({desertores/len(y_set)*100:.1f}%)")
    
    def _build_pipeline(self) -> Pipeline:
        """Construir pipeline de preprocesamiento + clasificación."""
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
            max_depth=15,
            min_samples_leaf=5,
            min_samples_split=10,
            random_state=self.random_state,
            class_weight="balanced",
            n_jobs=-1,
        )
        return Pipeline(
            steps=[
                ("preprocess", preprocessor),
                ("classifier", classifier),
            ]
        )
    
    def train(self) -> ModelMetrics:
        """
        Entrenar el modelo y evaluar en todos los conjuntos.
        
        Returns:
            test_metrics: Métricas en conjunto de test
        """
        print("\n🚀 INICIANDO ENTRENAMIENTO...\n")
        
        # Preparar datos
        self._prepare_data()
        
        # Construir pipeline
        self.pipeline = self._build_pipeline()
        
        # Entrenar
        print("\n⏳ Entrenando modelo...")
        self.pipeline.fit(self.X_train, self.y_train)
        print("✅ Entrenamiento completado")
        
        # Evaluar en train
        print("\n📈 Evaluando en Train...")
        y_train_pred = self.pipeline.predict(self.X_train)
        y_train_proba = self.pipeline.predict_proba(self.X_train)[:, 1]
        self.train_metrics = calculate_metrics(self.y_train, y_train_pred, y_train_proba)
        
        # Evaluar en validation
        print("\n📊 Evaluando en Validation...")
        y_val_pred = self.pipeline.predict(self.X_val)
        y_val_proba = self.pipeline.predict_proba(self.X_val)[:, 1]
        self.val_metrics = calculate_metrics(self.y_val, y_val_pred, y_val_proba)
        
        # Evaluar en test
        print("\n🧪 Evaluando en Test...")
        y_test_pred = self.pipeline.predict(self.X_test)
        y_test_proba = self.pipeline.predict_proba(self.X_test)[:, 1]
        self.test_metrics = calculate_metrics(self.y_test, y_test_pred, y_test_proba)
        
        # Validación cruzada
        print("\n🔄 Validación Cruzada (5-fold)...")
        cv_scores = cross_val_score(
            self.pipeline,
            self.X_train,
            self.y_train,
            cv=5,
            scoring='f1_weighted'
        )
        print(f"  F1-Score: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        return self.test_metrics
    
    def get_metrics_summary(self) -> str:
        """Obtener resumen de métricas en los 3 conjuntos."""
        summary = "\n" + "="*60
        summary += "\n🎯 RESUMEN DE MÉTRICAS - TODOS LOS CONJUNTOS"
        summary += "\n" + "="*60
        
        if self.train_metrics:
            summary += "\n\n📚 TRAIN SET:"
            summary += f"\n  F1-Score (Desertores): {self.train_metrics.f1_dropouts:.4f}"
            summary += f"\n  Recall (Desertores):   {self.train_metrics.recall_dropouts:.4f}"
            summary += f"\n  ROC-AUC:               {self.train_metrics.roc_auc:.4f}"
        
        if self.val_metrics:
            summary += "\n\n✅ VALIDATION SET:"
            summary += f"\n  F1-Score (Desertores): {self.val_metrics.f1_dropouts:.4f}"
            summary += f"\n  Recall (Desertores):   {self.val_metrics.recall_dropouts:.4f}"
            summary += f"\n  ROC-AUC:               {self.val_metrics.roc_auc:.4f}"
        
        if self.test_metrics:
            summary += "\n\n🧪 TEST SET (CONFIABLE):"
            summary += f"\n  F1-Score (Desertores): {self.test_metrics.f1_dropouts:.4f}"
            summary += f"\n  Recall (Desertores):   {self.test_metrics.recall_dropouts:.4f}"
            summary += f"\n  ROC-AUC:               {self.test_metrics.roc_auc:.4f}"
            summary += f"\n  Accuracy:              {self.test_metrics.accuracy:.4f}"
        
        summary += "\n" + "="*60 + "\n"
        
        # Análisis de overfitting
        if self.train_metrics and self.test_metrics:
            f1_diff = self.train_metrics.f1_dropouts - self.test_metrics.f1_dropouts
            summary += f"\n⚠️ ANÁLISIS DE OVERFITTING:"
            summary += f"\n  Diferencia F1 (Train-Test): {f1_diff:.4f}"
            if f1_diff > 0.1:
                summary += "\n  ⚠️ Posible overfitting detectado"
            else:
                summary += "\n  ✅ Modelo generaliza bien"
        
        return summary
