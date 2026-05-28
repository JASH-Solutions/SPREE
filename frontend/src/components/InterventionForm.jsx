import { useState, useEffect } from "react";

const InterventionForm = ({ studentId: initialStudentId, onSubmitSuccess }) => {
  const [students, setStudents] = useState([]);
  const [loadingStudents, setLoadingStudents] = useState(false);
  const [selectedStudentId, setSelectedStudentId] = useState(initialStudentId || null);
  const [studentSearch, setStudentSearch] = useState("");

  const [formData, setFormData] = useState({
    tipo: "Académica",
    descripcion: "",
    responsable: "",
    resultado_esperado: "",
    estado: "Planeada",
    notas_adicionales: "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [interventions, setInterventions] = useState([]);
  const [loadingInterventions, setLoadingInterventions] = useState(false);

  const tipos = ["Académica", "Financiera", "Personal", "Emocional", "Familiar"];
  const estados = ["Planeada", "En progreso", "Completada", "Cancelada"];

  // Cargar estudiantes
  useEffect(() => {
    const loadStudents = async () => {
      try {
        setLoadingStudents(true);
        const response = await fetch("http://127.0.0.1:8000/api/students");
        if (!response.ok) throw new Error("Error al cargar estudiantes");
        const data = await response.json();
        setStudents(data.items || []);
      } catch (err) {
        console.error("Error loading students:", err);
      } finally {
        setLoadingStudents(false);
      }
    };
    loadStudents();
  }, []);

  // Cargar intervenciones del estudiante
  useEffect(() => {
    if (selectedStudentId) {
      loadInterventions();
    }
  }, [selectedStudentId]);

  const loadInterventions = async () => {
    try {
      setLoadingInterventions(true);
      const response = await fetch(
        `http://127.0.0.1:8000/api/interventions/student/${selectedStudentId}`
      );
      if (!response.ok) throw new Error("Error al cargar intervenciones");
      const data = await response.json();
      setInterventions(data.intervenciones || []);
    } catch (err) {
      console.error("Error loading interventions:", err);
    } finally {
      setLoadingInterventions(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const payload = {
        student_id: selectedStudentId,
        ...formData,
      };

      const response = await fetch("http://127.0.0.1:8000/api/interventions/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Error al registrar intervención");
      }

      const result = await response.json();
      setSuccess(`✓ ${result.mensaje}`);

      // Limpiar formulario
      setFormData({
        tipo: "Académica",
        descripcion: "",
        responsable: "",
        resultado_esperado: "",
        estado: "Planeada",
        notas_adicionales: "",
      });

      // Recargar intervenciones
      await loadInterventions();

      // Llamar callback si existe
      if (onSubmitSuccess) onSubmitSuccess();
    } catch (err) {
      setError(err.message || "Error al registrar intervención");
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (estado) => {
    switch (estado) {
      case "Completada":
        return "#137333";
      case "En progreso":
        return "#b26a00";
      case "Planeada":
        return "#041c3b";
      case "Cancelada":
        return "#b3261e";
      default:
        return "#1f1f1f";
    }
  };

  const getTypeIcon = (tipo) => {
    const icons = {
      Académica: "📚",
      Financiera: "💰",
      Personal: "👤",
      Emocional: "❤️",
      Familiar: "👨‍👩‍👧",
    };
    return icons[tipo] || "📋";
  };

  // Filtrar estudiantes por búsqueda
  const filteredStudents = students.filter((s) =>
    s.nombre?.toLowerCase().includes(studentSearch.toLowerCase()) ||
    s.id_estudiante?.toString().includes(studentSearch)
  );

  const selectedStudent = students.find((s) => s.id_estudiante === selectedStudentId);

  if (!selectedStudentId) {
    return (
      <div className="intervention-container">
        <div className="intervention-header">
          <h1>Registro de Intervenciones</h1>
          <p>Documenta las acciones tomadas para mitigar el riesgo de deserción</p>
        </div>

        <div className="student-selector">
          <div className="selector-card">
            <h2>Selecciona un Estudiante</h2>
            <p>Elige un estudiante para registrar sus intervenciones</p>

            <div className="search-box">
              <input
                type="text"
                placeholder="Buscar por nombre o ID..."
                value={studentSearch}
                onChange={(e) => setStudentSearch(e.target.value)}
                className="search-input"
              />
            </div>

            <div className="students-grid">
              {loadingStudents ? (
                <p className="loading">Cargando estudiantes...</p>
              ) : filteredStudents.length === 0 ? (
                <p className="no-results">No se encontraron estudiantes</p>
              ) : (
                filteredStudents.map((student) => (
                  <button
                    key={student.id_estudiante}
                    type="button"
                    onClick={() => setSelectedStudentId(student.id_estudiante)}
                    className="student-card"
                  >
                    <div className="student-card-name">{student.nombre}</div>
                    <div className="student-card-id">ID: {student.id_estudiante}</div>
                    <div className="student-card-program">{student.programa_academico}</div>
                    <div
                      className="student-risk-badge"
                      style={{
                        backgroundColor:
                          student.riesgo_nivel === "Alto"
                            ? "#b3261e"
                            : student.riesgo_nivel === "Medio"
                            ? "#b26a00"
                            : "#137333",
                      }}
                    >
                      {student.riesgo_nivel}
                    </div>
                  </button>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="intervention-container">
      <div className="intervention-header">
        <div className="header-content">
          <h1>Registro de Intervenciones</h1>
          <p>Documenta las acciones tomadas para mitigar el riesgo de deserción</p>
        </div>
        {selectedStudent && (
          <div className="selected-student-info">
            <div className="student-info">
              <span className="label">Estudiante:</span>
              <span className="value">{selectedStudent.nombre}</span>
              <span className="id">(ID: {selectedStudent.id_estudiante})</span>
            </div>
            <button
              type="button"
              onClick={() => setSelectedStudentId(null)}
              className="btn-change-student"
            >
              Cambiar
            </button>
          </div>
        )}
      </div>

      <div className="intervention-content">
        <form onSubmit={handleSubmit} className="intervention-form">
          <div className="form-section">
            <h2>Nueva Intervención</h2>

            <div className="form-group">
              <label htmlFor="tipo">Tipo de Intervención *</label>
              <select
                id="tipo"
                name="tipo"
                value={formData.tipo}
                onChange={handleInputChange}
                required
              >
                {tipos.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="descripcion">Descripción de la Intervención *</label>
              <textarea
                id="descripcion"
                name="descripcion"
                value={formData.descripcion}
                onChange={handleInputChange}
                placeholder="Describe detalladamente qué se hizo..."
                required
                rows="4"
              />
            </div>

            <div className="form-group">
              <label htmlFor="responsable">Responsable *</label>
              <input
                type="text"
                id="responsable"
                name="responsable"
                value={formData.responsable}
                onChange={handleInputChange}
                placeholder="Nombre de la persona responsable"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="resultado_esperado">Resultado Esperado *</label>
              <textarea
                id="resultado_esperado"
                name="resultado_esperado"
                value={formData.resultado_esperado}
                onChange={handleInputChange}
                placeholder="Cuál es el objetivo de esta intervención?"
                required
                rows="3"
              />
            </div>

            <div className="form-grid-2">
              <div className="form-group">
                <label htmlFor="estado">Estado *</label>
                <select
                  id="estado"
                  name="estado"
                  value={formData.estado}
                  onChange={handleInputChange}
                  required
                >
                  {estados.map((e) => (
                    <option key={e} value={e}>
                      {e}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="notas_adicionales">Notas Adicionales</label>
                <input
                  type="text"
                  id="notas_adicionales"
                  name="notas_adicionales"
                  value={formData.notas_adicionales}
                  onChange={handleInputChange}
                  placeholder="Información adicional (opcional)"
                />
              </div>
            </div>

            <div className="form-actions">
              <button type="submit" className="btn-register" disabled={loading}>
                {loading ? "Registrando..." : "Registrar Intervención"}
              </button>
            </div>

            {error && <div className="error-message">{error}</div>}
            {success && <div className="success-message">{success}</div>}
          </div>
        </form>

        <div className="interventions-history">
          <h2>Historial de Intervenciones</h2>
          {loadingInterventions ? (
            <p>Cargando...</p>
          ) : interventions.length === 0 ? (
            <p className="empty-message">No hay intervenciones registradas</p>
          ) : (
            <div className="interventions-list">
              {interventions.map((intervention) => (
                <div key={intervention.intervention_id} className="intervention-card">
                  <div className="intervention-header-card">
                    <div className="intervention-title">
                      <span className="intervention-icon">{getTypeIcon(intervention.tipo)}</span>
                      <h3>{intervention.tipo}</h3>
                    </div>
                    <span
                      className="intervention-status"
                      style={{ backgroundColor: getStatusColor(intervention.estado) }}
                    >
                      {intervention.estado}
                    </span>
                  </div>

                  <div className="intervention-body">
                    <div className="intervention-field">
                      <span className="label">Descripción:</span>
                      <p>{intervention.descripcion}</p>
                    </div>

                    <div className="intervention-field">
                      <span className="label">Resultado Esperado:</span>
                      <p>{intervention.resultado_esperado}</p>
                    </div>

                    <div className="intervention-meta">
                      <div className="meta-item">
                        <span className="meta-label">Responsable:</span>
                        <span className="meta-value">{intervention.responsable}</span>
                      </div>
                      <div className="meta-item">
                        <span className="meta-label">Fecha:</span>
                        <span className="meta-value">
                          {new Date(intervention.fecha_creacion).toLocaleDateString()}
                        </span>
                      </div>
                    </div>

                    {intervention.notas_adicionales && (
                      <div className="intervention-field">
                        <span className="label">Notas:</span>
                        <p className="notes">{intervention.notas_adicionales}</p>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default InterventionForm;
