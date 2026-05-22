# Requisitos previos

Antes de ejecutar el proyecto, asegúrese de tener instalado:

- Python 3.12+
- Node.js LTS
- Git

Verificar instalaciones:

```bash
python --version
node --version
npm --version
git --version
```

# SPREE-2026
Sistema Predictivo de Retención Estudiantil


## Descripción
SPREE es una plataforma basada en Machine Learning orientada a la detección temprana de riesgo de deserción estudiantil.

## Tecnologías
- Python 3.12 LTS (a la fecha)
- FastAPI
- React + Vite
- Azure
- Power BI

## Estructura del proyecto
El proyecto tiene la siguiente estructura:
SPREE-2026/
│
├── app/
│   ├── api/
│   ├── services/
│   ├── models/
│   ├── utils/
│   └── main.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
│
├── notebooks/
│   ├── exploratory/
│   └── modeling/
│
├── models/
│   ├── trained/
│   └── artifacts/
│
├── docs/
│   └── architecture/
│
├── tests/
├── venv/
|
├── .gitignore
├── README.md
├── requirements.txt
└── requirements-dev.txt

Explicación breve de carpetas.

| Carpeta             | Propósito                   |
| ------------------- | --------------------------- |
| `/app`              | Backend y lógica principal  |
| `/data/raw`         | Datos originales            |
| `/data/processed`   | Datos limpios               |
| `/data/external`    | Archivos externos           |
| `/notebooks`        | Experimentación ML          |
| `/models/trained`   | Modelos entrenados          |
| `/models/artifacts` | Encoders, scalers, métricas |
| `/docs`             | Diagramas y documentación   |
| `/tests`            | Pruebas                     |


## Instalación



### 1. Clonar el repositorio

```bash
git clone https://github.com/usuario/SPREE-2026.git
```

### 2. Ingresar al proyecto

```bash
cd SPREE-2026
```

### 3. Crear entorno virtual

```bash
python -m venv venv
```

### 4. Activar entorno virtual

#### Windows

```bash
venv\Scripts\activate
```

### Linux / Mac

```bash
source venv/bin/activate
```


### Crear entorno virtual
python -m venv venv


### Activar entorno
venv\Scripts\activate

### Instalar dependencias
pip install -r requirements.txt


## Verificar instalación

```bash
pip list
```

## Ejecutar aplicación (FastAPI)

```bash
uvicorn app.main:app --reload
```

La API estará disponible en:

```txt
http://127.0.0.1:8000
```

Documentación automática Swagger:

```txt
http://127.0.0.1:8000/docs
```

## Equipo
JASH Solutions