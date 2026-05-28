import { useEffect, useRef } from "react";
import Chart from "chart.js/auto";

const SemesterEvolutionChart = ({ semesters }) => {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);

  useEffect(() => {
    if (!canvasRef.current || !semesters?.length) return;
    if (chartRef.current) chartRef.current.destroy();

    chartRef.current = new Chart(canvasRef.current, {
      type: "bar",
      data: {
        labels: semesters.map((s) => `Sem. ${s.semester}`),
        datasets: [
          {
            label: "Alto",
            data: semesters.map((s) => s.Alto),
            backgroundColor: "#b3261e",
            borderRadius: 4,
            stack: "risk",
          },
          {
            label: "Medio",
            data: semesters.map((s) => s.Medio),
            backgroundColor: "#b26a00",
            borderRadius: 4,
            stack: "risk",
          },
          {
            label: "Bajo",
            data: semesters.map((s) => s.Bajo),
            backgroundColor: "#137333",
            borderRadius: 4,
            stack: "risk",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "bottom",
            labels: { color: "#1b1b1b", boxWidth: 12, boxHeight: 12, padding: 16 },
          },
        },
        scales: {
          x: {
            stacked: true,
            grid: { display: false },
            ticks: { color: "#444" },
          },
          y: {
            stacked: true,
            beginAtZero: true,
            grid: { color: "rgba(0,0,0,0.05)" },
            ticks: { color: "#444", precision: 0 },
          },
        },
      },
    });

    return () => {
      if (chartRef.current) chartRef.current.destroy();
    };
  }, [semesters]);

  return (
    <div className="chart-canvas-wrapper">
      <canvas ref={canvasRef} />
    </div>
  );
};

export default SemesterEvolutionChart;
