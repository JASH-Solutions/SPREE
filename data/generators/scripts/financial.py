import os
import numpy as np
import pandas as pd

N = 500
SEED = 42
OUTPUT_FILE = "financial.csv"

rng = np.random.default_rng(SEED)

# Vector de deserción común
desertion_bool = np.zeros(N, dtype=bool)
desertion_bool[:150] = True
rng.shuffle(desertion_bool)

ids = [f"EST-{i+1:04d}" for i in range(N)]

estado_pagos = []
mora_matricula = []
becas_apoyos = []

for i in range(N):
    des = desertion_bool[i]

    # Estado de pagos
    if des:
        pagos = rng.choice(["Al día", "En mora", "Pago parcial"], p=[0.3, 0.5, 0.2])
    else:
        pagos = rng.choice(["Al día", "En mora", "Pago parcial"], p=[0.8, 0.1, 0.1])
    estado_pagos.append(pagos)

    # Mora en matrícula (booleano) - Menos diferencia artificial
    prob_mora = 0.4 if des else 0.2
    mora = rng.random() < prob_mora
    mora_matricula.append(mora)

    # Becas o apoyos financieros
    prob_beca = 0.2 if des else 0.4
    beca = "Sí" if rng.random() < prob_beca else "No"
    becas_apoyos.append(beca)

df = pd.DataFrame({
    "id_estudiante": ids,
    "estado_pagos": estado_pagos,
    "mora_matricula": mora_matricula,
    "becas_apoyos": becas_apoyos
})

# Guardar CSV en data/raw
import os
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)
df.to_csv(os.path.join(OUTPUT_DIR, OUTPUT_FILE), index=False, encoding="utf-8")
print(f"Archivo generado: {OUTPUT_FILE}")