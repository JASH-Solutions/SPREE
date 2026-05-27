import pandas as pd
from pathlib import Path

from sklearn.preprocessing import StandardScaler

# Directorios
PROCESSED_DIR = Path("data/processed")

INPUT_FILE = PROCESSED_DIR / "students.csv"
OUTPUT_FILE = PROCESSED_DIR / "students_preprocessed.csv"

# =========================
# Cargar dataset
# =========================

df = pd.read_csv(INPUT_FILE)

print("Dataset cargado correctamente.")
print(f"Registros: {len(df)}")
print(f"Columnas: {len(df.columns)}")

# =========================
# Eliminar duplicados
# =========================

df.drop_duplicates(inplace=True)

# =========================
# Manejo básico de nulos
# =========================

# Numéricos → media
numeric_columns = df.select_dtypes(include=["int64", "float64"]).columns

for col in numeric_columns:
    df[col] = df[col].fillna(df[col].mean())

# Categóricos → moda
categorical_columns = df.select_dtypes(include=["object"]).columns

for col in categorical_columns:
    df[col] = df[col].fillna(df[col].mode()[0])

# =========================
# Guardar id_estudiante aparte
# =========================

student_ids = df["id_estudiante"]

# =========================
# Encoding variables categóricas
# =========================

df_encoded = pd.get_dummies(
    df,
    drop_first=True
)

# =========================
# Escalado variables numéricas
# =========================

scaler = StandardScaler()

scaled_columns = df_encoded.select_dtypes(
    include=["int64", "float64"]
).columns

df_encoded[scaled_columns] = scaler.fit_transform(
    df_encoded[scaled_columns]
)

# =========================
# Restaurar IDs
# =========================

df_encoded["id_estudiante"] = student_ids

# =========================
# Guardar dataset procesado
# =========================

df_encoded.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8"
)

print("\nPreprocesamiento completado.")
print(f"Archivo generado: {OUTPUT_FILE}")
print(f"Columnas finales: {len(df_encoded.columns)}")