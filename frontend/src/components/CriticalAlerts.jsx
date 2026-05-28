const CriticalAlerts = ({ alerts }) => {
  const formatProbability = (value) => {
    const normalized = Number.isFinite(value) ? value : 0;
    const capped = Math.min(normalized, 0.999);
    return (capped * 100).toFixed(1);
  };

  if (!alerts.length) {
    return <div className="empty">Sin alertas críticas por ahora.</div>;
  }

  return (
    <div className="critical-list critical-scroll">
      {alerts.map((alert) => (
        <article key={alert.id_estudiante} className="critical-item alert-high">
          <div className="critical-main">
            <div>
              <span className="eyebrow">{alert.programa_academico}</span>
              <h4>{alert.nombre}</h4>
            </div>
            {/* Reemplazamos barras de progreso confusas por un badge semántico claro */}
            <span className="badge badge-high">{alert.riesgo_nivel}</span>
          </div>
          <div className="critical-meta">
            <span className="critical-risk text-high">
              Riesgo predictivo: {formatProbability(alert.riesgo_probabilidad)}%
            </span>
            <div className="critical-reco">
              <span className="reco-icon">!</span>
              <span>{alert.recomendacion}</span>
            </div>
          </div>
        </article>
      ))}
    </div>
  );
};

export default CriticalAlerts;