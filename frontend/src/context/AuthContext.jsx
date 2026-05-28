import { createContext, useContext, useState } from "react";

const ROLES = {
  directivo: {
    label: "Directivo",
    color: "#7c3aed",
    pages: ["inicio", "resumen", "analitica", "estudiantes", "prediccion", "intervenciones", "alertas", "reportes"],
  },
  consejero: {
    label: "Consejero",
    color: "#0369a1",
    pages: ["inicio", "resumen", "estudiantes", "alertas", "intervenciones", "prediccion"],
  },
  analista: {
    label: "Analista",
    color: "#065f46",
    pages: ["inicio", "resumen", "analitica", "reportes"],
  },
};

const USERS = [
  { id: 1, username: "carlos.rodriguez", password: "director123", name: "Carlos Rodríguez", role: "directivo" },
  { id: 2, username: "maria.lopez",      password: "consejero123", name: "María López",      role: "consejero" },
  { id: 3, username: "juan.perez",       password: "analista123",  name: "Juan Pérez",       role: "analista"  },
];

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  const login = (username, password) => {
    const found = USERS.find(
      (u) => u.username === username && u.password === password
    );
    if (!found) return false;
    setUser(found);
    return true;
  };

  const logout = () => setUser(null);

  const canAccess = (page) => {
    if (!user) return false;
    return ROLES[user.role]?.pages.includes(page) ?? false;
  };

  const allowedPages = user ? ROLES[user.role]?.pages ?? [] : [];
  const roleInfo = user ? ROLES[user.role] : null;

  return (
    <AuthContext.Provider value={{ user, login, logout, canAccess, allowedPages, roleInfo, ROLES }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);

export { USERS, ROLES };
