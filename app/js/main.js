// Add event listeners for chart type selection
document.addEventListener("DOMContentLoaded", function () {
  const chartRadios = document.querySelectorAll('input[name="chartType"]');
  chartRadios.forEach((radio) => {
    radio.addEventListener("change", function () {
      if (latestResults.length > 0) {
        updateChart(this.value);
      }
    });
  });
});
