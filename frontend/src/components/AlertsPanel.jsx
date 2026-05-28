import { useMemo, useState } from "react";

const AlertsPanel = ({ alerts, loading }) => {
  // Estados para la barra de herramientas (Panel de Control)
  const [searchTerm, setSearchTerm] = useState("");
  const [filterIntervention, setFilterIntervention] = useState("Todas");
  const [filterRisk, setFilterRisk] = useState("Todos");
  const [sortBy, setSortBy] = useState("prob_desc");

  // Extraer dinámicamente los tipos de intervención únicos para el filtro
  const interventionTypes = useMemo(() => {
    const types = new Set(alerts.map((a) => a.recomendacion));
    return ["Todas", ...Array.from(types).filter(Boolean)];
  }, [alerts]);

  // Lógica de filtrado y ordenamiento
  const filteredAndSortedAlerts = useMemo(() => {
    let result = [...alerts];

    // 1. Filtro por búsqueda (Nombre)
    if (searchTerm) {
      const lowerSearch = searchTerm.toLowerCase();
      result = result.filter((a) =>
        a.nombre?.toLowerCase().includes(lowerSearch)
      );
    }

    // 2. Filtro por tipo de intervención
    if (filterIntervention !== "Todas") {
      result = result.filter((a) => a.recomendacion === filterIntervention);
    }

    // 3. Filtro por nivel de riesgo
    if (filterRisk !== "Todos") {
      result = result.filter((a) => a.riesgo_nivel === filterRisk);
    }

    // 4. Ordenamiento
    result.sort((a, b) => {
      if (sortBy === "prob_desc") {
        return b.riesgo_probabilidad - a.riesgo_probabilidad;
      }
      if (sortBy === "prob_asc") {
        return a.riesgo_probabilidad - b.riesgo_probabilidad;
      }
      if (sortBy === "name_asc") {
        return (a.nombre || "").localeCompare(b.nombre || "");
      }
      return 0;
    });

    return result;
  }, [alerts, searchTerm, filterIntervention, filterRisk, sortBy]);

  const riskBadgeClass = (level) => {
    if (level === "Alto") return "badge badge-high";
    if (level === "Medio") return "badge badge-mid";
    return "badge badge-low";
  };

  const formatProbability = (value) => {
    const normalized = Number.isFinite(value) ? value : 0;
    const capped = Math.min(normalized, 0.999);
    return (capped * 100).toFixed(1);
  };

  if (loading) {
    return <div className="empty">Cargando alertas...</div>;
  }

  if (!alerts.length) {
    return <div className="empty">No hay alertas activas en este momento.</div>;
  }

  return (
    <div className="alerts-container">
      {/* PANEL DE CONTROL */}
      <div className="alerts-toolbar">
        <div className="search toolbar-search">
          <input
            type="search"
            placeholder="Buscar por estudiante..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="toolbar-filters">
          <select
            value={filterIntervention}
            onChange={(e) => setFilterIntervention(e.target.value)}
            className="filter-select"
          >
            {interventionTypes.map((type) => (
              <option key={type} value={type}>
                {type === "Todas" ? "Todas las intervenciones" : type}
              </option>
            ))}
          </select>
          <select
            value={filterRisk}
            onChange={(e) => setFilterRisk(e.target.value)}
            className="filter-select"
          >
            <option value="Todos">Todos los riesgos</option>
            <option value="Alto">Riesgo Alto</option>
            <option value="Medio">Riesgo Medio</option>
            <option value="Bajo">Riesgo Bajo</option>
          </select>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="filter-select"
          >
            <option value="prob_desc">Mayor probabilidad</option>
            <option value="prob_asc">Menor probabilidad</option>
            <option value="name_asc">Nombre (A-Z)</option>
          </select>
        </div>
      </div>

      {/* VISTA DE LISTA EXPANDIBLE / FILAS */}
      <div className="alerts-list">
        {filteredAndSortedAlerts.length === 0 ? (
          <div className="empty">No se encontraron alertas con estos filtros.</div>
        ) : (
          filteredAndSortedAlerts.map((alert) => (
            <article key={alert.id_estudiante} className="alert-row">
              {/* Columna 1: Estudiante y Meta */}
              <div className="alert-col-main">
                <h4>{alert.nombre}</h4>
                <span className="alert-meta">
                  Probabilidad: {formatProbability(alert.riesgo_probabilidad)}%
                </span>
              </div>

              {/* Columna 2: Motivo / Recomendación */}
              <div className="alert-col-reason">
                <span className="reason-label">{alert.recomendacion}</span>
              </div>

              {/* Columna 3: Riesgo (Badge Semántico) */}
              <div className="alert-col-risk">
                <span className={riskBadgeClass(alert.riesgo_nivel)}>
                  {alert.riesgo_nivel}
                </span>
              </div>

              {/* Columna 4: Acción alineada a la derecha */}
              <div className="alert-col-action">
                <button type="button" className="action-button secondary">
                  Gestionar caso
                </button>
              </div>
            </article>
          ))
        )}
      </div>
    </div>
  );
};

export default AlertsPanel;