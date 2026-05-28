import { useEffect, useRef } from "react";
import Chart from "chart.js/auto";

const FeatureImportanceChart = ({ features }) => {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);

  useEffect(() => {
    if (!canvasRef.current || !features?.length) return;
    if (chartRef.current) chartRef.current.destroy();

    const sorted = [...features].sort((a, b) => b.importance - a.importance);
    const maxImp = sorted[0]?.importance ?? 1;

    chartRef.current = new Chart(canvasRef.current, {
      type: "bar",
      data: {
        labels: sorted.map((f) => f.label),
        datasets: [
          {
            label: "Importancia",
            data: sorted.map((f) => f.importance),
            backgroundColor: sorted.map((_, i) =>
              `rgba(4, 28, 59, ${Math.max(1 - i * 0.14, 0.25)})`
            ),
            borderRadius: 4,
            borderSkipped: false,
          },
        ],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => ` ${(ctx.raw * 100).toFixed(1)}%`,
            },
          },
        },
        scales: {
          x: {
            beginAtZero: true,
            max: maxImp * 1.15,
            grid: { color: "rgba(0,0,0,0.05)" },
            ticks: {
              color: "#444",
              callback: (v) => `${(v * 100).toFixed(0)}%`,
            },
          },
          y: {
            grid: { display: false },
            ticks: { color: "#333", font: { size: 12 } },
          },
        },
      },
    });

    return () => {
      if (chartRef.current) chartRef.current.destroy();
    };
  }, [features]);

  return (
    <div className="chart-canvas-wrapper chart-canvas-horizontal">
      <canvas ref={canvasRef} />
    </div>
  );
};

export default FeatureImportanceChart;
