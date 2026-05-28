import { useEffect, useMemo, useState } from "react";

import { getAlerts, getStudentDetail, getStudents } from "./api/client";
import AlertsPanel from "./components/AlertsPanel";
import CriticalAlerts from "./components/CriticalAlerts";
import Header from "./components/Header";
import InterventionForm from "./components/InterventionForm";
import MetricCard from "./components/MetricCard";
import RiskDonut from "./components/RiskDonut";
import SearchBar from "./components/SearchBar";
import Sidebar from "./components/Sidebar";
import StudentDetailModal from "./components/StudentDetailModal";
import StudentInferenceForm from "./components/StudentInferenceForm";
import StudentTable from "./components/StudentTable";
import Topbar from "./components/Topbar";

const App = () => {
  const [students, setStudents] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [selected, setSelected] = useState(null);
  const [query, setQuery] = useState("");
  const [notice, setNotice] = useState("");
  const [activePage, setActivePage] = useState("inicio");
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;
  const [sortConfig, setSortConfig] = useState({
    key: "promedio_academico",
    direction: "desc",
  });

  // Limpiador de "nan" para Data Binding
  const cleanString = (str) => {
    if (!str || typeof str !== 'string') return str;
    return str.replace(/\bnan\b/gi, '').replace(/\s+/g, ' ').trim();
  };

  useEffect(() => {
    const load = async () => {
      try {
        console.debug("[app] loading data...");
        setLoading(true);
        const [studentsResponse, alertsResponse] = await Promise.all([
          getStudents(1, 500),
          getAlerts(),
        ]);
        
        // Aplicamos la limpieza de Nulos ("nan") antes de guardar en estado
        const cleanedStudents = (studentsResponse.items || []).map(s => ({
          ...s,
          nombre: cleanString(s.nombre)
        }));
        const cleanedAlerts = (alertsResponse.items || []).map(a => ({
          ...a,
          nombre: cleanString(a.nombre)
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

  const stats = useMemo(() => {
    if (!students.length) {
      return { total: 0, highRisk: 0, retention: 0 };
    }
    const highRisk = students.filter((item) => item.riesgo_nivel === "Alto").length;
    const avgRisk =
      students.reduce((sum, item) => sum + item.riesgo_probabilidad, 0) /
      students.length;
    const retention = Math.max(0, Math.round((1 - avgRisk) * 100));
    return { total: students.length, highRisk, retention };
  }, [students]);

  const riskCounts = useMemo(() => {
    return students.reduce(
      (acc, student) => {
        acc[student.riesgo_nivel] = (acc[student.riesgo_nivel] || 0) + 1;
        return acc;
      },
      { Alto: 0, Medio: 0, Bajo: 0 }
    );
  }, [students]);

  const searchedStudents = useMemo(() => {
    if (!query.trim()) return students;
    const value = query.toLowerCase();
    return students.filter((student) => {
      const nameMatch = student.nombre?.toLowerCase().includes(value);
      const programMatch = student.programa_academico
        ?.toLowerCase()
        .includes(value);
      return nameMatch || programMatch;
    });
  }, [query, students]);

  const sortedStudents = useMemo(() => {
    const list = [...searchedStudents];
    if (!sortConfig.key) return list;

    const riskRank = { Bajo: 1, Medio: 2, Alto: 3 };

    list.sort((left, right) => {
      let leftValue = left[sortConfig.key];
      let rightValue = right[sortConfig.key];

      if (sortConfig.key === "riesgo_nivel") {
        leftValue = riskRank[leftValue] || 0;
        rightValue = riskRank[rightValue] || 0;
      }

      const leftNumber = Number(leftValue);
      const rightNumber = Number(rightValue);
      const bothNumbers = !Number.isNaN(leftNumber) && !Number.isNaN(rightNumber);

      if (bothNumbers) {
        return leftNumber - rightNumber;
      }

      return String(leftValue || "").localeCompare(String(rightValue || ""));
    });

    if (sortConfig.direction === "desc") {
      list.reverse();
    }

    return list;
  }, [searchedStudents, sortConfig]);

  const totalPages = Math.max(1, Math.ceil(sortedStudents.length / pageSize));

  useEffect(() => {
    setCurrentPage(1);
  }, [query, sortConfig, students.length]);

  useEffect(() => {
    if (currentPage > totalPages) {
      setCurrentPage(totalPages);
    }
  }, [currentPage, totalPages]);

  const pagedStudents = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return sortedStudents.slice(start, start + pageSize);
  }, [sortedStudents, currentPage]);

  const criticalAlerts = useMemo(() => {
    return [...alerts].sort(
      (left, right) => right.riesgo_probabilidad - left.riesgo_probabilidad
    );
  }, [alerts]);

  const riskDrivers = useMemo(() => {
    const summary = { financial: 0, academic: 0, attendance: 0 };
    students.forEach((student) => {
      if (student.riesgo_nivel !== "Alto") return;

      const estadoPagos = String(student.estado_pagos || "").toLowerCase();
      const mora = Number(student.mora_matricula);
      const promedio = Number(student.promedio_academico);
      const perdidas = Number(student.materias_perdidas);
      const asistencia = Number(student.asistencia_clases);

      if (mora === 1 || estadoPagos.includes("mora") || estadoPagos.includes("parcial")) {
        summary.financial += 1;
      }
      if ((Number.isFinite(promedio) && promedio < 3) || perdidas >= 5) {
        summary.academic += 1;
      }
      if (Number.isFinite(asistencia) && asistencia < 70) {
        summary.attendance += 1;
      }
    });
    return summary;
  }, [students]);

  const pageLabels = {
    inicio: "Inicio",
    resumen: "Resumen",
    analitica: "Analítica",
    estudiantes: "Estudiantes",
    prediccion: "Predicción",
    intervenciones: "Intervenciones",
    alertas: "Alertas",
    reportes: "Reportes",
  };

  const renderPage = () => {
    switch (activePage) {
      case "inicio":
        return (
          <>
            <Header />

            <section className="metrics">
              <MetricCard label="Total estudiantes" value={stats.total} hint="Base activa" />
              <MetricCard label="Riesgo alto" value={stats.highRisk} hint="Prioridad" />
              <MetricCard
                label="Retención estimada"
                value={`${stats.retention}%`}
                hint="Simulada"
              />
            </section>

            <section className="grid-two">
              <div className="panel">
                <div className="panel-header">
                  <h2>Mapa de riesgo</h2>
                  <span>Distribución</span>
                </div>
                <RiskDonut counts={riskCounts} />
              </div>
              <div className="panel">
                <div className="panel-header">
                  <h2>Alertas críticas</h2>
                  <span>{criticalAlerts.length} casos críticos</span>
                </div>
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
                <div>
                  <h2>Resumen ejecutivo</h2>
                  <p>Vista general de riesgo y retención</p>
                </div>
              </div>
              <div className="metrics">
                <MetricCard label="Total estudiantes" value={stats.total} hint="Base activa" />
                <MetricCard label="Riesgo alto" value={stats.highRisk} hint="Prioridad" />
                <MetricCard
                  label="Retención estimada"
                  value={`${stats.retention}%`}
                  hint="Simulada"
                />
              </div>
            </section>
            <section className="panel">
              <div className="panel-header">
                <div>
                  <h2>Focos prioritarios</h2>
                  <p>Detonantes frecuentes en riesgo alto</p>
                </div>
              </div>
              {/* Aquí usamos los datos desglosados y no los redundantes */}
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
              <div className="panel-header">
                <h2>Mapa de riesgo</h2>
                <span>Distribución</span>
              </div>
              <RiskDonut counts={riskCounts} />
            </div>
            <div className="panel">
              <div className="panel-header">
                <h2>Alertas críticas</h2>
                <span>{criticalAlerts.length} casos críticos</span>
              </div>
              <CriticalAlerts alerts={criticalAlerts} />
            </div>
          </section>
        );
      case "estudiantes":
        return (
          <section className="panel table-panel">
            <div className="panel-header">
              <div>
                <h2>Tabla de estudiantes</h2>
                <p>{sortedStudents.length} registros</p>
              </div>
              <SearchBar
                value={query}
                onChange={setQuery}
                placeholder="Buscar por nombre o programa"
              />
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
          <div className="page">
            <StudentInferenceForm />
          </div>
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
              <div>
                <h2>Panel de alertas</h2>
                <p>{alerts.length} alertas en seguimiento</p>
              </div>
            </div>
            <AlertsPanel alerts={alerts} loading={loading} />
          </section>
        );
      case "reportes":
        return (
          <section className="panel reportes">
            <div className="panel-header">
              <div>
                <h2>Reportes ejecutivos</h2>
                <p>Resumen para comités y bienestar</p>
              </div>
            </div>
            <div className="report-filters">
              <label>
                <span>Periodo</span>
                <select className="filter-select">
                  <option>Semestre actual</option>
                  <option>Semestre anterior</option>
                </select>
              </label>
              <label>
                <span>Programa</span>
                <select className="filter-select">
                  <option>Todos</option>
                  <option>Ingeniería de Sistemas</option>
                </select>
              </label>
              <label>
                <span>Tipo</span>
                <select className="filter-select">
                  <option>Ejecutivo</option>
                  <option>Detallado</option>
                </select>
              </label>
              <button type="button" className="action-button">
                Generar reporte
              </button>
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
          </section>
        );
      default:
        return null;
    }
  };

  const handleSelect = async (studentId) => {
    try {
      setDetailLoading(true);
      const detail = await getStudentDetail(studentId);
      detail.data.primer_nombre = cleanString(detail.data.primer_nombre);
      detail.data.primer_apellido = cleanString(detail.data.primer_apellido);
      setSelected(detail);
    } catch (error) {
      setNotice("No se pudo cargar el detalle del estudiante.");
    } finally {
      setDetailLoading(false);
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

export default App;