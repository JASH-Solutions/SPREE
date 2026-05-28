# SPREE Backend

FastAPI backend with layered architecture (controllers, services, repositories, ml).

## Setup

```bash
pip install -r backend/requirements.txt
```

## Run

```bash
uvicorn backend.main:app --reload
```

## Notes

- Dataset path defaults to ./students.csv
- Override with SPREE_DATA_PATH if needed
- CORS origins can be set with SPREE_CORS_ORIGINS (comma-separated)
