# SPREE: Modelo y Arquitectura del Sistema

## Descripción General

**SPREE** predice el riesgo de deserción estudiantil utilizando únicamente características causales (sin *data leakage*). El modelo se ejecuta sobre un backend en FastAPI con persistencia y monitoreo del modelo.

## El Modelo

### Algoritmo

* **RandomForestClassifier** (150 árboles)
* **Salida**: Probabilidad de deserción (0-1)
* **Umbral de decisión**: 0.5 → Nivel de riesgo (Bajo/Medio/Alto)

### Rendimiento

* **F1-Score**: 0.76 (balance entre precisión y recall)
* **Recall**: 86% (detecta 19 de 22 estudiantes en riesgo)
* **Precision**: 68% (9 falsos positivos de 28 predicciones)
* **ROC-AUC**: 0.94 (excelente capacidad de discriminación)
* **Accuracy**: 84%

### Datos de Entrenamiento

* **Registros totales**: 500 estudiantes
* **Desertores**: 22 (4.4%)
* **No desertores**: 478 (95.6%)
* **División**: 70% entrenamiento / 15% validación / 15% prueba

## Características (Solo Causales)

Se utilizan seis características causales disponibles **antes** de que ocurra la deserción estudiantil:

| Característica          | Tipo       | Descripción                     |
| ----------------------- | ---------- | ------------------------------- |
| promedio_academico      | Numérica   | Promedio académico (escala 0-5) |
| asistencia_clases       | Numérica   | Porcentaje de asistencia        |
| horas_trabajo_semanales | Numérica   | Horas de trabajo por semana     |
| ingresos_familiares     | Numérica   | Nivel de ingresos familiares    |
| estrato                 | Categórica | Estrato socioeconómico (1-6)    |
| rendimiento_periodo     | Numérica   | Rendimiento del período         |

**¿Por qué solo estas?** Se excluyeron características con *data leakage*:

* `materias_perdidas` — Solo se conoce DESPUÉS de la deserción
* `mora_matricula` — Solo se conoce DESPUÉS de la deserción
* `casos_riesgo` — Es consecuencia de la deserción, no una causa

## Arquitectura del Sistema

### Backend (FastAPI)

```text id="4h5n2j"
backend/
├── app/ml/
│   ├── train_clean_model.py       → Entrena RF con características causales
│   ├── hyperparameter_tuning.py   → GridSearchCV (120 combinaciones de parámetros)
│   ├── model_persister.py         → Guarda/carga modelos en disco
│   ├── metrics.py                 → Calcula todas las métricas de ML
│   └── risk_model.py              → Modelo original + evaluación
├── app/controllers/
│   ├── model_controller.py        → /api/model/metrics, /api/model/versions
│   ├── risk_controller.py         → /api/risk/{student_id}
│   └── ...
├── models/                        → Almacenamiento persistente de modelos
│   ├── model_v*.joblib            → Pipeline serializado de sklearn
│   ├── model_v*_metrics.json      → Métricas de rendimiento por versión
│   └── model_registry.json        → Índice de todos los modelos
└── main.py                        → Punto de entrada de la aplicación FastAPI
```

### Persistencia del Modelo

**Problema**: Reentrenar el modelo tarda ~1 segundo en cada inicio.
**Solución**: Guardar modelos entrenados en disco y cargarlos en 0.02 segundos.

**Flujo**:

1. Primer inicio → Entrenar y guardar (1.0 s)
2. Inicios posteriores → Cargar modelo en caché (0.02 s)
3. **Aceleración**: 50 veces más rápido

**Almacenamiento**:

* Pipeline de sklearn → binario `.joblib`
* Métricas → metadatos `.json`
* Registro → índice JSON de versiones

**Selección del modelo**: Siempre se carga la versión más reciente (orden descendente por timestamp)

### Endpoints de la API

```text id="9zprx2"
GET /api/students                      → Todos los estudiantes
GET /api/students/{id}                 → Estudiante individual + predicción de riesgo
GET /api/risk/{id}                     → Solo predicción de riesgo

GET /api/model/metrics                 → F1, Recall, ROC-AUC y Accuracy del modelo actual
GET /api/model/versions                → Lista de todos los modelos entrenados
GET /api/model/info                    → Metadatos completos del modelo
```

## Pipeline de Datos

### Fuente

7 archivos CSV en `data/raw/`:

* personal.csv
* academics.csv
* financial.csv
* socioeconomic.csv
* demographic.csv
* well-being.csv
* additional.csv

### Procesamiento

1. **Merge** de 7 archivos por ID de estudiante → `students.csv` (500 registros, 39 características)
2. **Preprocesamiento**:

   * Numéricas: `StandardScaler` (ajustado sobre entrenamiento y aplicado a prueba)
   * Categóricas: `OneHotEncoder`
   * Valores faltantes: imputación por mediana (numéricas) y valor más frecuente (categóricas)
3. **Etiqueta**: `estado_estudiante` → 1 = desertor, 0 = no desertor

## Entrenamiento del Modelo

### Ciclo de Entrenamiento

```python id="d6u4m0"
trainer = CleanModelTrainer(df)           # Inicializar
metrics = trainer.train()                 # Entrenar y evaluar

# Internamente:
# 1. _prepare_data()    → División 70/15/15
# 2. _build_pipeline()  → Preprocesamiento + clasificador RF
# 3. train()            → Ajustar pipeline, validación cruzada y evaluación
```

### Optimización de Hiperparámetros

GridSearchCV probó 120 combinaciones:

* n_estimators: [100, 150, 200]
* max_depth: [8, 10, 12]
* min_samples_leaf: [3, 4, 5]
* min_samples_split: [5, 10]
* class_weight: ["balanced", "balanced_subsample"]

**Resultado**: Mejores parámetros = `n_estimators=150, max_depth=8, min_samples_leaf=4`

## Niveles de Riesgo

El modelo convierte la probabilidad en niveles de riesgo accionables:

```text id="c93i9v"
Probabilidad    Nivel de Riesgo    Acción
[0.0 - 0.33)    Bajo               No se requiere acción
[0.33 - 0.66)   Medio              Monitorear y ofrecer apoyo
[0.66 - 1.0]    Alto               Intervención urgente
```

## Explicación de Métricas

| Métrica       | Fórmula                | Significado                                                   |
| ------------- | ---------------------- | ------------------------------------------------------------- |
| **F1-Score**  | 2×(P×R)/(P+R)          | Balance entre precisión y recall                              |
| **Recall**    | TP/(TP+FN)             | % de desertores reales detectados                             |
| **Precision** | TP/(TP+FP)             | % de desertores predichos correctamente                       |
| **ROC-AUC**   | Área bajo la curva ROC | Capacidad de discriminación (0.5 = aleatorio, 1.0 = perfecto) |
| **Accuracy**  | (TP+TN)/(TP+TN+FP+FN)  | Exactitud general                                             |

**Matriz de Confusión (Conjunto de Prueba - 75 estudiantes)**:

```text id="0zjlwm"
                Predicción
              Desertor | No Desertor
Real   Desertor       19  |     3        (22 total)
       No Desertor     9  |    44        (53 total)
```

* TP = 19: Desertores identificados correctamente
* FP = 9: No desertores marcados incorrectamente (falsas alarmas)
* TN = 44: No desertores identificados correctamente
* FN = 3: Desertores no detectados

## Validación Cruzada

La validación cruzada estratificada de 5 particiones garantiza:

* Cada partición mantiene la misma distribución de clases (22 desertores distribuidos en todos los folds)
* Múltiples evaluaciones con diferentes divisiones de datos
* Métrica de estabilidad: F1 = 0.8565 ± 0.0291 (consistente)

## Despliegue

### Requisitos

* Python 3.x
* scikit-learn, pandas, numpy, joblib (ML)
* FastAPI, uvicorn (API)

### Iniciar Backend

```bash id="ovq3w8"
cd backend
python -m uvicorn main:app --reload
```

### Primera Ejecución

* Carga datos (500 estudiantes)
* Entrena el modelo (~1.0 s)
* Guarda el modelo en disco
* Disponible en http://127.0.0.1:8000

### Ejecuciones Posteriores

* Carga el modelo en caché (0.02 s)
* Mismas predicciones, mucho más rápido

## Mejoras Futuras

1. **Optimización del umbral** — Encontrar el mejor límite de decisión para reducir falsos positivos
2. **SMOTE** — Manejar el desbalance de clases (4.4%) mediante sobremuestreo sintético
3. **Feature engineering** — Crear características de interacción (ej. asistencia × promedio)
4. **Monitoreo** — Detectar deriva del modelo, registrar predicciones y alertar degradaciones
5. **Modelos alternativos** — Probar XGBoost y LightGBM para un mejor manejo del desbalance
