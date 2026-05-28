"""
Script para investigar causalidad vs consecuencia en features.

Uso:
    cd backend
    python app/ml/investigate_causality.py
"""
from pathlib import Path
import sys

# Agregar backend al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
import numpy as np

from app.config import DATA_PATH
from app.repositories.student_repository import StudentRepository


def analyze_feature_causality():
    """Analizar si features son causales o consecuenciales."""
    
    if not DATA_PATH.exists():
        print(f"Error: Dataset not found at {DATA_PATH}")
        sys.exit(1)
    
    repository = StudentRepository(str(DATA_PATH))
    df = repository.data
    
    # Separar desertores y no-desertores
    target_series = df["estado_estudiante"].astype(str).str.lower()
    is_desertor = target_series.apply(lambda value: 1 if "desertor" in value else 0)
    
    desertores = df[is_desertor == 1]
    no_desertores = df[is_desertor == 0]
    
    print("\n" + "="*70)
    print("🔍 ANÁLISIS DE CAUSALIDAD: ¿Causa o Consecuencia?")
    print("="*70)
    
    features_to_analyze = [
        "materias_perdidas",
        "asistencia_clases", 
        "promedio_academico",
        "mora_matricula",
        "casos_riesgo",
        "rendimiento_periodo",
    ]
    
    print("\n" + "-"*70)
    print("⚠️  ANÁLISIS DE FEATURES SOSPECHOSAS:")
    print("-"*70)
    print("\nUna feature es SOSPECHOSA si:")
    print("  • Difiere significativamente entre desertores y no-desertores")
    print("  • Es más probable que sea CONSECUENCIA que CAUSA")
    print("  • Solo estaría disponible después que el estudiante deserta\n")
    
    for feature in features_to_analyze:
        if feature not in df.columns:
            continue
        
        print(f"\n{feature}:")
        print("-" * 60)
        
        try:
            # Convertir a numérico para análisis
            desertor_vals = pd.to_numeric(desertores[feature], errors='coerce').dropna()
            no_desertor_vals = pd.to_numeric(no_desertores[feature], errors='coerce').dropna()
            
            if len(desertor_vals) == 0:
                print(f"  (Sin datos numéricos)")
                continue
            
            # Estadísticas
            d_mean = desertor_vals.mean()
            nd_mean = no_desertor_vals.mean()
            d_std = desertor_vals.std()
            nd_std = no_desertor_vals.std()
            
            print(f"  Desertores:        {d_mean:8.2f} ± {d_std:.2f}")
            print(f"  No Desertores:     {nd_mean:8.2f} ± {nd_std:.2f}")
            print(f"  Diferencia:        {abs(d_mean - nd_mean):8.2f}")
            
            # Análisis
            if feature == "materias_perdidas":
                print(f"\n  🚨 SOSPECHA: Estudiantes que desertan pierden más materias.")
                print(f"     ¿Es causa o consecuencia? Probablemente CONSECUENCIA.")
                print(f"     Razón: Un desertor naturalmente pierden más materias.")
            
            elif feature == "asistencia_clases":
                print(f"\n  🚨 SOSPECHA: Desertores tienen peor asistencia.")
                print(f"     ¿Es causa o consecuencia? Ambas (causal), pero...")
                print(f"     Razón: Puede medirse ANTES de desertar.")
            
            elif feature == "promedio_academico":
                print(f"\n  ✅ Posible feature CAUSAL (bueno).")
                print(f"     Razón: Disponible antes de desertar.")
            
            elif feature == "mora_matricula":
                print(f"\n  🚨 SOSPECHA: Desertores tienen más mora.")
                print(f"     ¿Es causa o consecuencia? Probablemente CONSECUENCIA.")
                print(f"     Razón: Estudiantes que desertan dejan de pagar.")
            
            elif feature == "casos_riesgo":
                print(f"\n  🚨 SOSPECHA: Variable de riesgo vs target.")
                print(f"     Revisar si es redundante con target.")
        
        except Exception as e:
            print(f"  Error: {e}")
    
    # Análisis de distribuciones
    print("\n" + "-"*70)
    print("📊 DISTRIBUCIONES DETALLADAS:")
    print("-"*70)
    
    for feature in ["materias_perdidas", "asistencia_clases", "promedio_academico"]:
        if feature not in df.columns:
            continue
        
        print(f"\n{feature}:")
        
        try:
            desertor_vals = pd.to_numeric(desertores[feature], errors='coerce')
            no_desertor_vals = pd.to_numeric(no_desertores[feature], errors='coerce')
            
            print(f"  Desertores:")
            print(f"    Min: {desertor_vals.min():.2f}, Max: {desertor_vals.max():.2f}")
            print(f"    Q1: {desertor_vals.quantile(0.25):.2f}, Q3: {desertor_vals.quantile(0.75):.2f}")
            
            print(f"  No Desertores:")
            print(f"    Min: {no_desertor_vals.min():.2f}, Max: {no_desertor_vals.max():.2f}")
            print(f"    Q1: {no_desertor_vals.quantile(0.25):.2f}, Q3: {no_desertor_vals.quantile(0.75):.2f}")
        except:
            pass
    
    # Recomendaciones
    print("\n" + "="*70)
    print("✅ RECOMENDACIONES PARA EVITAR MEMORIZACIÓN:")
    print("="*70)
    print("""
1. ELIMINAR features CONSECUENCIALES:
   ❌ materias_perdidas (solo aparece DESPUÉS de desertar)
   ❌ mora_matricula (solo aparece DESPUÉS de desertar)
   
2. MANTENER features CAUSALES:
   ✅ promedio_academico (disponible ANTES)
   ✅ asistencia_clases (disponible ANTES)
   ✅ horas_trabajo_semanales (disponible ANTES)
   ✅ ingresos_familiares (disponible ANTES)
   ✅ estrato (disponible ANTES)
   
3. REVISAR:
   ⚠️  casos_riesgo (¿cómo se calcula?)
   ⚠️  rendimiento_periodo (¿qué período?)

4. SEPARACIÓN TEMPORAL:
   Usar SOLO features del semestre anterior para predecir deserción actual.
""")
    print("="*70 + "\n")


if __name__ == "__main__":
    analyze_feature_causality()
