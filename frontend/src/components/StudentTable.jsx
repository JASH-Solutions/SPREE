const riskClass = (level) => {
  // Aplicando colores semánticos desde el CSS
  if (level === "Alto") return "badge badge-high";
  if (level === "Medio") return "badge badge-mid";
  return "badge badge-low";
};

const StudentTable = ({
  students,
  loading,
  onSelect,
  sortConfig,
  onSortChange,
  page,
  totalPages,
  onPageChange,
}) => {
  const renderSort = (label, key) => {
    const isActive = sortConfig.key === key;
    const direction = isActive ? (sortConfig.direction === "asc" ? "▲" : "▼") : "↕";

    return (
      <button
        type="button"
        className={`sort-button ${isActive ? "active" : ""}`}
        onClick={() =>
          onSortChange((prev) => {
            if (prev.key === key) {
              return {
                key,
                direction: prev.direction === "asc" ? "desc" : "asc",
              };
            }
            return { key, direction: "asc" };
          })
        }
      >
        <span>{label}</span>
        <span className="sort-indicator">{direction}</span>
      </button>
    );
  };

  return (
    <div className="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>{renderSort("Estudiante", "nombre")}</th>
            <th>{renderSort("Programa", "programa_academico")}</th>
            <th>{renderSort("Promedio", "promedio_academico")}</th>
            <th>{renderSort("Materias perdidas", "materias_perdidas")}</th>
            <th>{renderSort("Riesgo", "riesgo_nivel")}</th>
          </tr>
        </thead>
        <tbody>
          {loading && (
            <tr>
              <td className="empty-cell" colSpan="5">Cargando estudiantes...</td>
            </tr>
          )}
          {!loading && students.length === 0 && (
            <tr>
              <td className="empty-cell" colSpan="5">Sin resultados para este filtro.</td>
            </tr>
          )}
          {!loading &&
            students.map((student) => (
              <tr key={student.id_estudiante} onClick={() => onSelect(student.id_estudiante)}>
                <td>{student.nombre}</td>
                <td>{student.programa_academico}</td>
                <td>{student.promedio_academico?.toFixed(2)}</td>
                <td>{student.materias_perdidas}</td>
                <td>
                  <span className={riskClass(student.riesgo_nivel)}>
                    {student.riesgo_nivel}
                  </span>
                </td>
              </tr>
            ))}
        </tbody>
      </table>
      
      {/* Paginación ya existente, se conserva para performance */}
      <div className="pagination">
        <button
          type="button"
          className="page-button"
          onClick={() => onPageChange(Math.max(1, page - 1))}
          disabled={page <= 1}
        >
          Anterior
        </button>
        <span className="page-status">
          Página {page} de {totalPages}
        </span>
        <button
          type="button"
          className="page-button"
          onClick={() => onPageChange(Math.min(totalPages, page + 1))}
          disabled={page >= totalPages}
        >
          Siguiente
        </button>
      </div>
    </div>
  );
};

export default StudentTable;