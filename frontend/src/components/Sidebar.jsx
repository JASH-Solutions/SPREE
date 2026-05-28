import { useState } from "react";
import {
  FiHome,
  FiBarChart2,
  FiTrendingUp,
  FiUsers,
  FiBell,
  FiFileText,
  FiZap,
  FiClipboard,
  FiChevronLeft,
  FiChevronRight,
  FiLogOut,
} from "react-icons/fi";
import { useAuth } from "../context/AuthContext";

const ALL_NAV_ITEMS = [
  { label: "Inicio",         key: "inicio",         icon: FiHome      },
  { label: "Resumen",        key: "resumen",         icon: FiBarChart2 },
  { label: "Analítica",      key: "analitica",       icon: FiTrendingUp },
  { label: "Estudiantes",    key: "estudiantes",     icon: FiUsers     },
  { label: "Predicción",     key: "prediccion",      icon: FiZap       },
  { label: "Intervenciones", key: "intervenciones",  icon: FiClipboard },
  { label: "Alertas",        key: "alertas",         icon: FiBell      },
  { label: "Reportes",       key: "reportes",        icon: FiFileText  },
];

const Sidebar = ({ active, onSelect }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const { user, logout, allowedPages, roleInfo } = useAuth();

  const navItems = ALL_NAV_ITEMS.filter((item) => allowedPages.includes(item.key));

  return (
    <aside className={`sidebar ${isCollapsed ? "collapsed" : ""}`}>
      <button
        type="button"
        className="sidebar-toggle"
        onClick={() => setIsCollapsed(!isCollapsed)}
        title={isCollapsed ? "Expandir sidebar" : "Contraer sidebar"}
      >
        {isCollapsed ? <FiChevronRight /> : <FiChevronLeft />}
      </button>

      <div className="sidebar-brand">
        <img
          src="/Escudo.png"
          alt="SPREE Logo"
          className="logo-image"
          style={{ display: "block", margin: "0 auto" }}
        />
        {!isCollapsed && <span className="subtitle">SPREE</span>}
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const IconComponent = item.icon;
          return (
            <button
              key={item.key}
              type="button"
              onClick={() => onSelect(item.key)}
              className={`sidebar-item ${active === item.key ? "active" : ""}`}
              title={isCollapsed ? item.label : ""}
            >
              <span className="sidebar-item-icon">
                <IconComponent />
              </span>
              {!isCollapsed && <span className="sidebar-item-label">{item.label}</span>}
            </button>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        {user && (
          <div className="sidebar-user">
            {!isCollapsed && (
              <>
                <span
                  className="sidebar-role-badge"
                  style={{ background: roleInfo?.color }}
                >
                  {roleInfo?.label}
                </span>
                <span className="sidebar-user-name">{user.name}</span>
              </>
            )}
            <button
              type="button"
              className="sidebar-logout"
              onClick={logout}
              title="Cerrar sesión"
            >
              <FiLogOut />
              {!isCollapsed && <span>Salir</span>}
            </button>
          </div>
        )}
        {!isCollapsed && (
          <div className="sidebar-footer-meta">
            <div>UPTC · JASH Solutions</div>
            <div>v0.2 MVP</div>
          </div>
        )}
        {isCollapsed && <div className="footer-collapsed">v0.2</div>}
      </div>
    </aside>
  );
};

export default Sidebar;
