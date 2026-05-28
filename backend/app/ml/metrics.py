from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
    roc_curve,
    auc,
)


@dataclass
class ClassMetrics:
    """Métricas para una clase específica."""
    precision: float
    recall: float
    f1: float
    support: int


@dataclass
class ModelMetrics:
    """Métricas completas del modelo."""
    accuracy: float
    precision_macro: float
    recall_macro: float
    f1_macro: float
    roc_auc: float
    
    # Métricas por clase (0: No desertor, 1: Desertor)
    class_0: ClassMetrics
    class_1: ClassMetrics
    
    # Matriz de confusión [TN, FP, FN, TP]
    tn: int
    fp: int
    fn: int
    tp: int
    
    # Métricas específicas para desertores
    recall_dropouts: float  # Recall de clase 1
    precision_dropouts: float  # Precision de clase 1
    f1_dropouts: float  # F1-score de clase 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario."""
        return asdict(self)
    
    def __str__(self) -> str:
        """Representación legible."""
        return f"""
=== EVALUACIÓN DEL MODELO ===

📊 MÉTRICAS GENERALES:
  Accuracy:  {self.accuracy:.4f}
  Precision: {self.precision_macro:.4f}
  Recall:    {self.recall_macro:.4f}
  F1-Score:  {self.f1_macro:.4f}
  ROC-AUC:   {self.roc_auc:.4f}

📋 MATRIZ DE CONFUSIÓN:
  VP (Verdaderos Positivos):     {self.tp}
  FP (Falsos Positivos):         {self.fp}
  VN (Verdaderos Negativos):     {self.tn}
  FN (Falsos Negativos):         {self.fn}

🎯 DESERTORES (Clase 1):
  Recall (Sensibilidad):         {self.recall_dropouts:.4f}
    → {self.tp}/{self.tp + self.fn} desertores identificados
  Precision:                      {self.precision_dropouts:.4f}
  F1-Score:                       {self.f1_dropouts:.4f}

✅ NO DESERTORES (Clase 0):
  Recall:                         {self.class_0.recall:.4f}
  Precision:                      {self.class_0.precision:.4f}
  F1-Score:                       {self.class_0.f1:.4f}
"""


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_pred_proba: np.ndarray) -> ModelMetrics:
    """
    Calcular métricas completas del modelo.
    
    Args:
        y_true: Valores reales (0 o 1)
        y_pred: Predicciones (0 o 1)
        y_pred_proba: Probabilidades predichas para clase 1 [0, 1]
    
    Returns:
        ModelMetrics: Objeto con todas las métricas calculadas
    """
    # Métricas generales
    accuracy = accuracy_score(y_true, y_pred)
    precision_macro = precision_score(y_true, y_pred, average='macro')
    recall_macro = recall_score(y_true, y_pred, average='macro')
    f1_macro = f1_score(y_true, y_pred, average='macro')
    roc_auc = roc_auc_score(y_true, y_pred_proba)
    
    # Matriz de confusión
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    
    # Métricas por clase usando weighted (mejor para datos desbalanceados)
    precision_per_class = precision_score(y_true, y_pred, average=None)
    recall_per_class = recall_score(y_true, y_pred, average=None)
    f1_per_class = f1_score(y_true, y_pred, average=None)
    
    # Support por clase
    unique, counts = np.unique(y_true, return_counts=True)
    support = {int(u): int(c) for u, c in zip(unique, counts)}
    
    class_0 = ClassMetrics(
        precision=float(precision_per_class[0]),
        recall=float(recall_per_class[0]),
        f1=float(f1_per_class[0]),
        support=support.get(0, 0)
    )
    
    class_1 = ClassMetrics(
        precision=float(precision_per_class[1]),
        recall=float(recall_per_class[1]),
        f1=float(f1_per_class[1]),
        support=support.get(1, 0)
    )
    
    # Métricas específicas para desertores
    recall_dropouts = float(recall_per_class[1])
    precision_dropouts = float(precision_per_class[1])
    f1_dropouts = float(f1_per_class[1])
    
    return ModelMetrics(
        accuracy=accuracy,
        precision_macro=precision_macro,
        recall_macro=recall_macro,
        f1_macro=f1_macro,
        roc_auc=roc_auc,
        class_0=class_0,
        class_1=class_1,
        tn=int(tn),
        fp=int(fp),
        fn=int(fn),
        tp=int(tp),
        recall_dropouts=recall_dropouts,
        precision_dropouts=precision_dropouts,
        f1_dropouts=f1_dropouts,
    )


def get_classification_report(y_true: np.ndarray, y_pred: np.ndarray) -> str:
    """Obtener reporte de clasificación detallado."""
    return classification_report(
        y_true,
        y_pred,
        target_names=['No Desertor', 'Desertor'],
        digits=4
    )
