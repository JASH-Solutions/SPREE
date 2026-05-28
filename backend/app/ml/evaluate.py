"""
Script de evaluación y entrenamiento del modelo de riesgo.

Uso:
    cd backend
    python evaluate.py
"""
from pathlib import Path
import sys
import logging

# Agregar backend al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd

from app.config import DATA_PATH
from app.repositories.student_repository import StudentRepository
from app.ml.model_trainer import ModelTrainer
from app.ml.metrics import get_classification_report


def main():
    """Ejecutar evaluación completa del modelo."""
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s: %(message)s"
    )
    logger = logging.getLogger("spree.eval")
    
    # Validar datos
    if not DATA_PATH.exists():
        logger.error(f"Dataset not found at {DATA_PATH}")
        sys.exit(1)
    
    logger.info(f"Cargando datos desde {DATA_PATH}")
    repository = StudentRepository(str(DATA_PATH))
    df = repository.data
    
    # Entrenar modelo
    trainer = ModelTrainer(df)
    trainer.train()
    
    # Mostrar métricas
    print(trainer.get_metrics_summary())
    
    # Test metrics detalladas
    if trainer.test_metrics:
        print("\n" + str(trainer.test_metrics))
    
    # Reporte de clasificación en test
    print("\n" + "="*60)
    print("📋 REPORTE DE CLASIFICACIÓN - TEST SET")
    print("="*60)
    y_test_pred = trainer.pipeline.predict(trainer.X_test)
    print(get_classification_report(trainer.y_test, y_test_pred))
    
    logger.info("✅ Evaluación completada")


if __name__ == "__main__":
    main()
