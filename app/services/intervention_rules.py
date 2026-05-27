def assign_intervention(student: dict) -> str:
    """
    Asigna una intervención recomendada
    según el perfil del estudiante.
    """

    # Riesgo financiero
    if (
        student["mora_matricula"] is True or
        student["ingresos_familiares"] < 1200000
    ):
        return "Apoyo Financiero"

    # Riesgo académico
    if (
        student["promedio_academico"] < 3.0 or
        student["materias_perdidas"] >= 3
    ):
        return "Tutoría Académica"

    # Riesgo psicológico
    if (
        student["atenciones_psicologicas"] > 2 or
        student["asistencia"] < 60
    ):
        return "Orientación Psicológica"

    # Riesgo laboral/académico
    if (
        student["horas_trabajo"] > 30 and
        student["promedio_academico"] < 3.2
    ):
        return "Flexibilización Académica"

    # Semestres iniciales
    if student["semestre"] <= 2:
        return "Mentoría Estudiantil"

    return "Seguimiento Bienestar"