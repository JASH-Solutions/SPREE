"""
Script para detectar data leakage y analizar features.

Uso:
    cd backend
    python app/ml/analyze_leakage.py
"""
from pathlib import Path
import sys
import logging

# Agregar backend al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

from app.config import DATA_PATH
from app.repositories.student_repository import StudentRepository, FEATURE_COLUMNS


def analyze_feature_importance():
    """Analizar importancia de features."""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("spree.leakage")
    
    if not DATA_PATH.exists():
        logger.error(f"Dataset not found at {DATA_PATH}")
        sys.exit(1)
    
    logger.info(f"Cargando datos desde {DATA_PATH}")
    repository = StudentRepository(str(DATA_PATH))
    df = repository.data
    
    # Preparar datos
    feature_columns = [col for col in FEATURE_COLUMNS if col in df.columns]
    target_series = df["estado_estudiante"].astype(str).str.lower()
    y = target_series.apply(lambda value: 1 if "desertor" in value else 0)
    X = df[feature_columns].copy()
    
    print("\n" + "="*70)
    print("🔍 ANÁLISIS DE DATA LEAKAGE Y FEATURES")
    print("="*70)
    
    # 1. Ver columnas disponibles
    print(f"\n📋 TOTAL DE COLUMNAS EN DATASET: {len(df.columns)}")
    print(f"📊 TOTAL DE FEATURES USADAS: {len(feature_columns)}")
    print(f"👥 TOTAL DE ESTUDIANTES: {len(df)}")
    print(f"⚠️  DESERTORES: {np.sum(y)} ({np.sum(y)/len(y)*100:.1f}%)")
    
    # 2. Verificar IDs y variables sospechosas
    print("\n" + "-"*70)
    print("🚨 VERIFICACIÓN DE VARIABLES SOSPECHOSAS:")
    print("-"*70)
    
    suspicious_cols = []
    for col in feature_columns:
        # Revisar si es un ID o tiene valores muy únicos
        unique_ratio = df[col].nunique() / len(df)
        if unique_ratio > 0.9:
            suspicious_cols.append((col, unique_ratio))
            print(f"⚠️  {col}: {unique_ratio*100:.1f}% valores únicos")
    
    if not suspicious_cols:
        print("✅ No se detectaron variables de ID")
    
    # 3. Verificar duplicados
    print("\n" + "-"*70)
    print("🔎 VERIFICACIÓN DE DUPLICADOS:")
    print("-"*70)
    
    duplicates = df[feature_columns].duplicated().sum()
    print(f"  Filas duplicadas (features): {duplicates}")
    
    # 4. Correlación con target
    print("\n" + "-"*70)
    print("📈 TOP 20 FEATURES POR CORRELACIÓN CON TARGET:")
    print("-"*70)
    
    # Convertir a numérico para correlación
    X_numeric = X.copy()
    for col in X_numeric.columns:
        if X_numeric[col].dtype == 'object':
            # Codificar categorías
            X_numeric[col] = pd.factorize(X_numeric[col])[0]
    
    correlations = []
    for col in X_numeric.columns:
        try:
            corr = X_numeric[col].corr(y)
            correlations.append((col, abs(corr)))
        except:
            pass
    
    correlations.sort(key=lambda x: x[1], reverse=True)
    
    for i, (col, corr) in enumerate(correlations[:20], 1):
        print(f"  {i:2d}. {col:40s}: {corr:.4f}")
    
    # 5. Feature Importance del RandomForest
    print("\n" + "-"*70)
    print("🎯 FEATURE IMPORTANCE (RandomForest):")
    print("-"*70)
    
    # Preparar datos para RF - manejar categorías correctamente
    from sklearn.preprocessing import LabelEncoder
    
    X_train = X.copy()
    
    for col in X_train.columns:
        try:
            # Intentar median para numéricos
            median_val = pd.to_numeric(X_train[col], errors='coerce').median()
            X_train[col] = pd.to_numeric(X_train[col], errors='coerce').fillna(median_val)
        except:
            # Si no es posible, es categórico - codificar
            X_train[col] = X_train[col].fillna('MISSING')
            le = LabelEncoder()
            X_train[col] = le.fit_transform(X_train[col].astype(str))
    
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X_train, y)
    
    importances = []
    for col, imp in zip(feature_columns, rf.feature_importances_):
        importances.append((col, imp))
    
    importances.sort(key=lambda x: x[1], reverse=True)
    
    for i, (col, imp) in enumerate(importances[:20], 1):
        print(f"  {i:2d}. {col:40s}: {imp:.6f}")
    
    # 6. Mostrar features que son 100% importantes
    print("\n" + "-"*70)
    print("⚠️  FEATURES CON IMPORTANCIA ANORMALMENTE ALTA:")
    print("-"*70)
    
    for col, imp in importances[:5]:
        if imp > 0.3:
            print(f"  ⚠️  {col}: {imp:.4f} - Posible data leakage!")
            # Mostrar distribución
            print(f"      Valores únicos: {df[col].nunique()}")
            print(f"      Tipo: {df[col].dtype}")
    
    # 7. Información de features numéricos vs categóricos
    print("\n" + "-"*70)
    print("📊 DESGLOSE DE FEATURES:")
    print("-"*70)
    
    numeric_features = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical_features = X.select_dtypes(exclude=[np.number]).columns.tolist()
    
    print(f"  Numéricos: {len(numeric_features)}")
    for col in numeric_features[:5]:
        print(f"    - {col}")
    
    print(f"\n  Categóricos: {len(categorical_features)}")
    for col in categorical_features[:5]:
        print(f"    - {col} ({df[col].nunique()} valores)")
    
    print("\n" + "="*70)
    print("💡 RECOMENDACIONES:")
    print("="*70)
    print("""
1. Si features con alta importancia son ID o nombres → ELIMINAR
2. Si hay variables categóricas = estado_estudiante → ELIMINAR (data leakage)
3. Si hay columnas de fecha futura → ELIMINAR
4. Revisar si "estado_estudiante" está en los features
5. Considerar validación temporal (no solo aleatorios)
""")
    print("="*70 + "\n")


if __name__ == "__main__":
    analyze_feature_importance()
