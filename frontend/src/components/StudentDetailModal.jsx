const StudentDetailModal = ({ detail, loading, onClose }) => {
  return (
    <div className="modal">
      <div className="modal-content">
        <button type="button" className="modal-close" onClick={onClose}>
          Cerrar
        </button>
        {loading ? (
          <div className="empty">Cargando detalle...</div>
        ) : (
          <div className="modal-grid">
            <div>
              <span className="eyebrow">Perfil 360</span>
              {/* Limpieza adicional por precaución aunque se filtró de raíz */}
              <h3>
                {detail.data.primer_nombre?.replace(/nan/gi, '')} {detail.data.primer_apellido?.replace(/nan/gi, '')}
              </h3>
              <p>{detail.data.programa_academico}</p>
              <div className="detail-list">
                <div>
                  <span>Promedio</span>
                  <strong>{detail.data.promedio_academico}</strong>
                </div>
                <div>
                  <span>Materias perdidas</span>
                  <strong>{detail.data.materias_perdidas}</strong>
                </div>
                <div>
                  <span>Asistencia</span>
                  <strong>{detail.data.asistencia_clases}%</strong>
                </div>
                <div>
                  <span>Estado de pagos</span>
                  <strong>{detail.data.estado_pagos}</strong>
                </div>
                <div>
                  <span>Mora matrícula</span>
                  <strong>{detail.data.mora_matricula}</strong>
                </div>
              </div>
            </div>
            <div className="risk-panel">
              <span className="eyebrow">Predicción</span>
              <h3 className={`text-${detail.riesgo_nivel.toLowerCase()}`}>
                Riesgo {detail.riesgo_nivel}
              </h3>
              <p>
                Probabilidad {(detail.riesgo_probabilidad * 100).toFixed(1)}%
              </p>
              <div className="risk-box">
                <span className="eyebrow">Recomendación</span>
                <p>{detail.recomendacion}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StudentDetailModal;