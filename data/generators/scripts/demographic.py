import os
import numpy as np
import pandas as pd
from faker import Faker

N = 500
SEED = 42
OUTPUT_FILE = "demographic.csv"

rng = np.random.default_rng(SEED)

# Deserción común
desertion_bool = np.zeros(N, dtype=bool)
desertion_bool[:150] = True
rng.shuffle(desertion_bool)

ids = [f"EST-{i+1:04d}" for i in range(N)]

# Faker para ciudades (solo en este script)
fake = Faker('es_CO')
Faker.seed(SEED)
# Generar una lista fija de 30 ciudades colombianas (sin Bogotá)
otras_ciudades = [
    "Arequipa", "Trujillo", "Cusco", "Piura", "Chiclayo",
    "Huancayo", "Tacna", "Iquitos", "Pucallpa", "Juliaca",
    "Chimbote", "Ayacucho", "Cajamarca", "Huaraz", "Puno",
    "Tarapoto", "Moquegua", "Tumbes", "Huánuco", "Ica",
    "Sullana", "Abancay", "Cerro de Pasco", "Puerto Maldonado",
    "Bagua", "Jaén", "Moyobamba", "Nazca", "Andahuaylas", "Barranca"
]
# Mezclar con el mismo rng para asignación ordenada
rng.shuffle(otras_ciudades)

edades = []
generos = []
prog_acad = []
ciudad_origen = []
estado = []

for i in range(N):
    des = desertion_bool[i]

    # Edad
    if des:
        edad = int(rng.normal(23, 4))
    else:
        edad = int(rng.normal(21, 3))
    edad = max(16, min(35, edad))
    edades.append(edad)

    # Género (independiente de deserción)
    gen = rng.choice(["Masculino", "Femenino", "Otro"], p=[0.48, 0.48, 0.04])
    generos.append(gen)

    # Programa académico
    prog_acad.append("Ingeniería de Sistemas")

    # Ciudad de origen
    if des:
        es_lima = rng.random() < 0.2
    else:
        es_lima = rng.random() < 0.5
    if es_lima:
        ciudad = "Lima"
    else:
        # Tomar una ciudad de la lista pregenerada (se consume en orden)
        ciudad = otras_ciudades[i % len(otras_ciudades)]
    ciudad_origen.append(ciudad)

    # Estado del estudiante (objetivo)
    estado.append("Desertor" if des else "Activo")

df = pd.DataFrame({
    "id_estudiante": ids,
    "edad": edades,
    "genero": generos,
    "programa_academico": prog_acad,
    "ciudad_origen": ciudad_origen,
    "estado_estudiante": estado
})

# Guardar CSV en data/raw
import os
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)
df.to_csv(os.path.join(OUTPUT_DIR, OUTPUT_FILE), index=False, encoding="utf-8")
print(f"Archivo generado: {OUTPUT_FILE}")