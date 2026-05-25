from pathlib import Path

import pandas as pd

from app.utils.model_persistence import load_risk_model, load_risk_model_metadata, train_and_persist_risk_model


def _write_csv(path: Path, data: dict[str, list]) -> None:
    pd.DataFrame(data).to_csv(path, index=False)


def test_train_persists_model_and_metadata(tmp_path):
    raw_dir = tmp_path / "raw"
    model_dir = tmp_path / "models"
    raw_dir.mkdir()

    ids = [f"EST-{index:04d}" for index in range(1, 11)]

    _write_csv(
        raw_dir / "demographic.csv",
        {
            "id_estudiante": ids,
            "edad": [20, 24, 21, 22, 19, 23, 25, 20, 22, 24],
            "genero": ["Masculino", "Femenino", "Masculino", "Femenino", "Masculino", "Femenino", "Masculino", "Femenino", "Masculino", "Femenino"],
            "programa_academico": ["Ingeniería"] * 10,
            "ciudad_origen": ["Lima", "Cusco", "Lima", "Piura", "Lima", "Arequipa", "Lima", "Trujillo", "Lima", "Ica"],
            "estado_estudiante": ["Activo", "Desertor", "Activo", "Desertor", "Activo", "Desertor", "Activo", "Desertor", "Activo", "Desertor"],
        },
    )
    _write_csv(
        raw_dir / "academics.csv",
        {
            "id_estudiante": ids,
            "promedio_academico": [4.2, 2.8, 3.9, 2.5, 4.0, 3.0, 4.1, 2.9, 3.8, 2.7],
            "materias_perdidas": [0, 4, 1, 5, 0, 3, 0, 4, 1, 5],
            "semestre_cursado": [3, 6, 4, 7, 2, 5, 3, 6, 4, 7],
            "creditos_matriculados": [16, 14, 15, 12, 16, 13, 15, 12, 16, 13],
            "creditos_aprobados": [16, 8, 14, 7, 15, 9, 15, 8, 14, 7],
            "asistencia_clases": [95, 62, 90, 58, 96, 65, 94, 60, 91, 57],
            "rendimiento_periodo": [0.1, -0.4, 0.2, -0.5, 0.15, -0.3, 0.1, -0.35, 0.2, -0.45],
        },
    )
    _write_csv(
        raw_dir / "financial.csv",
        {
            "id_estudiante": ids,
            "estado_pagos": ["Al día", "En mora", "Al día", "Pago parcial", "Al día", "En mora", "Al día", "Pago parcial", "Al día", "En mora"],
            "mora_matricula": [False, True, False, True, False, True, False, True, False, True],
            "becas_apoyos": ["Sí", "No", "Sí", "No", "Sí", "No", "Sí", "No", "Sí", "No"],
        },
    )
    _write_csv(
        raw_dir / "socioeconomic.csv",
        {
            "id_estudiante": ids,
            "estrato": [3, 1, 4, 2, 3, 1, 4, 2, 3, 1],
            "ingresos_familiares": [2500000, 900000, 3200000, 1200000, 2400000, 1000000, 3100000, 1100000, 2600000, 950000],
            "num_dependientes": [2, 4, 1, 3, 2, 4, 1, 3, 2, 4],
            "situacion_laboral": ["No trabaja", "Tiempo completo", "No trabaja", "Medio tiempo", "No trabaja", "Tiempo completo", "No trabaja", "Medio tiempo", "No trabaja", "Tiempo completo"],
            "horas_trabajo_semanales": [0, 45, 0, 20, 0, 42, 0, 18, 0, 40],
            "lugar_residencia": ["Misma ciudad", "Ciudad lejana", "Misma ciudad", "Ciudad cercana", "Misma ciudad", "Ciudad lejana", "Misma ciudad", "Ciudad cercana", "Misma ciudad", "Ciudad lejana"],
            "tipo_vivienda": ["Familiar", "Arrendada", "Propia", "Arrendada", "Familiar", "Arrendada", "Propia", "Arrendada", "Familiar", "Arrendada"],
        },
    )
    _write_csv(
        raw_dir / "well-being.csv",
        {
            "id_estudiante": ids,
            "atenciones_psicologicas": [0, 3, 0, 2, 0, 2, 0, 3, 0, 2],
            "seguimientos_realizados": [1, 3, 0, 2, 1, 2, 0, 3, 1, 2],
            "casos_riesgo": [False, True, False, True, False, True, False, True, False, True],
        },
    )
    _write_csv(
        raw_dir / "additional.csv",
        {
            "id_estudiante": ids,
            "participacion_institucional": [3, 0, 2, 1, 3, 1, 2, 0, 3, 1],
            "evaluacion_docente": [4.6, 3.2, 4.7, 3.1, 4.5, 3.3, 4.4, 3.0, 4.6, 3.2],
        },
    )

    artifact = train_and_persist_risk_model(data_dir=raw_dir, model_dir=model_dir)

    assert artifact["model_path"].exists()
    assert artifact["metadata_path"].exists()

    model = load_risk_model(artifact["model_path"])
    metadata = load_risk_model_metadata(artifact["metadata_path"])

    sample = pd.DataFrame(
        [
            {
                "edad": 22,
                "genero": "Masculino",
                "programa_academico": "Ingeniería",
                "ciudad_origen": "Lima",
                "estrato": 3,
                "ingresos_familiares": 2000000,
                "num_dependientes": 2,
                "situacion_laboral": "No trabaja",
                "horas_trabajo_semanales": 0,
                "lugar_residencia": "Misma ciudad",
                "tipo_vivienda": "Familiar",
                "promedio_academico": 4.1,
                "materias_perdidas": 0,
                "semestre_cursado": 3,
                "creditos_matriculados": 16,
                "creditos_aprobados": 16,
                "asistencia_clases": 94,
                "rendimiento_periodo": 0.2,
                "estado_pagos": "Al día",
                "mora_matricula": False,
                "becas_apoyos": "Sí",
                "atenciones_psicologicas": 0,
                "seguimientos_realizados": 1,
                "casos_riesgo": False,
                "participacion_institucional": 3,
                "evaluacion_docente": 4.5,
            }
        ]
    )

    prediction = model.predict(sample)

    assert prediction.shape == (1,)
    assert metadata["features"]
    assert "created_at" in metadata
    assert "metrics" in metadata
    assert "accuracy" in metadata["metrics"]
