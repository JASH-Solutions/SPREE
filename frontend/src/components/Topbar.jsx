const Topbar = ({ page }) => {
  return (
    <div className="topbar">
      <div className="topbar-left">
        <div className="topbar-title">Panel de Retención · {page}</div>
        {/* Contraste solucionado en CSS, pero se asegura la estructura */}
        <div className="topbar-sub">
          Universidad Pedagógica y Tecnológica de Colombia
        </div>
      </div>
      <div className="topbar-right">
        <div className="topbar-program">
          <span>Programa</span>
          <strong>Ingeniería de Sistemas</strong>
        </div>
        <span className="status-pill">Datos sincronizados</span>
      </div>
    </div>
  );
};

export default Topbar;