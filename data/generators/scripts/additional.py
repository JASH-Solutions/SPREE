import os
import numpy as np
import pandas as pd

N = 500
SEED = 42
OUTPUT_FILE = "additional.csv"

rng = np.random.default_rng(SEED)

# Deserción común
desertion_bool = np.zeros(N, dtype=bool)
desertion_bool[:150] = True
rng.shuffle(desertion_bool)

ids = [f"EST-{i+1:04d}" for i in range(N)]

participacion = []
evaluacion = []

for i in range(N):
    des = desertion_bool[i]

    # Participación institucional (número de actividades)
    lam = 0.8 if des else 2.0
    part = rng.poisson(lam)
    participacion.append(part)

    # Evaluación docente (1-5)
    media = 3.8 if des else 4.2
    nota = rng.normal(media, 0.4)
    nota = max(1.0, min(5.0, round(nota, 1)))
    evaluacion.append(nota)

df = pd.DataFrame({
    "id_estudiante": ids,
    "participacion_institucional": participacion,
    "evaluacion_docente": evaluacion
})

# Guardar CSV en data/raw
import os
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)
df.to_csv(os.path.join(OUTPUT_DIR, OUTPUT_FILE), index=False, encoding="utf-8")
print(f"Archivo generado: {OUTPUT_FILE}")