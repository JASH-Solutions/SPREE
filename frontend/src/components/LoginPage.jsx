import { useState } from "react";
import { useAuth, USERS } from "../context/AuthContext";
import { FiEye, FiEyeOff, FiLock, FiUser } from "react-icons/fi";

const roleHints = {
  directivo: { color: "#7c3aed", label: "Directivo" },
  consejero:  { color: "#0369a1", label: "Consejero" },
  analista:   { color: "#065f46", label: "Analista"  },
};

const LoginPage = () => {
  const { login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPass, setShowPass] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    setTimeout(() => {
      const ok = login(username.trim(), password);
      if (!ok) setError("Credenciales incorrectas. Verifica usuario y contraseña.");
      setLoading(false);
    }, 400);
  };

  const fillUser = (u) => {
    setUsername(u.username);
    setPassword(u.password);
    setError("");
  };

  return (
    <div className="login-shell">
      <div className="login-card">
        <div className="login-header">
          <img src="/Escudo.png" alt="SPREE" className="login-logo" />
          <h1>SPREE</h1>
          <p>Sistema de Predicción y Retención Estudiantil</p>
          <span className="login-uni">UPTC · Ingeniería de Sistemas</span>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <div className="login-field">
            <label htmlFor="username">Usuario</label>
            <div className="login-input-wrap">
              <FiUser className="login-input-icon" />
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="nombre.apellido"
                autoComplete="username"
                required
              />
            </div>
          </div>

          <div className="login-field">
            <label htmlFor="password">Contraseña</label>
            <div className="login-input-wrap">
              <FiLock className="login-input-icon" />
              <input
                id="password"
                type={showPass ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                autoComplete="current-password"
                required
              />
              <button
                type="button"
                className="login-pass-toggle"
                onClick={() => setShowPass((v) => !v)}
                tabIndex={-1}
              >
                {showPass ? <FiEyeOff /> : <FiEye />}
              </button>
            </div>
          </div>

          {error && <p className="login-error">{error}</p>}

          <button type="submit" className="login-btn" disabled={loading}>
            {loading ? "Ingresando…" : "Iniciar sesión"}
          </button>
        </form>

        <div className="login-demo">
          <p>Acceso rápido (demo)</p>
          <div className="login-demo-users">
            {USERS.map((u) => {
              const r = roleHints[u.role];
              return (
                <button
                  key={u.id}
                  type="button"
                  className="login-demo-chip"
                  style={{ "--chip-color": r.color }}
                  onClick={() => fillUser(u)}
                >
                  <span className="chip-role" style={{ background: r.color }}>{r.label}</span>
                  <span className="chip-name">{u.name}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
