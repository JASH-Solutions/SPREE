const StudentDetailModal = ({ detail, loading, onClose }) => {
  const getRiskColor = (nivel) => {
    switch(nivel) {
      case 'Alto': return '#b3261e';
      case 'Medio': return '#b26a00';
      case 'Bajo': return '#137333';
      default: return '#041c3b';
    }
  };

  const getStatusBadgeColor = (estado) => {
    if (estado === 'Al Día') return '#137333';
    if (estado === 'Atraso') return '#b26a00';
    if (estado === 'Embargo') return '#b3261e';
    return '#041c3b';
  };

  return (
    <div className="modal">
      <div className="modal-content modal-expanded">
        <div className="modal-header">
          <div className="modal-title-section">
            <h2>Perfil del Estudiante</h2>
            <button type="button" className="modal-close" onClick={onClose}>
              ✕
            </button>
          </div>
        </div>

        {loading ? (
          <div className="empty">Cargando detalle...</div>
        ) : (
          <div className="modal-body">
            {/* HEADER CON INFORMACIÓN PERSONAL */}
            <div className="detail-header">
              <div className="student-name-section">
                <h3>
                  {detail.data.primer_nombre?.replace(/nan/gi, '')} {detail.data.primer_apellido?.replace(/nan/gi, '')}
                </h3>
                <p className="student-id">ID: {detail.data.id_estudiante}</p>
                <p className="student-program">{detail.data.programa_academico}</p>
              </div>
              <div className="risk-badge-large" style={{ backgroundColor: getRiskColor(detail.riesgo_nivel) }}>
                <div className="risk-label">Riesgo</div>
                <div className="risk-level">{detail.riesgo_nivel}</div>
                <div className="risk-prob">{(detail.riesgo_probabilidad * 100).toFixed(1)}%</div>
              </div>
            </div>

            {/* SECCIONES PRINCIPALES */}
            <div className="detail-sections">
              {/* SECCIÓN ACADÉMICA */}
              <section className="detail-section">
                <div className="section-header">
                  <h4>Desempeño Académico</h4>
                </div>
                <div className="section-grid-3">
                  <div className="detail-item">
                    <span className="item-label">Promedio General</span>
                    <span className="item-value">{detail.data.promedio_academico?.toFixed(2)}</span>
                  </div>
                  <div className="detail-item">
                    <span className="item-label">Materias Perdidas</span>
                    <span className="item-value">{detail.data.materias_perdidas}</span>
                  </div>
                  <div className="detail-item">
                    <span className="item-label">Asistencia a Clases</span>
                    <span className="item-value">{detail.data.asistencia_clases}%</span>
                  </div>
                </div>
                <div className="section-grid-2">
                  <div className="detail-item">
                    <span className="item-label">Rendimiento Período</span>
                    <span className="item-value">{detail.data.rendimiento_periodo}%</span>
                  </div>
                  <div className="detail-item">
                    <span className="item-label">Casos de Riesgo</span>
                    <span className="item-value">{detail.data.casos_riesgo || 0}</span>
                  </div>
                </div>
              </section>

              {/* SECCIÓN FINANCIERA */}
              <section className="detail-section">
                <div className="section-header">
                  <h4>Situación Financiera</h4>
                </div>
                <div className="section-grid-3">
                  <div className="detail-item">
                    <span className="item-label">Estado de Pagos</span>
                    <span className="item-value" style={{ backgroundColor: getStatusBadgeColor(detail.data.estado_pagos), color: 'white', padding: '4px 8px', borderRadius: '4px', display: 'inline-block' }}>
                      {detail.data.estado_pagos}
                    </span>
                  </div>
                  <div className="detail-item">
                    <span className="item-label">Mora en Matrícula</span>
                    <span className="item-value">{detail.data.mora_matricula === 1 ? 'Sí' : 'No'}</span>
                  </div>
                  <div className="detail-item">
                    <span className="item-label">Estrato Socioeconómico</span>
                    <span className="item-value">{detail.data.estrato}</span>
                  </div>
                </div>
                <div className="section-grid-2">
                  <div className="detail-item">
                    <span className="item-label">Ingresos Familiares (aprox.)</span>
                    <span className="item-value">${Number(detail.data.ingresos_familiares || 0).toLocaleString()}</span>
                  </div>
                  <div className="detail-item">
                    <span className="item-label">Horas de Trabajo Semanal</span>
                    <span className="item-value">{detail.data.horas_trabajo_semanales} hrs</span>
                  </div>
                </div>
              </section>

              {/* SECCIÓN DE RECOMENDACIÓN */}
              <section className="detail-section recommendation-section">
                <div className="section-header">
                  <h4>Recomendación del Sistema</h4>
                </div>
                <div className="recommendation-box" style={{ borderLeftColor: getRiskColor(detail.riesgo_nivel) }}>
                  <p>{detail.recomendacion}</p>
                </div>
              </section>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StudentDetailModal;