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
# Escalado variables numéricas (Train/Test separado)
# =========================

import numpy as np

# Crear índices para train (70%) y test (30%)
n_samples = len(df_encoded)
np.random.seed(42)
train_idx = np.random.choice(n_samples, size=int(0.7 * n_samples), replace=False)
test_idx = np.setdiff1d(np.arange(n_samples), train_idx)

# Obtener columnas a escalar
scaled_columns = df_encoded.select_dtypes(
    include=["int64", "float64"]
).columns.tolist()

# Crear escalador
scaler = StandardScaler()

# Separar datos
df_train = df_encoded.loc[train_idx].copy()
df_test = df_encoded.loc[test_idx].copy()

# Fit SOLO en train, apply en ambos (EVITA LEAKAGE)
train_scaled = scaler.fit_transform(df_train[scaled_columns])
test_scaled = scaler.transform(df_test[scaled_columns])

# Reemplazar columnas escaladas
df_train[scaled_columns] = train_scaled
df_test[scaled_columns] = test_scaled

# Recombinar
df_encoded = pd.concat([df_train, df_test], axis=0).sort_index()

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