let currentChart = null;

function updateChart(chartType) {
  if (currentChart) {
    currentChart.destroy();
  }

  const ctx = document.getElementById("resultsChart").getContext("2d");

  switch (chartType) {
    case "bar":
      currentChart = createBarChart(ctx);
      break;
    case "line":
      currentChart = createLineChart(ctx);
      break;
    case "pie":
      currentChart = createPieChart(ctx);
      break;
    case "stacked":
      currentChart = createStackedChart(ctx);
      break;
    case "scatter":
      currentChart = createScatterChart(ctx);
      break;
    case "comparison":
      currentChart = createComparisonChart(ctx);
      break;
    case "improvement":
      currentChart = createImprovementChart(ctx);
      break;
  }
}

function createBarChart(ctx) {
  const labels = latestResults.map((_, i) => `Sensor ${i + 1}`);
  const datasets = [];

  const firstResult = latestResults[0];
  if (firstResult.impact) {
    datasets.push({
      label: "Original Congestion",
      data: latestResults.map((d) => d.impact?.original_congestion || 0),
      backgroundColor: "rgba(255, 99, 132, 0.8)",
      borderColor: "rgba(255, 99, 132, 1)",
      borderWidth: 1,
    });
    datasets.push({
      label: "Optimized Congestion",
      data: latestResults.map((d) => d.impact?.optimized_congestion || 0),
      backgroundColor: "rgba(75, 192, 192, 0.8)",
      borderColor: "rgba(75, 192, 192, 1)",
      borderWidth: 1,
    });
  }

  return new Chart(ctx, {
    type: "bar",
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: "#ddd" } },
        title: {
          display: true,
          text: "Congestion Levels - Before vs After Optimization",
          color: "#fff",
        },
      },
      scales: {
        x: { ticks: { color: "#aaa" } },
        y: { ticks: { color: "#aaa" }, beginAtZero: true },
      },
    },
  });
}

function createLineChart(ctx) {
  const labels = latestResults.map((_, i) => `Sensor ${i + 1}`);
  const datasets = [];

  const firstResult = latestResults[0];
  if (firstResult.impact) {
    datasets.push({
      label: "Original Congestion",
      data: latestResults.map((d) => d.impact?.original_congestion || 0),
      borderColor: "rgba(255, 205, 86, 1)",
      backgroundColor: "rgba(255, 205, 86, 0.1)",
      tension: 0.4,
      fill: true,
    });
    datasets.push({
      label: "Optimized Congestion",
      data: latestResults.map((d) => d.impact?.optimized_congestion || 0),
      borderColor: "rgba(153, 102, 255, 1)",
      backgroundColor: "rgba(153, 102, 255, 0.1)",
      tension: 0.4,
      fill: true,
    });
  }

  return new Chart(ctx, {
    type: "line",
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: "#ddd" } },
        title: {
          display: true,
          text: "Congestion Trends - Before vs After Optimization",
          color: "#fff",
        },
      },
      scales: {
        x: { ticks: { color: "#aaa" } },
        y: { ticks: { color: "#aaa" }, beginAtZero: true },
      },
    },
  });
}

function createPieChart(ctx) {
  // Categorizar las mejoras
  const improvements = latestResults.map((d) => {
    const original = d.impact?.original_congestion || 0;
    const optimized = d.impact?.optimized_congestion || 0;
    return original > 0 ? ((original - optimized) / original) * 100 : 0;
  });

  const excellent = improvements.filter((imp) => imp >= 50).length;
  const good = improvements.filter((imp) => imp >= 25 && imp < 50).length;
  const moderate = improvements.filter((imp) => imp >= 10 && imp < 25).length;
  const low = improvements.filter((imp) => imp >= 0 && imp < 10).length;
  const noImprovement = improvements.filter((imp) => imp < 0).length;

  const labels = [
    "Excellent (≥50%)",
    "Good (25-49%)",
    "Moderate (10-24%)",
    "Low (0-9%)",
    "No Improvement",
  ];
  const data = [excellent, good, moderate, low, noImprovement];

  return new Chart(ctx, {
    type: "pie",
    data: {
      labels,
      datasets: [
        {
          data,
          backgroundColor: [
            "rgba(75, 192, 192, 0.8)", // Excellent - Green
            "rgba(54, 162, 235, 0.8)", // Good - Blue
            "rgba(255, 205, 86, 0.8)", // Moderate - Yellow
            "rgba(255, 159, 64, 0.8)", // Low - Orange
            "rgba(255, 99, 132, 0.8)", // No Improvement - Red
          ],
          borderColor: [
            "rgba(75, 192, 192, 1)",
            "rgba(54, 162, 235, 1)",
            "rgba(255, 205, 86, 1)",
            "rgba(255, 159, 64, 1)",
            "rgba(255, 99, 132, 1)",
          ],
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: "#ddd" },
          position: "bottom",
        },
        title: {
          display: true,
          text: "Distribution of Improvement Levels",
          color: "#fff",
        },
      },
    },
  });
}

function createStackedChart(ctx) {
  const labels = latestResults.map((_, i) => `Sensor ${i + 1}`);
  const greenTimes = latestResults.map(
    (d) => d.optimization?.green_time_sec || 0
  );
  const redTimes = latestResults.map((d) => d.optimization?.red_time_sec || 0);

  return new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Green Time",
          data: greenTimes,
          backgroundColor: "rgba(75, 192, 192, 0.8)",
          borderColor: "rgba(75, 192, 192, 1)",
          borderWidth: 1,
        },
        {
          label: "Red Time",
          data: redTimes,
          backgroundColor: "rgba(255, 99, 132, 0.8)",
          borderColor: "rgba(255, 99, 132, 1)",
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: "#ddd" } },
        title: {
          display: true,
          text: "Traffic Light Timing Distribution",
          color: "#fff",
        },
      },
      scales: {
        x: {
          ticks: { color: "#aaa" },
          stacked: true,
        },
        y: {
          ticks: { color: "#aaa" },
          beginAtZero: true,
          stacked: true,
        },
      },
    },
  });
}

function createScatterChart(ctx) {
  const originalData = latestResults.map(
    (d) => d.impact?.original_congestion || 0
  );
  const optimizedData = latestResults.map(
    (d) => d.impact?.optimized_congestion || 0
  );

  // Crear línea de referencia (y = x)
  const maxValue = Math.max(...originalData, ...optimizedData);
  const referenceLine = Array.from({ length: 2 }, (_, i) => i * maxValue);

  return new Chart(ctx, {
    type: "scatter",
    data: {
      datasets: [
        {
          label: "Optimization Results",
          data: originalData.map((value, index) => ({
            x: value,
            y: optimizedData[index],
          })),
          backgroundColor: originalData.map((orig, index) => {
            const opt = optimizedData[index];
            const improvement = orig > 0 ? ((orig - opt) / orig) * 100 : 0;
            if (improvement >= 50) return "rgba(75, 192, 192, 0.8)"; // Green - Excellent
            if (improvement >= 25) return "rgba(54, 162, 235, 0.8)"; // Blue - Good
            if (improvement >= 10) return "rgba(255, 205, 86, 0.8)"; // Yellow - Moderate
            if (improvement >= 0) return "rgba(255, 159, 64, 0.8)"; // Orange - Low
            return "rgba(255, 99, 132, 0.8)"; // Red - No improvement
          }),
          borderColor: "rgba(255, 255, 255, 0.5)",
          borderWidth: 1,
          pointRadius: 6,
        },
        {
          label: "No Change Line",
          data: referenceLine.map((value, index) => ({
            x: index * maxValue,
            y: index * maxValue,
          })),
          type: "line",
          borderColor: "rgba(255, 255, 255, 0.3)",
          borderWidth: 2,
          pointRadius: 0,
          fill: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: "#ddd" } },
        title: {
          display: true,
          text: "Optimization Effectiveness: Original vs Optimized Congestion",
          color: "#fff",
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              if (context.dataset.label === "Optimization Results") {
                const original = context.parsed.x;
                const optimized = context.parsed.y;
                const improvement =
                  original > 0 ? ((original - optimized) / original) * 100 : 0;
                return `Original: ${original}, Optimized: ${optimized}, Improvement: ${improvement.toFixed(
                  1
                )}%`;
              }
              return context.dataset.label;
            },
          },
        },
      },
      scales: {
        x: {
          ticks: { color: "#aaa" },
          title: {
            display: true,
            text: "Original Congestion",
            color: "#ddd",
          },
        },
        y: {
          ticks: { color: "#aaa" },
          beginAtZero: true,
          title: {
            display: true,
            text: "Optimized Congestion",
            color: "#ddd",
          },
        },
      },
    },
  });
}

function createComparisonChart(ctx) {
  const labels = latestResults.map((_, i) => `Sensor ${i + 1}`);
  const originalData = latestResults.map(
    (d) => d.impact?.original_congestion || 0
  );
  const optimizedData = latestResults.map(
    (d) => d.impact?.optimized_congestion || 0
  );

  return new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Before Optimization",
          data: originalData,
          backgroundColor: "rgba(255, 99, 132, 0.8)",
          borderColor: "rgba(255, 99, 132, 1)",
          borderWidth: 1,
        },
        {
          label: "After Optimization",
          data: optimizedData,
          backgroundColor: "rgba(75, 192, 192, 0.8)",
          borderColor: "rgba(75, 192, 192, 1)",
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: "#ddd" } },
        title: {
          display: true,
          text: "Before vs After Optimization Comparison",
          color: "#fff",
        },
      },
      scales: {
        x: { ticks: { color: "#aaa" } },
        y: { ticks: { color: "#aaa" }, beginAtZero: true },
      },
    },
  });
}

function createImprovementChart(ctx) {
  const labels = latestResults.map((_, i) => `Sensor ${i + 1}`);
  const improvementData = latestResults.map((d) => {
    const original = d.impact?.original_congestion || 0;
    const optimized = d.impact?.optimized_congestion || 0;
    return original > 0 ? ((original - optimized) / original) * 100 : 0;
  });

  return new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Improvement %",
          data: improvementData,
          backgroundColor: improvementData.map((value) =>
            value > 0 ? "rgba(75, 192, 192, 0.8)" : "rgba(255, 99, 132, 0.8)"
          ),
          borderColor: improvementData.map((value) =>
            value > 0 ? "rgba(75, 192, 192, 1)" : "rgba(255, 99, 132, 1)"
          ),
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { labels: { color: "#ddd" } },
        title: {
          display: true,
          text: "Percentage Improvement per Sensor",
          color: "#fff",
        },
      },
      scales: {
        x: { ticks: { color: "#aaa" } },
        y: {
          ticks: {
            color: "#aaa",
            callback: function (value) {
              return value + "%";
            },
          },
          beginAtZero: true,
        },
      },
    },
  });
}
