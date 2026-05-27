import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

FILES = [
    "personal.csv",
    "academics.csv",
    "financial.csv",
    "socioeconomic.csv",
    "demographic.csv",
    "well-being.csv",
    "additional.csv"
]

df_master = None

for file in FILES:

    path = RAW_DIR / file

    if not path.exists():
        print(f"Archivo no encontrado: {file}")
        continue

    df_temp = pd.read_csv(path)

    if "id_estudiante" not in df_temp.columns:
        print(f"{file} no contiene id_estudiante")
        continue

    if df_master is None:
        df_master = df_temp
    else:
        df_master = df_master.merge(
            df_temp,
            on="id_estudiante",
            how="inner"
        )

output_path = PROCESSED_DIR / "students.csv"

df_master.to_csv(output_path, index=False)

print(f"\nDataset consolidado generado:")
print(output_path)

print(f"\nRegistros: {len(df_master)}")
print(f"Columnas: {len(df_master.columns)}")