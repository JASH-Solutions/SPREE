import { useEffect, useRef } from "react";
import Chart from "chart.js/auto";

const RiskDonut = ({ counts }) => {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);

  useEffect(() => {
    if (!canvasRef.current) return;

    if (chartRef.current) {
      chartRef.current.destroy();
    }

    const total = counts.Alto + counts.Medio + counts.Bajo;

    // Etiqueta central con el total
    const centerText = {
      id: "centerText",
      afterDraw(chart) {
        const { ctx } = chart;
        const { width, height } = chart;
        ctx.save();
        ctx.fillStyle = "#1f1f1f";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.font = "600 24px 'Unbounded', sans-serif";
        ctx.fillText(String(total), width / 2, height / 2 - 8);
        ctx.font = "500 12px 'Space Grotesk', sans-serif";
        ctx.fillText("Total", width / 2, height / 2 + 14);
        ctx.restore();
      },
    };

    const labels = [
      `Alto (${total ? Math.round((counts.Alto / total) * 100) : 0}%)`,
      `Medio (${total ? Math.round((counts.Medio / total) * 100) : 0}%)`,
      `Bajo (${total ? Math.round((counts.Bajo / total) * 100) : 0}%)`,
    ];

    chartRef.current = new Chart(canvasRef.current, {
      type: "doughnut",
      data: {
        labels,
        datasets: [
          {
            data: [counts.Alto, counts.Medio, counts.Bajo],
            // Colores Semánticos (Rojo, Ámbar, Verde) en lugar de marca
            backgroundColor: ["#b3261e", "#b26a00", "#137333"], 
            borderColor: "#ffffff",
            borderWidth: 2,
          },
        ],
      },
      options: {
        cutout: "75%",
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "bottom", // Leyenda clara y accesible abajo
            labels: { color: "#1b1b1b", boxWidth: 12, boxHeight: 12, padding: 16 },
          },
        },
      },
      plugins: [centerText],
    });

    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
      }
    };
  }, [counts]);

  return (
    // Se agregó limitación de tamaño en CSS para que no robe tanta pantalla
    <div className="donut-wrapper">
      <canvas ref={canvasRef} height="220"></canvas>
    </div>
  );
};

export default RiskDonut;