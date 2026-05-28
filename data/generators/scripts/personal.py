import numpy as np
import pandas as pd
from faker import Faker
from datetime import date, timedelta

# Configuración
N = 500
SEED = 42
REFERENCE_DATE = date(2024, 8, 1)  # fecha de referencia para calcular la edad
OUTPUT_FILE = "personal.csv"

# RNG para replicar exactamente las edades de demograficos.py
rng = np.random.default_rng(SEED)

# Deserción común (misma lógica que en los otros scripts)
desertion_bool = np.zeros(N, dtype=bool)
desertion_bool[:150] = True
rng.shuffle(desertion_bool)

# IDs y listas
ids = [f"EST-{i+1:04d}" for i in range(N)]
edades = []

# 1. Replicar la generación de edad de demograficos.py
for i in range(N):
    des = desertion_bool[i]
    if des:
        edad = int(rng.normal(23, 4))
    else:
        edad = int(rng.normal(21, 3))
    edad = max(16, min(35, edad))
    edades.append(edad)

# 2. Configurar Faker para el resto de campos
fake = Faker('es_CO')
Faker.seed(SEED + 100)  # semilla diferente para no interferir con el RNG de numpy

# Listas finales
primer_nombre = []
segundo_nombre = []
primer_apellido = []
segundo_apellido = []
tipo_doc = []
num_doc = []
correo = []
telefono = []
direccion = []
fecha_nacimiento = []

for i in range(N):
    # -- Nombre y apellidos --
    p_nombre = fake.first_name()
    # Segundo nombre (algunos lo tienen, probabilidad 0.6)
    s_nombre = fake.first_name() if np.random.rand() < 0.6 else ""
    p_apellido = fake.last_name()
    # Segundo apellido (probabilidad 0.7)
    s_apellido = fake.last_name() if np.random.rand() < 0.7 else ""

    primer_nombre.append(p_nombre)
    segundo_nombre.append(s_nombre)
    primer_apellido.append(p_apellido)
    segundo_apellido.append(s_apellido)

    # -- Documento --
    # Los menores de 18 pueden tener tarjeta de identidad (TI), el resto CC
    if edades[i] < 18 and np.random.rand() < 0.3:
        tipo = "TI"
    else:
        tipo = "CC"
    tipo_doc.append(tipo)
    # Número de documento único (8-10 dígitos)
    num_doc.append(str(fake.unique.random_number(digits=10, fix_len=True)))

    # -- Correo electrónico basado en nombre --
    # ejemplo: juan.perez@email.com
    user = f"{p_nombre.lower()}.{p_apellido.lower().replace(' ', '')}"
    correo.append(f"{user}{np.random.randint(0,99)}@email.com")

    # -- Teléfono celular --
    telefono.append(fake.phone_number())

    # -- Dirección en Colombia --
    direccion.append(fake.address().replace('\n', ', '))

    # -- Fecha de nacimiento consistente con la edad --
    edad_actual = edades[i]
    # El estudiante nació entre (REFERENCE_DATE - edad años - 1 año) y (REFERENCE_DATE - edad años)
    inicio_ventana = REFERENCE_DATE.replace(year=REFERENCE_DATE.year - edad_actual - 1)
    fin_ventana = REFERENCE_DATE.replace(year=REFERENCE_DATE.year - edad_actual)
    # días aleatorios dentro del período
    dias_aleatorios = np.random.randint(0, 365)
    nacimiento = inicio_ventana + timedelta(days=dias_aleatorios)
    # Ajuste para que realmente tenga la edad correcta en la fecha de referencia
    if (REFERENCE_DATE - nacimiento).days // 365 != edad_actual:
        # corregir al día exacto
        dias_necesarios = edad_actual * 365
        nacimiento = REFERENCE_DATE - timedelta(days=dias_necesarios)
    fecha_nacimiento.append(nacimiento.isoformat())

# Crear DataFrame
df = pd.DataFrame({
    "id_estudiante": ids,
    "primer_nombre": primer_nombre,
    "segundo_nombre": segundo_nombre,
    "primer_apellido": primer_apellido,
    "segundo_apellido": segundo_apellido,
    "tipo_documento": tipo_doc,
    "numero_documento": num_doc,
    "correo_electronico": correo,
    "telefono": telefono,
    "direccion": direccion,
    "fecha_nacimiento": fecha_nacimiento
})

# Guardar CSV en data/raw
import os
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)
df.to_csv(os.path.join(OUTPUT_DIR, OUTPUT_FILE), index=False, encoding="utf-8")
print(f"Archivo generado: {OUTPUT_FILE}")