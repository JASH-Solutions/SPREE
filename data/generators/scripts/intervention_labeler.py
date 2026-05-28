import pandas as pd
from pathlib import Path

# Directorios
PROCESSED_DIR = Path("data/processed")

INPUT_FILE = PROCESSED_DIR / "students_preprocessed.csv"
OUTPUT_FILE = PROCESSED_DIR / "students_labeled.csv"

# =========================
# Cargar dataset
# =========================

df = pd.read_csv(INPUT_FILE)

print("Dataset preprocesado cargado.")

# =========================
# Función de recomendación
# =========================

def assign_intervention(row):

    # Riesgo académico
    if (
        row.get("promedio_academico", 0) < 3.0 or
        row.get("materias_perdidas", 0) >= 3
    ):
        return "Tutoria Academica"

    # Riesgo financiero
    if (
        row.get("mora_matricula", 0) == 1 or
        row.get("ingresos_familiares", 99999999) < 1200000
    ):
        return "Apoyo Financiero"

    # Riesgo psicológico
    if (
        row.get("atenciones_psicologicas", 0) > 2 or
        row.get("asistencia", 100) < 60
    ):
        return "Orientacion Psicologica"

    # Sobrecarga laboral
    if (
        row.get("horas_trabajo", 0) > 30 and
        row.get("promedio_academico", 5) < 3.2
    ):
        return "Flexibilizacion Academica"

    # Estudiantes nuevos
    if row.get("semestre", 10) <= 2:
        return "Mentoria Estudiantil"

    # Riesgo bajo
    return "Seguimiento Bienestar"

# =========================
# Aplicar recomendaciones
# =========================

df["recommended_intervention"] = df.apply(
    assign_intervention,
    axis=1
)

# =========================
# Guardar dataset etiquetado
# =========================

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8"
)

print("\nEtiquetado de intervenciones completado.")
print(f"Archivo generado: {OUTPUT_FILE}")

print("\nDistribución de intervenciones:")
print(df["recommended_intervention"].value_counts())