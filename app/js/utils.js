let latestResults = [];
const loadingMessages = [
  "Applying fuzzy logic...",
  "Applying hierarchical clustering...",
  "Applying particle swarm optimization...",
];
let loadingInterval = null;
let messageIndex = 0;

function showLoading() {
  document.getElementById("loadingSection").style.display = "block";
  document.getElementById("resultsSection").style.display = "none";
  document.getElementById("chartsSection").style.display = "none";
  loadingInterval = setInterval(() => {
    messageIndex = (messageIndex + 1) % loadingMessages.length;
    document.getElementById("loadingMessage").innerText =
      loadingMessages[messageIndex];
  }, 2000);
}

function hideLoading() {
  clearInterval(loadingInterval);
  document.getElementById("loadingSection").style.display = "none";
}

function getCurrentTimestamp() {
  return new Date().toISOString();
}

function updateMetricsCards() {
  if (latestResults.length === 0) return;

  // Calculate metrics
  const originalCongestions = latestResults.map(
    (d) => d.impact?.original_congestion || 0
  );
  const optimizedCongestions = latestResults.map(
    (d) => d.impact?.optimized_congestion || 0
  );
  const greenTimes = latestResults.map(
    (d) => d.optimization?.green_time_sec || 0
  );

  const avgOriginal =
    originalCongestions.reduce((a, b) => a + b, 0) / originalCongestions.length;
  const avgOptimized =
    optimizedCongestions.reduce((a, b) => a + b, 0) /
    optimizedCongestions.length;
  const avgReduction =
    avgOriginal > 0 ? ((avgOriginal - avgOptimized) / avgOriginal) * 100 : 0;

  const improvements = originalCongestions.map((orig, i) => {
    const opt = optimizedCongestions[i];
    return orig > 0 ? ((orig - opt) / orig) * 100 : 0;
  });
  const bestImprovement = Math.max(...improvements);

  const avgGreenTime =
    greenTimes.reduce((a, b) => a + b, 0) / greenTimes.length;
  const optimizedSensors = improvements.filter((imp) => imp > 0).length;
  const totalSensors = latestResults.length;

  // Update cards
  document.getElementById("avgReduction").textContent =
    avgReduction.toFixed(1) + "%";
  document.getElementById("bestImprovement").textContent =
    bestImprovement.toFixed(1) + "%";
  document.getElementById("avgGreenTime").textContent =
    avgGreenTime.toFixed(0) + "s";
  document.getElementById(
    "optimizedSensors"
  ).textContent = `${optimizedSensors}/${totalSensors}`;
}

function formatOptimizationData(optimization) {
  if (!optimization) return "N/A";
  return `Green: ${optimization.green_time_sec}s, Red: ${optimization.red_time_sec}s`;
}

function formatImpactData(impact) {
  if (!impact) return "N/A";
  const improvement =
    impact.original_congestion > 0
      ? (
          ((impact.original_congestion - impact.optimized_congestion) /
            impact.original_congestion) *
          100
        ).toFixed(1)
      : "0.0";
  return `Original: ${impact.original_congestion} (${impact.original_category}), Optimized: ${impact.optimized_congestion} (${impact.optimized_category}), Improvement: ${improvement}%`;
}

function showResults(data) {
  hideLoading();
  latestResults = data;

  document.getElementById("resultsSection").style.display = "block";
  document.getElementById("chartsSection").style.display = "block";

  // Create formatted data for the table
  const formattedData = data.map((item) => ({
    ...item,
    optimization: formatOptimizationData(item.optimization),
    impact: formatImpactData(item.impact),
  }));

  const columns = Object.keys(formattedData[0]).map((key) => ({
    field: key,
    title: key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, " "),
    sortable: true,
    formatter: function (value, row, index) {
      if (key === "optimization" || key === "impact") {
        return `<div style="white-space: pre-wrap; max-width: 300px;">${value}</div>`;
      }
      return value;
    },
  }));

  $("#resultTable").bootstrapTable("destroy").bootstrapTable({
    columns,
    data: formattedData,
  });

  // Initialize with bar chart
  updateChart("bar");
  updateMetricsCards();
}
