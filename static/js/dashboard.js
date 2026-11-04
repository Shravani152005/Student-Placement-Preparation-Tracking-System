/**
 * dashboard.js - Chart.js integrations for Placement Analytics Dashboard
 * Visualizes aptitude score progression, coding problem distributions, and job CRM stages.
 */

document.addEventListener("DOMContentLoaded", () => {
  initDashboardCharts();
});

async function initDashboardCharts() {
  const aptChartCanvas = document.getElementById("aptitudeTrendChart");
  const jobChartCanvas = document.getElementById("jobDistributionChart");
  const codingChartCanvas = document.getElementById("codingBreakdownChart");

  if (!aptChartCanvas && !jobChartCanvas && !codingChartCanvas) return;

  try {
    const res = await fetch("/api/dashboard-charts");
    if (!res.ok) throw new Error("Failed to load chart data");
    const data = await res.json();

    // 1. Aptitude Score Progression Line Chart
    if (aptChartCanvas) {
      const ctx = aptChartCanvas.getContext("2d");
      const gradient = ctx.createLinearGradient(0, 0, 0, 250);
      gradient.addColorStop(0, "rgba(13, 148, 136, 0.35)");
      gradient.addColorStop(1, "rgba(13, 148, 136, 0.0)");

      new Chart(aptChartCanvas, {
        type: "line",
        data: {
          labels: data.aptitude_trend.labels,
          datasets: [
            {
              label: "Score (%)",
              data: data.aptitude_trend.data,
              borderColor: "#0d9488",
              backgroundColor: gradient,
              borderWidth: 2.5,
              tension: 0.35,
              fill: true,
              pointBackgroundColor: "#0f766e",
              pointRadius: 4,
              pointHoverRadius: 6,
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
                label: (ctx) => `Score: ${ctx.parsed.y}%`,
              },
            },
          },
          scales: {
            y: {
              min: 0,
              max: 100,
              ticks: { stepSize: 20 },
              grid: { color: "#f1f5f9" },
            },
            x: {
              grid: { display: false },
            },
          },
        },
      });
    }

    // 2. Job Application Status Distribution (Doughnut)
    if (jobChartCanvas) {
      new Chart(jobChartCanvas, {
        type: "doughnut",
        data: {
          labels: data.job_distribution.labels,
          datasets: [
            {
              data: data.job_distribution.data,
              backgroundColor: [
                "#0284c7", // Applied (Blue)
                "#6366f1", // Shortlisted (Indigo)
                "#f59e0b", // Interview (Amber)
                "#10b981", // Selected (Green)
                "#ef4444", // Rejected (Red)
              ],
              borderWidth: 2,
              borderColor: "#ffffff",
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: "68%",
          plugins: {
            legend: {
              position: "bottom",
              labels: {
                boxWidth: 12,
                padding: 12,
                font: { size: 11, weight: "600" },
              },
            },
          },
        },
      });
    }

    // 3. Coding Problems Breakdown (Horizontal Bar)
    if (codingChartCanvas) {
      new Chart(codingChartCanvas, {
        type: "bar",
        data: {
          labels: ["Easy", "Medium", "Hard", "In Progress", "Need Revision"],
          datasets: [
            {
              label: "Count",
              data: [
                data.coding_distribution.data[0], // Easy
                data.coding_distribution.data[1], // Medium
                data.coding_distribution.data[2], // Hard
                data.coding_distribution.data[3], // In Progress
                data.coding_distribution.data[4], // Need Revision
              ],
              backgroundColor: [
                "#10b981",
                "#f59e0b",
                "#ef4444",
                "#38bdf8",
                "#a855f7",
              ],
              borderRadius: 6,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          indexAxis: "y",
          plugins: {
            legend: { display: false },
          },
          scales: {
            x: {
              beginAtZero: true,
              ticks: { precision: 0 },
              grid: { color: "#f1f5f9" },
            },
            y: {
              grid: { display: false },
            },
          },
        },
      });
    }
  } catch (err) {
    console.error("Error loading dashboard charts:", err);
  }
}
