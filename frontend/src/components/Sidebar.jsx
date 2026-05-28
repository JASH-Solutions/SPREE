const navItems = [
  { label: "Inicio", key: "inicio" },
  { label: "Resumen", key: "resumen" },
  { label: "Analítica", key: "analitica" },
  { label: "Estudiantes", key: "estudiantes" },
  { label: "Alertas", key: "alertas" },
  { label: "Reportes", key: "reportes" },
];

const Sidebar = ({ active, onSelect }) => {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="logo">SPREE</div>
        <span className="subtitle">Retention Suite</span>
      </div>
      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <button
            key={item.label}
            type="button"
            onClick={() => onSelect(item.key)}
            className={`sidebar-item ${active === item.key ? "active" : ""}`}
          >
            {item.label}
          </button>
        ))}
      </nav>
      <div className="sidebar-footer">
        <div>UPTC - JASH Solutions</div>
        <div>v0.2 MVP</div>
      </div>
    </aside>
  );
};

export default Sidebar;