import { useEffect, useRef } from "react";
import Chart from "chart.js/auto";

const COLORS = { Alto: "#b3261e", Medio: "#b26a00", Bajo: "#137333" };

const RiskDistributionChart = ({ distribution }) => {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);

  useEffect(() => {
    if (!canvasRef.current || !distribution?.length) return;
    if (chartRef.current) chartRef.current.destroy();

    chartRef.current = new Chart(canvasRef.current, {
      type: "bar",
      data: {
        labels: distribution.map((d) => d.level),
        datasets: [
          {
            label: "Estudiantes",
            data: distribution.map((d) => d.count),
            backgroundColor: distribution.map((d) => COLORS[d.level] ?? "#999"),
            borderRadius: 8,
            borderSkipped: false,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const item = distribution[ctx.dataIndex];
                return ` ${item.count} estudiantes (${item.percentage}%)`;
              },
            },
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: { color: "rgba(0,0,0,0.05)" },
            ticks: { color: "#444", precision: 0 },
          },
          x: {
            grid: { display: false },
            ticks: { color: "#444", font: { weight: "600" } },
          },
        },
      },
    });

    return () => {
      if (chartRef.current) chartRef.current.destroy();
    };
  }, [distribution]);

  return (
    <div className="chart-canvas-wrapper">
      <canvas ref={canvasRef} />
    </div>
  );
};

export default RiskDistributionChart;
