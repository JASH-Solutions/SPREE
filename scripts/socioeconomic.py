import os
import numpy as np
import pandas as pd

N = 500
SEED = 42
OUTPUT_FILE = "socioeconomic.csv"

rng = np.random.default_rng(SEED)

# Deserción común
desertion_bool = np.zeros(N, dtype=bool)
desertion_bool[:150] = True
rng.shuffle(desertion_bool)

ids = [f"EST-{i+1:04d}" for i in range(N)]

estrato = []
ingresos = []
dependientes = []
sit_laboral = []
horas_trabajo = []
lugar_res = []
tipo_vivienda = []

for i in range(N):
    des = desertion_bool[i]

    # Estrato (1-6)
    if des:
        p_est = [0.25, 0.30, 0.25, 0.10, 0.07, 0.03]
    else:
        p_est = [0.10, 0.20, 0.30, 0.25, 0.10, 0.05]
    estr = rng.choice([1,2,3,4,5,6], p=p_est)
    estrato.append(estr)

    # Ingresos familiares (COP)
    mean_log = np.log(1_200_000) if des else np.log(2_000_000)
    ing = np.exp(rng.normal(mean_log, 0.5))
    ingresos.append(round(ing, -3))  # redondeo a miles

    # Número de dependientes
    lam = 3 if des else 2
    dep = rng.poisson(lam) + 1  # al menos 1
    dependientes.append(dep)

    # Situación laboral
    if des:
        sit = rng.choice(["No trabaja", "Medio tiempo", "Tiempo completo"], p=[0.2, 0.3, 0.5])
    else:
        sit = rng.choice(["No trabaja", "Medio tiempo", "Tiempo completo"], p=[0.4, 0.35, 0.25])
    sit_laboral.append(sit)

    # Horas de trabajo semanales
    if sit == "No trabaja":
        horas = 0
    elif sit == "Medio tiempo":
        horas = int(rng.normal(20, 5))
        horas = max(10, min(30, horas))
    else:
        horas = int(rng.normal(40, 8))
        horas = max(30, min(50, horas))
    horas_trabajo.append(horas)

    # Lugar de residencia
    if des:
        lugar = rng.choice(["Misma ciudad", "Ciudad cercana", "Ciudad lejana"], p=[0.3, 0.3, 0.4])
    else:
        lugar = rng.choice(["Misma ciudad", "Ciudad cercana", "Ciudad lejana"], p=[0.6, 0.25, 0.15])
    lugar_res.append(lugar)

    # Tipo de vivienda
    if des:
        viv = rng.choice(["Propia", "Arrendada", "Familiar"], p=[0.2, 0.5, 0.3])
    else:
        viv = rng.choice(["Propia", "Arrendada", "Familiar"], p=[0.4, 0.4, 0.2])
    tipo_vivienda.append(viv)

df = pd.DataFrame({
    "id_estudiante": ids,
    "estrato": estrato,
    "ingresos_familiares": ingresos,
    "num_dependientes": dependientes,
    "situacion_laboral": sit_laboral,
    "horas_trabajo_semanales": horas_trabajo,
    "lugar_residencia": lugar_res,
    "tipo_vivienda": tipo_vivienda
})

# Guardar CSV en data/raw
import os
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)
df.to_csv(os.path.join(OUTPUT_DIR, OUTPUT_FILE), index=False, encoding="utf-8")
print(f"Archivo generado: {OUTPUT_FILE}")