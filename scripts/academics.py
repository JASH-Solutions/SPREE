import os
import numpy as np
import pandas as pd

# Configuración
OUTPUT_FILE = "academics.csv"

N = 500
SEED = 42

rng = np.random.default_rng(SEED)

# Generar vector de deserción común a todos los scripts
desertion_bool = np.zeros(N, dtype=bool)
desertion_bool[:150] = True         # exactamente 30%
rng.shuffle(desertion_bool)

ids = [f"EST-{i+1:04d}" for i in range(N)]

# Variables a llenar
promedio = []
historial_list = []
materias_perdidas = []
semestres = []
creditos_mat = []
creditos_aprob = []
asistencia = []
rendimiento = []

for i in range(N):
    desertor = desertion_bool[i]

    # Semestre cursado
    if desertor:
        probs = [0.25, 0.25, 0.20, 0.10, 0.05, 0.05, 0.04, 0.03, 0.02, 0.01]
    else:
        probs = [0.15, 0.15, 0.12, 0.12, 0.10, 0.10, 0.08, 0.08, 0.05, 0.05]
    sem = rng.choice(np.arange(1, 20), p=probs)
    semestres.append(sem)

    # Capacidad académica latente
    ability = rng.normal(-0.5 if desertor else 0.0, 0.3)

    # Historial de notas (por semestre)
    grades = []
    for t in range(1, sem + 1):
        gpa_t = 4.0 - 0.05 * (t - 1) + ability + rng.normal(0, 0.15)
        gpa_t = max(2.0, min(5.0, gpa_t))
        grades.append(round(gpa_t, 2))
    # Promedio acumulado
    prom = round(np.mean(grades), 2) if grades else 0.0
    promedio.append(prom)
    # Guardar historial como string separado por ";"
    historial_list.append(";".join(f"{g:.2f}" for g in grades))

    # Materias perdidas (relacionado con promedio y deserción)
    mat_perd = max(0, int(round(3 * (4.5 - prom) + 2 * desertor + rng.normal(0, 0.5))))
    materias_perdidas.append(mat_perd)

    # Créditos matriculados
    cred_mat = 16 - 3 * desertor + 0.5 * sem + rng.normal(0, 2)
    cred_mat = max(6, min(24, int(round(cred_mat))))
    creditos_mat.append(cred_mat)

    # Créditos aprobados (no puede superar matriculados)
    cred_aprob = cred_mat - 3 * mat_perd + rng.integers(-2, 3)
    cred_aprob = max(0, min(cred_mat, cred_aprob))
    creditos_aprob.append(cred_aprob)

    # Asistencia (%)
    asist = 85 - 20 * desertor + rng.normal(0, 10)
    asist = max(0, min(100, round(asist)))
    asistencia.append(asist)

    # Rendimiento por período (diferencia último - penúltimo semestre)
    if sem >= 2:
        diff = grades[-1] - grades[-2]
    else:
        diff = 0.0
    rendimiento.append(round(diff, 2))

# Crear DataFrame y exportar
df = pd.DataFrame({
    "id_estudiante": ids,
    "promedio_academico": promedio,
    "historial_notas": historial_list,
    "materias_perdidas": materias_perdidas,
    "semestre_cursado": semestres,
    "creditos_matriculados": creditos_mat,
    "creditos_aprobados": creditos_aprob,
    "asistencia_clases": asistencia,
    "rendimiento_periodo": rendimiento
})

# Guardar CSV en data/raw
import os
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)
df.to_csv(os.path.join(OUTPUT_DIR, OUTPUT_FILE), index=False, encoding="utf-8")
print(f"Archivo generado: {OUTPUT_FILE}")