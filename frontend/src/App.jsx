import { useEffect, useMemo, useState } from "react";

import { getAlerts, getFeatureImportance, getReportsSemesterEvolution, getStudentDetail, getStudents } from "./api/client";
import AlertsPanel from "./components/AlertsPanel";
import CriticalAlerts from "./components/CriticalAlerts";
import FeatureImportanceChart from "./components/FeatureImportanceChart";
import Header from "./components/Header";
import InterventionForm from "./components/InterventionForm";
import LoginPage from "./components/LoginPage";
import MetricCard from "./components/MetricCard";
import RiskDistributionChart from "./components/RiskDistributionChart";
import RiskDonut from "./components/RiskDonut";
import SearchBar from "./components/SearchBar";
import SemesterEvolutionChart from "./components/SemesterEvolutionChart";
import Sidebar from "./components/Sidebar";
import StudentDetailModal from "./components/StudentDetailModal";
import StudentInferenceForm from "./components/StudentInferenceForm";
import StudentTable from "./components/StudentTable";
import Topbar from "./components/Topbar";
import { AuthProvider, useAuth } from "./context/AuthContext";

const pageLabels = {
  inicio:         "Inicio",
  resumen:        "Resumen",
  analitica:      "Analítica",
  estudiantes:    "Estudiantes",
  prediccion:     "Predicción",
  intervenciones: "Intervenciones",
  alertas:        "Alertas",
  reportes:       "Reportes",
};

const cleanString = (str) => {
  if (!str || typeof str !== "string") return str;
  return str.replace(/\bnan\b/gi, "").replace(/\s+/g, " ").trim();
};

const Dashboard = () => {
  const { allowedPages, canAccess } = useAuth();

  const [students, setStudents] = useState([]);
  const [alerts, setAlerts]     = useState([]);
  const [loading, setLoading]   = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [selected, setSelected] = useState(null);
  const [query, setQuery]       = useState("");
  const [notice, setNotice]     = useState("");
  const [activePage, setActivePage] = useState(() => allowedPages[0] ?? "inicio");
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;
  const [sortConfig, setSortConfig] = useState({
    key: "promedio_academico",
    direction: "desc",
  });
  const [semesterEvolution, setSemesterEvolution] = useState([]);
  const [featureImportance, setFeatureImportance] = useState([]);

  // Keep activePage in sync if role changes or page is no longer accessible
  useEffect(() => {
    if (!canAccess(activePage)) {
      setActivePage(allowedPages[0] ?? "inicio");
    }
  }, [allowedPages, activePage, canAccess]);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const [studentsResponse, alertsResponse] = await Promise.all([
          getStudents(1, 500),
          getAlerts(),
        ]);
        const cleanedStudents = (studentsResponse.items || []).map((s) => ({
          ...s,
          nombre: cleanString(s.nombre),
        }));
        const cleanedAlerts = (alertsResponse.items || []).map((a) => ({
          ...a,
          nombre: cleanString(a.nombre),
        }));
        setStudents(cleanedStudents);
        setAlerts(cleanedAlerts);
        setNotice("");
      } catch (error) {
        console.error("[app] data load failed", error);
        setNotice("No se pudo cargar la información. Revisa el backend.");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  useEffect(() => {
    if (activePage !== "reportes") return;
    if (semesterEvolution.length && featureImportance.length) return;
    Promise.all([
      getReportsSemesterEvolution(),
      getFeatureImportance(),
    ])
      .then(([semData, featData]) => {
        setSemesterEvolution(semData.semesters || []);
        setFeatureImportance(featData.features || []);
      })
      .catch((err) => console.error("[app] reports charts load failed", err));
  }, [activePage, semesterEvolution.length, featureImportance.length]);

  const stats = useMemo(() => {
    if (!students.length) return { total: 0, highRisk: 0, retention: 0 };
    const highRisk = students.filter((s) => s.riesgo_nivel === "Alto").length;
    const avgRisk  = students.reduce((sum, s) => sum + s.riesgo_probabilidad, 0) / students.length;
    const retention = Math.max(0, Math.round((1 - avgRisk) * 100));
    return { total: students.length, highRisk, retention };
  }, [students]);

  const riskCounts = useMemo(() =>
    students.reduce(
      (acc, s) => { acc[s.riesgo_nivel] = (acc[s.riesgo_nivel] || 0) + 1; return acc; },
      { Alto: 0, Medio: 0, Bajo: 0 }
    ),
  [students]);

  const searchedStudents = useMemo(() => {
    if (!query.trim()) return students;
    const value = query.toLowerCase();
    return students.filter(
      (s) => s.nombre?.toLowerCase().includes(value) || s.programa_academico?.toLowerCase().includes(value)
    );
  }, [query, students]);

  const sortedStudents = useMemo(() => {
    const list = [...searchedStudents];
    if (!sortConfig.key) return list;
    const riskRank = { Bajo: 1, Medio: 2, Alto: 3 };
    list.sort((l, r) => {
      let lv = l[sortConfig.key];
      let rv = r[sortConfig.key];
      if (sortConfig.key === "riesgo_nivel") { lv = riskRank[lv] || 0; rv = riskRank[rv] || 0; }
      const ln = Number(lv);
      const rn = Number(rv);
      if (!Number.isNaN(ln) && !Number.isNaN(rn)) return ln - rn;
      return String(lv || "").localeCompare(String(rv || ""));
    });
    if (sortConfig.direction === "desc") list.reverse();
    return list;
  }, [searchedStudents, sortConfig]);

  const totalPages = Math.max(1, Math.ceil(sortedStudents.length / pageSize));

  useEffect(() => { setCurrentPage(1); }, [query, sortConfig, students.length]);
  useEffect(() => { if (currentPage > totalPages) setCurrentPage(totalPages); }, [currentPage, totalPages]);

  const pagedStudents = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return sortedStudents.slice(start, start + pageSize);
  }, [sortedStudents, currentPage]);

  const criticalAlerts = useMemo(() =>
    [...alerts].sort((l, r) => r.riesgo_probabilidad - l.riesgo_probabilidad),
  [alerts]);

  const riskDrivers = useMemo(() => {
    const summary = { financial: 0, academic: 0, attendance: 0 };
    students.forEach((s) => {
      if (s.riesgo_nivel !== "Alto") return;
      const estadoPagos = String(s.estado_pagos || "").toLowerCase();
      const mora        = Number(s.mora_matricula);
      const promedio    = Number(s.promedio_academico);
      const perdidas    = Number(s.materias_perdidas);
      const asistencia  = Number(s.asistencia_clases);
      if (mora === 1 || estadoPagos.includes("mora") || estadoPagos.includes("parcial")) summary.financial += 1;
      if ((Number.isFinite(promedio) && promedio < 3) || perdidas >= 5) summary.academic += 1;
      if (Number.isFinite(asistencia) && asistencia < 70) summary.attendance += 1;
    });
    return summary;
  }, [students]);

  const handleSelect = async (studentId) => {
    try {
      setDetailLoading(true);
      const detail = await getStudentDetail(studentId);
      detail.data.primer_nombre    = cleanString(detail.data.primer_nombre);
      detail.data.primer_apellido  = cleanString(detail.data.primer_apellido);
      setSelected(detail);
    } catch {
      setNotice("No se pudo cargar el detalle del estudiante.");
    } finally {
      setDetailLoading(false);
    }
  };

  const renderPage = () => {
    switch (activePage) {
      case "inicio":
        return (
          <>
            <Header />
            <section className="metrics">
              <MetricCard label="Total estudiantes"  value={stats.total}             hint="Base activa" />
              <MetricCard label="Riesgo alto"         value={stats.highRisk}          hint="Prioridad"   />
              <MetricCard label="Retención estimada"  value={`${stats.retention}%`}  hint="Simulada"    />
            </section>
            <section className="grid-two">
              <div className="panel">
                <div className="panel-header"><h2>Mapa de riesgo</h2><span>Distribución</span></div>
                <RiskDonut counts={riskCounts} />
              </div>
              <div className="panel">
                <div className="panel-header"><h2>Alertas críticas</h2><span>{criticalAlerts.length} casos críticos</span></div>
                <CriticalAlerts alerts={criticalAlerts} />
              </div>
            </section>
          </>
        );
      case "resumen":
        return (
          <>
            <section className="panel">
              <div className="panel-header">
                <div><h2>Resumen ejecutivo</h2><p>Vista general de riesgo y retención</p></div>
              </div>
              <div className="metrics">
                <MetricCard label="Total estudiantes"  value={stats.total}            hint="Base activa" />
                <MetricCard label="Riesgo alto"         value={stats.highRisk}         hint="Prioridad"   />
                <MetricCard label="Retención estimada"  value={`${stats.retention}%`} hint="Simulada"    />
              </div>
            </section>
            <section className="panel">
              <div className="panel-header">
                <div><h2>Focos prioritarios</h2><p>Detonantes frecuentes en riesgo alto</p></div>
              </div>
              <div className="report-grid">
                <div className="report-card">
                  <span className="eyebrow">Alertas financieras</span>
                  <h3>{riskDrivers.financial} casos</h3>
                  <p>Mora o pagos parciales detectados.</p>
                </div>
                <div className="report-card">
                  <span className="eyebrow">Alertas académicas</span>
                  <h3>{riskDrivers.academic} casos</h3>
                  <p>Promedios bajos o materias perdidas.</p>
                </div>
                <div className="report-card">
                  <span className="eyebrow">Alertas de asistencia</span>
                  <h3>{riskDrivers.attendance} casos</h3>
                  <p>Asistencia por debajo del umbral mínimo.</p>
                </div>
              </div>
            </section>
          </>
        );
      case "analitica":
        return (
          <section className="grid-two">
            <div className="panel">
              <div className="panel-header"><h2>Mapa de riesgo</h2><span>Distribución</span></div>
              <RiskDonut counts={riskCounts} />
            </div>
            <div className="panel">
              <div className="panel-header"><h2>Alertas críticas</h2><span>{criticalAlerts.length} casos críticos</span></div>
              <CriticalAlerts alerts={criticalAlerts} />
            </div>
          </section>
        );
      case "estudiantes":
        return (
          <section className="panel table-panel">
            <div className="panel-header">
              <div><h2>Tabla de estudiantes</h2><p>{sortedStudents.length} registros</p></div>
              <SearchBar value={query} onChange={setQuery} placeholder="Buscar por nombre o programa" />
            </div>
            <StudentTable
              students={pagedStudents}
              loading={loading}
              onSelect={handleSelect}
              sortConfig={sortConfig}
              onSortChange={setSortConfig}
              page={currentPage}
              totalPages={totalPages}
              onPageChange={setCurrentPage}
            />
          </section>
        );
      case "prediccion":
        return (
          <div className="page"><StudentInferenceForm /></div>
        );
      case "intervenciones":
        return (
          <div className="page">
            <InterventionForm studentId={selected?.data?.id_estudiante} onSubmitSuccess={() => {}} />
          </div>
        );
      case "alertas":
        return (
          <section className="panel">
            <div className="panel-header">
              <div><h2>Panel de alertas</h2><p>{alerts.length} alertas en seguimiento</p></div>
            </div>
            <AlertsPanel alerts={alerts} loading={loading} />
          </section>
        );
      case "reportes": {
        const distData = [
          { level: "Alto",  count: riskCounts.Alto,  percentage: stats.total ? Math.round((riskCounts.Alto  / stats.total) * 100) : 0 },
          { level: "Medio", count: riskCounts.Medio, percentage: stats.total ? Math.round((riskCounts.Medio / stats.total) * 100) : 0 },
          { level: "Bajo",  count: riskCounts.Bajo,  percentage: stats.total ? Math.round((riskCounts.Bajo  / stats.total) * 100) : 0 },
        ];
        return (
          <section className="panel reportes">
            <div className="panel-header">
              <div><h2>Reportes ejecutivos</h2><p>Resumen para comités y bienestar</p></div>
            </div>
            <div className="report-filters">
              <label><span>Periodo</span>
                <select className="filter-select">
                  <option>Semestre actual</option><option>Semestre anterior</option>
                </select>
              </label>
              <label><span>Programa</span>
                <select className="filter-select">
                  <option>Todos</option><option>Ingeniería de Sistemas</option>
                </select>
              </label>
              <label><span>Tipo</span>
                <select className="filter-select">
                  <option>Ejecutivo</option><option>Detallado</option>
                </select>
              </label>
              <button type="button" className="action-button">Generar reporte</button>
            </div>
            <div className="report-grid">
              <div className="report-card">
                <span className="eyebrow">Riesgo alto</span>
                <h3>{stats.highRisk} estudiantes</h3>
                <p>Listado priorizado para intervención inmediata.</p>
              </div>
              <div className="report-card">
                <span className="eyebrow">Retención</span>
                <h3>{stats.retention}%</h3>
                <p>Proyección de retención con base en riesgo actual.</p>
              </div>
              <div className="report-card">
                <span className="eyebrow">Alertas</span>
                <h3>{alerts.length} activas</h3>
                <p>Seguimiento semanal con responsables asignados.</p>
              </div>
            </div>

            <div className="charts-grid">
              <div className="chart-card">
                <h4 className="chart-title">Distribución de riesgo</h4>
                <p className="chart-subtitle">Conteo de estudiantes por nivel de riesgo predicho</p>
                <RiskDistributionChart distribution={distData} />
              </div>
              <div className="chart-card">
                <h4 className="chart-title">Evolución por semestre</h4>
                <p className="chart-subtitle">Distribución de riesgo acumulada por semestre cursado</p>
                <SemesterEvolutionChart semesters={semesterEvolution} />
              </div>
              <div className="chart-card chart-card--wide">
                <h4 className="chart-title">Feature importance del modelo de riesgo</h4>
                <p className="chart-subtitle">Peso relativo de cada variable en la predicción del modelo Random Forest</p>
                <FeatureImportanceChart features={featureImportance} />
              </div>
            </div>
          </section>
        );
      }
      default:
        return null;
    }
  };

  return (
    <div className="shell">
      <Sidebar active={activePage} onSelect={setActivePage} />
      <div className="content">
        <Topbar page={pageLabels[activePage] || "Inicio"} />
        <div className="app">
          {notice && (
            <div className="notice">
              <span>{notice}</span>
              <button type="button" onClick={() => setNotice("")}>Cerrar</button>
            </div>
          )}
          <div className="page">{renderPage()}</div>

          {selected && (
            <StudentDetailModal
              detail={selected}
              loading={detailLoading}
              onClose={() => setSelected(null)}
            />
          )}
        </div>
      </div>
    </div>
  );
};

const App = () => {
  const { user } = useAuth();
  return user ? <Dashboard /> : <LoginPage />;
};

const Root = () => (
  <AuthProvider>
    <App />
  </AuthProvider>
);

export default Root;
