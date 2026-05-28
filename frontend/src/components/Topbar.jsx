import { useAuth } from "../context/AuthContext";

const Topbar = ({ page }) => {
  const { user, roleInfo } = useAuth();

  return (
    <div className="topbar">
      <div className="topbar-left">
        <div className="topbar-title">Panel de Retención</div>
        <div className="topbar-sub">
          Universidad Pedagógica y Tecnológica de Colombia
        </div>
      </div>

      <div className="topbar-view-badge">
        <span className="view-dot" />
        <span>{page}</span>
      </div>

      <div className="topbar-right">
        <div className="topbar-program">
          <span>Programa</span>
          <strong>Ingeniería de Sistemas</strong>
        </div>
        {user && roleInfo && (
          <span
            className="role-pill"
            style={{ background: roleInfo.color }}
          >
            {roleInfo.label}
          </span>
        )}
        <span className="status-pill">Datos sincronizados</span>
      </div>
    </div>
  );
};

export default Topbar;
