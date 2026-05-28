# SPREE: Sistema de Predicción de Riesgo de Deserción Estudiantil

**Sistema de alerta temprana impulsado por Machine Learning para predecir y prevenir la deserción estudiantil.**

## Inicio Rápido

### 1. Generar Dataset (primera vez)

```bash
# Desde la raíz del proyecto
python data/generators/generate_dataset.py
```

Esto ejecuta secuencialmente 10 scripts para simular datos:
* `personal.py` — Datos personales de estudiantes
* `academics.py` — Historial académico
* `financial.py` — Información financiera
* `socioeconomic.py` — Datos socioeconómicos
* `demographic.py` — Datos demográficos
* `well-being.py` — Bienestar estudiantil
* `additional.py` — Características adicionales
* `merge_datasets.py` — Fusionar todas las fuentes
* `preprocess_dataset.py` — Normalizar y limpiar
* `intervention_labeler.py` — Generar variable objetivo (deserción)

Salida: `data/raw/` (archivos CSV intermedios) → `data/processed/students.csv`

### 2. Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

En el primer inicio, el modelo se entrenará (~1.0 s). Ejecuciones posteriores cargarán desde caché (~0.02 s).

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

## El Modelo

**Clasificador RandomForest** que predice la probabilidad de deserción utilizando 6 características causales.

* **F1-Score**: 0.76 | **Recall**: 86% | **ROC-AUC**: 0.94
* **Datos**: 500 estudiantes (22 desertores, 478 no desertores)
* **Entrenamiento**: 70% entrenamiento / 15% validación / 15% prueba con validación cruzada estratificada de 5 particiones
* **Rendimiento**: Detecta 19 de 22 estudiantes en riesgo, con 9 falsas alarmas

## Arquitectura

### Backend (FastAPI)

* **app/ml/**: Entrenamiento, persistencia y evaluación del modelo
* **app/controllers/**: Endpoints de la API para predicciones y métricas
* **app/services/**: Lógica de negocio
* **models/**: Almacenamiento persistente del modelo (.joblib + metadatos JSON)

### Característica Principal

**Persistencia del Modelo**: El primer inicio entrena el modelo en 1.0 s; las ejecuciones posteriores cargan el modelo en caché en 0.02 s (50 veces más rápido).

## Características Causales

Solo se utilizan características disponibles **antes** de que ocurra la deserción estudiantil:

* `promedio_academico` — Promedio académico (GPA)
* `asistencia_clases` — Porcentaje de asistencia a clases
* `horas_trabajo_semanales` — Horas de trabajo por semana
* `ingresos_familiares` — Ingresos familiares
* `estrato` — Nivel socioeconómico
* `rendimiento_periodo` — Rendimiento del período

Se eliminó el *data leakage* excluyendo características consecuenciales (`materias_perdidas`, `mora_matricula`, `casos_riesgo`).

## Endpoints de la API

```text
GET /api/students                          → Todos los estudiantes
GET /api/students/{id}                     → Estudiante + predicción de riesgo
GET /api/risk/{id}                         → Solo predicción de riesgo
GET /api/model/metrics                     → Rendimiento actual del modelo
GET /api/model/versions                    → Historial de versiones del modelo
GET /api/model/info                        → Metadatos del modelo
```

## Niveles de Riesgo

```text
Probabilidad     Nivel de Riesgo    Acción
0.0 - 0.33       Bajo               Monitoreo
0.33 - 0.66      Medio              Acompañamiento
0.66 - 1.0       Alto               Intervención
```

## Datos

* Dataset: `students.csv` (500 registros, 39 características)
* Ruta predeterminada: `./students.csv`
* Personalización: variable de entorno `SPREE_DATA_PATH`

## Documentación

**Detalles técnicos completos**: Ver [MODEL_SYSTEM.md](MODEL_SYSTEM.md)

* Algoritmo del modelo y métricas de rendimiento
* Pipeline de datos y preprocesamiento
* Arquitectura del sistema
* Proceso de entrenamiento
* Guía de despliegue

## Estructura del Proyecto

```text
SPREE/
├── backend/
│   ├── app/ml/                    → Pipeline de ML
│   ├── app/controllers/           → Endpoints de la API
│   ├── app/services/              → Lógica de negocio
│   ├── models/                    → Modelos y métricas guardadas
│   ├── main.py                    → Aplicación FastAPI
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── data/
│   ├── raw/                       → Archivos CSV fuente
│   └── processed/                 → Dataset consolidado
├── README.md                      → Este archivo
└── MODEL_SYSTEM.md                → Documentación técnica
```
