"""
Modelo limpio sin data leakage.

Features CAUSALES (disponibles ANTES de que el estudiante deserte):
- promedio_academico
- asistencia_clases
- horas_trabajo_semanales
- ingresos_familiares
- estrato
- rendimiento_periodo
"""
from pathlib import Path
import sys

# Agregar backend al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from app.config import DATA_PATH
from app.repositories.student_repository import StudentRepository
from app.ml.metrics import ModelMetrics, calculate_metrics, get_classification_report


class CleanModelTrainer:
    """Trainer para modelo sin data leakage."""
    
    def __init__(self, df: pd.DataFrame, target_column: str = "estado_estudiante"):
        """Inicializar con features CAUSALES solo."""
        self.df = df
        self.target_column = target_column
        self.random_state = 42
        
        # Features CAUSALES (sin leakage)
        self.feature_columns = [
            "promedio_academico",
            "asistencia_clases",
            "horas_trabajo_semanales",
            "ingresos_familiares",
            "estrato",
            "rendimiento_periodo",
        ]
        
        # Filtrar features que existan en el dataset
        self.feature_columns = [col for col in self.feature_columns if col in df.columns]
        
        if not self.feature_columns:
            raise ValueError("No valid causal features available")
        
        # Separar numéricos y categóricos
        self.numeric_columns = df[self.feature_columns].select_dtypes(
            include=[np.number]
        ).columns.tolist()
        
        self.categorical_columns = df[self.feature_columns].select_dtypes(
            exclude=[np.number]
        ).columns.tolist()
        
        # Conjuntos de datos
        self.X_train = None
        self.X_val = None
        self.X_test = None
        self.y_train = None
        self.y_val = None
        self.y_test = None
        
        # Modelo
        self.pipeline = None
        
        # Métricas
        self.train_metrics = None
        self.val_metrics = None
        self.test_metrics = None
    
    def _prepare_data(self):
        """Preparar y dividir datos."""
        if self.target_column not in self.df.columns:
            raise ValueError("Target column not found")
        
        # Target
        target_series = self.df[self.target_column].astype(str).str.lower()
        y = target_series.apply(lambda value: 1 if "desertor" in value else 0).values
        
        # Features
        X = self.df[self.feature_columns].copy()
        
        # Split train/test
        X_temp, self.X_test, y_temp, self.y_test = train_test_split(
            X, y,
            test_size=0.15,
            random_state=self.random_state,
            stratify=y
        )
        
        # Split train/val
        self.X_train, self.X_val, self.y_train, self.y_val = train_test_split(
            X_temp, y_temp,
            test_size=0.15 / 0.85,
            random_state=self.random_state,
            stratify=y_temp
        )
        
        print(f"\n📊 DATOS SIN LEAKAGE:")
        print(f"  Train: {len(self.X_train)}")
        print(f"  Val:   {len(self.X_val)}")
        print(f"  Test:  {len(self.X_test)}")
        print(f"\n⚙️  FEATURES CAUSALES (sin leakage):")
        for col in self.feature_columns:
            print(f"  ✅ {col}")
    
    def _build_pipeline(self):
        """Construir pipeline."""
        numeric_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ])
        
        categorical_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ])
        
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", numeric_transformer, self.numeric_columns),
                ("cat", categorical_transformer, self.categorical_columns),
            ],
            remainder="drop",
        )
        
        classifier = RandomForestClassifier(
            n_estimators=150,  # Optimized via GridSearchCV
            max_depth=8,       # Optimized via GridSearchCV
            min_samples_leaf=4,  # Optimized via GridSearchCV
            min_samples_split=10,
            random_state=self.random_state,
            class_weight="balanced",
            n_jobs=-1,
        )
        
        return Pipeline(steps=[
            ("preprocess", preprocessor),
            ("classifier", classifier),
        ])
    
    def train(self):
        """Entrenar modelo."""
        print("\n🚀 ENTRENANDO MODELO SIN DATA LEAKAGE...\n")
        
        self._prepare_data()
        
        self.pipeline = self._build_pipeline()
        
        print("\n⏳ Entrenando...")
        self.pipeline.fit(self.X_train, self.y_train)
        print("✅ Listo")
        
        # Evaluar
        print("\n📈 Evaluando Train...")
        y_train_pred = self.pipeline.predict(self.X_train)
        y_train_proba = self.pipeline.predict_proba(self.X_train)[:, 1]
        self.train_metrics = calculate_metrics(self.y_train, y_train_pred, y_train_proba)
        
        print("📊 Evaluando Validation...")
        y_val_pred = self.pipeline.predict(self.X_val)
        y_val_proba = self.pipeline.predict_proba(self.X_val)[:, 1]
        self.val_metrics = calculate_metrics(self.y_val, y_val_pred, y_val_proba)
        
        print("🧪 Evaluando Test...")
        y_test_pred = self.pipeline.predict(self.X_test)
        y_test_proba = self.pipeline.predict_proba(self.X_test)[:, 1]
        self.test_metrics = calculate_metrics(self.y_test, y_test_pred, y_test_proba)
        
        # CV
        print("\n🔄 Validación Cruzada...")
        cv_scores = cross_val_score(
            self.pipeline,
            self.X_train,
            self.y_train,
            cv=5,
            scoring='f1_weighted'
        )
        print(f"  F1-Score: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        return self.test_metrics
    
    def print_results(self):
        """Mostrar resultados."""
        print("\n" + "="*70)
        print("📊 RESULTADOS - MODELO SIN DATA LEAKAGE")
        print("="*70)
        
        print("\n🎯 TRAIN SET:")
        print(f"  F1-Score (Desertores): {self.train_metrics.f1_dropouts:.4f}")
        print(f"  Recall (Desertores):   {self.train_metrics.recall_dropouts:.4f}")
        print(f"  ROC-AUC:               {self.train_metrics.roc_auc:.4f}")
        
        print("\n✅ VALIDATION SET:")
        print(f"  F1-Score (Desertores): {self.val_metrics.f1_dropouts:.4f}")
        print(f"  Recall (Desertores):   {self.val_metrics.recall_dropouts:.4f}")
        print(f"  ROC-AUC:               {self.val_metrics.roc_auc:.4f}")
        
        print("\n🧪 TEST SET:")
        print(f"  F1-Score (Desertores): {self.test_metrics.f1_dropouts:.4f}")
        print(f"  Recall (Desertores):   {self.test_metrics.recall_dropouts:.4f}")
        print(f"  ROC-AUC:               {self.test_metrics.roc_auc:.4f}")
        print(f"  Accuracy:              {self.test_metrics.accuracy:.4f}")
        
        print(f"\n📋 MATRIZ DE CONFUSIÓN (Test):")
        print(f"  VP (correctos):  {self.test_metrics.tp}")
        print(f"  FP (falsos):     {self.test_metrics.fp}")
        print(f"  VN (correctos):  {self.test_metrics.tn}")
        print(f"  FN (falsos):     {self.test_metrics.fn}")
        
        # Análisis de overfitting
        f1_diff = self.train_metrics.f1_dropouts - self.test_metrics.f1_dropouts
        print(f"\n⚠️  OVERFITTING CHECK:")
        print(f"  Diferencia F1 (Train-Test): {f1_diff:+.4f}")
        if abs(f1_diff) > 0.1:
            print(f"  ⚠️  Posible overfitting")
        else:
            print(f"  ✅ Generalización correcta")
        
        print("\n" + "="*70)
        print("📋 REPORTE DE CLASIFICACIÓN - TEST SET")
        print("="*70)
        y_test_pred = self.pipeline.predict(self.X_test)
        print(get_classification_report(self.y_test, y_test_pred))


def main():
    if not DATA_PATH.exists():
        print(f"Error: Dataset not found at {DATA_PATH}")
        sys.exit(1)
    
    repository = StudentRepository(str(DATA_PATH))
    
    trainer = CleanModelTrainer(repository.data)
    trainer.train()
    trainer.print_results()


if __name__ == "__main__":
    main()
