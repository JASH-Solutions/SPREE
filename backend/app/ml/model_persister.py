"""
Módulo de persistencia de modelos ML.

Maneja serialización, versionado y carga de modelos entrenados.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

import joblib
import pandas as pd
import numpy as np

from .train_clean_model import CleanModelTrainer
from .metrics import ModelMetrics, calculate_metrics


logger = logging.getLogger("spree.model_persister")

# Rutas
MODELS_DIR = Path(__file__).parent.parent.parent / "models"
REGISTRY_FILE = MODELS_DIR / "model_registry.json"


class ModelRegistry:
    """Registro de modelos entrenados."""
    
    def __init__(self, registry_path: Path = REGISTRY_FILE):
        self.registry_path = registry_path
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self._load_registry()
    
    def _load_registry(self) -> None:
        """Cargar registro existente."""
        if self.registry_path.exists():
            with open(self.registry_path, "r") as f:
                self.registry = json.load(f)
        else:
            self.registry = {"models": []}
    
    def _save_registry(self) -> None:
        """Guardar registro."""
        with open(self.registry_path, "w") as f:
            json.dump(self.registry, f, indent=2, default=str)
    
    def register(self, model_entry: Dict[str, Any]) -> None:
        """Registrar nuevo modelo."""
        self.registry["models"].append(model_entry)
        self._save_registry()
        logger.info(f"Modelo registrado: {model_entry['version']}")
    
    def get_latest(self) -> Optional[Dict[str, Any]]:
        """Obtener último modelo registrado."""
        if self.registry["models"]:
            return self.registry["models"][-1]
        return None
    
    def get_by_version(self, version: str) -> Optional[Dict[str, Any]]:
        """Obtener modelo por versión."""
        for model in self.registry["models"]:
            if model["version"] == version:
                return model
        return None
    
    def list_all(self) -> list:
        """Listar todos los modelos."""
        return self.registry["models"]


class ModelPersister:
    """Gestor de persistencia de modelos."""
    
    def __init__(self, models_dir: Path = MODELS_DIR):
        self.models_dir = models_dir
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.registry = ModelRegistry()
    
    def train_and_save(
        self,
        df: pd.DataFrame,
        description: str = "Model trained"
    ) -> Dict[str, Any]:
        """
        Entrenar modelo y guardarlo.
        
        Args:
            df: DataFrame con datos
            description: Descripción del modelo
        
        Returns:
            Información del modelo guardado
        """
        logger.info("Iniciando entrenamiento...")
        
        # Entrenar
        trainer = CleanModelTrainer(df)
        test_metrics = trainer.train()
        
        # Generar versión
        version = self._generate_version()
        model_path = self.models_dir / f"{version}.joblib"
        metrics_path = self.models_dir / f"{version}_metrics.json"
        
        # Guardar modelo
        joblib.dump(trainer.pipeline, model_path)
        logger.info(f"Modelo guardado: {model_path}")
        
        # Guardar métricas
        metrics_dict = {
            "test": test_metrics.to_dict(),
            "timestamp": datetime.now().isoformat(),
        }
        
        if trainer.train_metrics:
            metrics_dict["train"] = trainer.train_metrics.to_dict()
        if trainer.val_metrics:
            metrics_dict["val"] = trainer.val_metrics.to_dict()
        
        with open(metrics_path, "w") as f:
            json.dump(metrics_dict, f, indent=2, default=str)
        
        logger.info(f"Métricas guardadas: {metrics_path}")
        
        # Registrar
        model_entry = {
            "version": version,
            "path": str(model_path),
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "f1_score": float(test_metrics.f1_dropouts),
                "recall": float(test_metrics.recall_dropouts),
                "roc_auc": float(test_metrics.roc_auc),
                "accuracy": float(test_metrics.accuracy),
            },
            "test_samples": len(trainer.y_test),
        }
        
        self.registry.register(model_entry)
        
        logger.info(f"✅ Modelo guardado como versión: {version}")
        
        return model_entry
    
    def load_latest(self) -> Optional[Any]:
        """Cargar último modelo entrenado."""
        latest = self.registry.get_latest()
        
        if not latest:
            logger.warning("No se encontró modelo registrado")
            return None
        
        model_path = Path(latest["path"])
        
        if not model_path.exists():
            logger.error(f"Archivo de modelo no encontrado: {model_path}")
            return None
        
        model = joblib.load(model_path)
        logger.info(f"Modelo cargado: {latest['version']}")
        
        return model
    
    def load_by_version(self, version: str) -> Optional[Any]:
        """Cargar modelo por versión."""
        entry = self.registry.get_by_version(version)
        
        if not entry:
            logger.warning(f"Versión no encontrada: {version}")
            return None
        
        model_path = Path(entry["path"])
        
        if not model_path.exists():
            logger.error(f"Archivo de modelo no encontrado: {model_path}")
            return None
        
        model = joblib.load(model_path)
        logger.info(f"Modelo cargado: {version}")
        
        return model
    
    def get_model_info(self, version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Obtener información del modelo."""
        if version:
            return self.registry.get_by_version(version)
        else:
            return self.registry.get_latest()
    
    def list_models(self) -> list:
        """Listar todos los modelos disponibles."""
        models = self.registry.list_all()
        
        result = []
        for model in models:
            result.append({
                "version": model["version"],
                "timestamp": model["timestamp"],
                "f1_score": model["metrics"]["f1_score"],
                "accuracy": model["metrics"]["accuracy"],
                "description": model["description"],
            })
        
        return result
    
    @staticmethod
    def _generate_version() -> str:
        """Generar identificador de versión con timestamp."""
        now = datetime.now()
        return now.strftime("model_v%Y%m%d_%H%M%S")
    
    def load_or_train(
        self,
        df: pd.DataFrame,
        description: str = "Model",
        force_retrain: bool = False
    ) -> Any:
        """
        Cargar modelo si existe, sino entrenar y guardar.
        
        Args:
            df: DataFrame con datos
            description: Descripción si entrena
            force_retrain: Forzar reentrenamiento
        
        Returns:
            Pipeline del modelo
        """
        if not force_retrain:
            model = self.load_latest()
            if model:
                return model
        
        # Entrenar y guardar
        logger.info("No se encontró modelo previo, entrenando...")
        self.train_and_save(df, description)
        
        return self.load_latest()
