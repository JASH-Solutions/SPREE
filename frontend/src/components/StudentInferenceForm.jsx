import { useState } from "react";
import { predictRisk } from "../api/client";

const StudentInferenceForm = () => {
  const [formData, setFormData] = useState({
    promedio_academico: "",
    materias_perdidas: "",
    asistencia_clases: "",
    rendimiento_periodo: "",
    estado_pagos: "Al Día",
    mora_matricula: false,
    estrato: "",
    ingresos_familiares: "",
    horas_trabajo_semanales: "",
    casos_riesgo: false,
  });

  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setPrediction(null);

    try {
      // Convertir valores a números donde sea necesario
      const cleanData = {
        promedio_academico: parseFloat(formData.promedio_academico),
        materias_perdidas: parseInt(formData.materias_perdidas, 10),
        asistencia_clases: parseFloat(formData.asistencia_clases),
        rendimiento_periodo: parseFloat(formData.rendimiento_periodo),
        estado_pagos: formData.estado_pagos,
        mora_matricula: formData.mora_matricula ? 1 : 0,
        estrato: parseInt(formData.estrato, 10),
        ingresos_familiares: parseFloat(formData.ingresos_familiares),
        horas_trabajo_semanales: parseFloat(formData.horas_trabajo_semanales),
        casos_riesgo: formData.casos_riesgo ? 1 : 0,
      };

      const result = await predictRisk({ student: cleanData });
      setPrediction(result);
    } catch (err) {
      setError(err.message || "Error al realizar la predicción");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFormData({
      promedio_academico: "",
      materias_perdidas: "",
      asistencia_clases: "",
      rendimiento_periodo: "",
      estado_pagos: "Al Día",
      mora_matricula: false,
      estrato: "",
      ingresos_familiares: "",
      horas_trabajo_semanales: "",
      casos_riesgo: false,
    });
    setPrediction(null);
    setError("");
  };

  const getRiskColor = (nivel) => {
    switch (nivel) {
      case "Alto":
        return "#b3261e";
      case "Medio":
        return "#b26a00";
      case "Bajo":
        return "#137333";
      default:
        return "#1f1f1f";
    }
  };

  return (
    <div className="inference-container">
      <div className="inference-header">
        <h1>Predicción de Riesgo de Deserción</h1>
        <p>Ingresa los datos del estudiante para obtener una predicción en tiempo real</p>
      </div>

      <div className="inference-content">
        <form onSubmit={handleSubmit} className="inference-form">
          <div className="form-section">
            <h2>Información Académica</h2>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="promedio_academico">Promedio Académico (0-5)</label>
                <input
                  type="number"
                  id="promedio_academico"
                  name="promedio_academico"
                  min="0"
                  max="5"
                  step="0.1"
                  value={formData.promedio_academico}
                  onChange={handleInputChange}
                  required
                  placeholder="Ej: 3.5"
                />
              </div>

              <div className="form-group">
                <label htmlFor="materias_perdidas">Materias Perdidas</label>
                <input
                  type="number"
                  id="materias_perdidas"
                  name="materias_perdidas"
                  min="0"
                  value={formData.materias_perdidas}
                  onChange={handleInputChange}
                  required
                  placeholder="Ej: 2"
                />
              </div>

              <div className="form-group">
                <label htmlFor="asistencia_clases">Asistencia a Clases (%)</label>
                <input
                  type="number"
                  id="asistencia_clases"
                  name="asistencia_clases"
                  min="0"
                  max="100"
                  step="0.1"
                  value={formData.asistencia_clases}
                  onChange={handleInputChange}
                  required
                  placeholder="Ej: 85.5"
                />
              </div>

              <div className="form-group">
                <label htmlFor="rendimiento_periodo">Rendimiento Período (%)</label>
                <input
                  type="number"
                  id="rendimiento_periodo"
                  name="rendimiento_periodo"
                  min="0"
                  max="100"
                  step="0.1"
                  value={formData.rendimiento_periodo}
                  onChange={handleInputChange}
                  required
                  placeholder="Ej: 75.0"
                />
              </div>
            </div>
          </div>

          <div className="form-section">
            <h2>Información Financiera</h2>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="estado_pagos">Estado de Pagos</label>
                <select
                  id="estado_pagos"
                  name="estado_pagos"
                  value={formData.estado_pagos}
                  onChange={handleInputChange}
                  required
                >
                  <option value="Al Día">Al Día</option>
                  <option value="Atraso">Atraso</option>
                  <option value="Embargo">Embargo</option>
                </select>
              </div>

              <div className="form-group checkbox-group">
                <label htmlFor="mora_matricula">
                  <input
                    type="checkbox"
                    id="mora_matricula"
                    name="mora_matricula"
                    checked={formData.mora_matricula}
                    onChange={handleInputChange}
                  />
                  Mora en Matrícula
                </label>
              </div>

              <div className="form-group">
                <label htmlFor="estrato">Estrato (1-6)</label>
                <input
                  type="number"
                  id="estrato"
                  name="estrato"
                  min="1"
                  max="6"
                  value={formData.estrato}
                  onChange={handleInputChange}
                  required
                  placeholder="Ej: 3"
                />
              </div>

              <div className="form-group">
                <label htmlFor="ingresos_familiares">Ingresos Familiares (COP)</label>
                <input
                  type="number"
                  id="ingresos_familiares"
                  name="ingresos_familiares"
                  min="0"
                  value={formData.ingresos_familiares}
                  onChange={handleInputChange}
                  required
                  placeholder="Ej: 2000000"
                />
              </div>
            </div>
          </div>

          <div className="form-section">
            <h2>Información General</h2>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="horas_trabajo_semanales">Horas de Trabajo Semanales</label>
                <input
                  type="number"
                  id="horas_trabajo_semanales"
                  name="horas_trabajo_semanales"
                  min="0"
                  max="168"
                  step="0.5"
                  value={formData.horas_trabajo_semanales}
                  onChange={handleInputChange}
                  required
                  placeholder="Ej: 20"
                />
              </div>

              <div className="form-group checkbox-group">
                <label htmlFor="casos_riesgo">
                  <input
                    type="checkbox"
                    id="casos_riesgo"
                    name="casos_riesgo"
                    checked={formData.casos_riesgo}
                    onChange={handleInputChange}
                  />
                  Casos de Riesgo
                </label>
              </div>
            </div>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn-predict" disabled={loading}>
              {loading ? "Procesando..." : "Obtener Predicción"}
            </button>
            <button type="button" className="btn-reset" onClick={handleReset}>
              Limpiar Formulario
            </button>
          </div>
        </form>

        {error && <div className="error-message">{error}</div>}

        {prediction && (
          <div className="prediction-result">
            <h2>Resultado de la Predicción</h2>
            <div className="prediction-card" style={{ borderColor: getRiskColor(prediction.riesgo_nivel) }}>
              <div className="prediction-level">
                <span className="label">Nivel de Riesgo:</span>
                <span
                  className="value"
                  style={{
                    color: getRiskColor(prediction.riesgo_nivel),
                    fontWeight: "700",
                    fontSize: "1.5rem",
                  }}
                >
                  {prediction.riesgo_nivel}
                </span>
              </div>
              <div className="prediction-probability">
                <span className="label">Probabilidad de Deserción:</span>
                <div className="probability-bar">
                  <div
                    className="probability-fill"
                    style={{
                      width: `${prediction.riesgo_probabilidad * 100}%`,
                      backgroundColor: getRiskColor(prediction.riesgo_nivel),
                    }}
                  />
                </div>
                <span className="percentage">{(prediction.riesgo_probabilidad * 100).toFixed(2)}%</span>
              </div>
              <div className="prediction-interpretation">
                {prediction.riesgo_nivel === "Alto" && (
                  <p>⚠️ Este estudiante tiene un alto riesgo de deserción. Se recomienda intervención inmediata.</p>
                )}
                {prediction.riesgo_nivel === "Medio" && (
                  <p>⚡ Este estudiante tiene un riesgo medio de deserción. Se sugiere seguimiento cercano.</p>
                )}
                {prediction.riesgo_nivel === "Bajo" && (
                  <p>✓ Este estudiante tiene bajo riesgo de deserción. Se recomienda seguimiento estándar.</p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StudentInferenceForm;
