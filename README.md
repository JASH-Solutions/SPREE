# SPREE MVP

SPREE is split into a dedicated backend and frontend for the MVP.

## Structure

- backend/ FastAPI API with layered architecture
- frontend/ React dashboard (Vite)

## Backend setup

```bash
pip install -r backend/requirements.txt
```

```bash
uvicorn backend.main:app --reload
```

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

## Data

- Dataset path defaults to ./students.csv
- Override with SPREE_DATA_PATH if needed
