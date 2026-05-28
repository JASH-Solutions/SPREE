import os
import numpy as np
import pandas as pd

N = 500
SEED = 42
OUTPUT_FILE = "well-being.csv"

rng = np.random.default_rng(SEED)

# Deserción común
desertion_bool = np.zeros(N, dtype=bool)
desertion_bool[:150] = True
rng.shuffle(desertion_bool)

ids = [f"EST-{i+1:04d}" for i in range(N)]

atenciones = []
seguimientos = []
casos_riesgo = []

for i in range(N):
    des = desertion_bool[i]

    # Atenciones psicológicas
    lam = 1.2 if des else 0.3
    atenc = rng.poisson(lam)
    atenciones.append(atenc)

    # Seguimientos realizados
    lam_seg = 2.0 if des else 0.5
    seg = rng.poisson(lam_seg)
    seguimientos.append(seg)

    # Casos de riesgo registrados
    prob_caso = 0.6 if des else 0.1
    caso = rng.random() < prob_caso
    casos_riesgo.append(caso)

df = pd.DataFrame({
    "id_estudiante": ids,
    "atenciones_psicologicas": atenciones,
    "seguimientos_realizados": seguimientos,
    "casos_riesgo": casos_riesgo
})

# Guardar CSV en data/raw
import os
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)
df.to_csv(os.path.join(OUTPUT_DIR, OUTPUT_FILE), index=False, encoding="utf-8")
print(f"Archivo generado: {OUTPUT_FILE}")