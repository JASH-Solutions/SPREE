
def classify_risk(
    probability: float,
    low_threshold: float = 0.4,
    high_threshold: float = 0.7
) -> str:
    """
    Clasifica el nivel de riesgo de deserción
    según la probabilidad generada por el modelo.

    Args:
        probability (float): Probabilidad entre 0 y 1.
        low_threshold (float): Umbral mínimo de riesgo medio.
        high_threshold (float): Umbral mínimo de riesgo alto.

    Returns:
        str: Etiqueta de riesgo.
    """

    if probability < 0 or probability > 1:
        raise ValueError("La probabilidad debe estar entre 0 y 1.")

    if low_threshold >= high_threshold:
        raise ValueError(
            "low_threshold debe ser menor que high_threshold."
        )

    if probability < low_threshold:
        return "Bajo"

    elif probability < high_threshold:
        return "Medio"

    return "Alto"

"""
Ejemplo de uso:

risk = classify_risk(0.82)

print(risk)

Ejemplo con parámetros:


risk = classify_risk(
    probability=0.55,
    low_threshold=0.3,
    high_threshold=0.6
)

print(risk)

"""