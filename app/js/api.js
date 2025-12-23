async function evaluateManual() {
  // Get all input values
  const trafficLightId =
    document.getElementById("inputTrafficLightId").value || "TL001";
  const controlledEdges = document
    .getElementById("inputControlledEdges")
    .value.split(",")
    .map((edge) => edge.trim()) || ["edge1", "edge2", "edge3"];

  const vehiclesPerMinute = parseInt(
    document.getElementById("inputVehiclesPerMinute").value
  );
  const avgSpeed = parseFloat(document.getElementById("inputAvgSpeed").value);
  const circulationTime = parseFloat(
    document.getElementById("inputCirculationTime").value
  );
  const density = parseFloat(document.getElementById("inputDensity").value);

  const motorcycle =
    parseInt(document.getElementById("inputMotorcycle").value) || 0;
  const car = parseInt(document.getElementById("inputCar").value) || 0;
  const bus = parseInt(document.getElementById("inputBus").value) || 0;
  const truck = parseInt(document.getElementById("inputTruck").value) || 0;

  // Validate required fields
  if (
    isNaN(vehiclesPerMinute) ||
    isNaN(avgSpeed) ||
    isNaN(circulationTime) ||
    isNaN(density)
  ) {
    alert("Please fill in all required fields with valid numbers.");
    return;
  }

  // Create the data structure expected by the API
  const trafficData = {
    version: "1.0",
    type: "data",
    timestamp: getCurrentTimestamp(),
    traffic_light_id: trafficLightId,
    controlled_edges: controlledEdges,
    metrics: {
      vehicles_per_minute: vehiclesPerMinute,
      avg_speed_kmh: avgSpeed,
      avg_circulation_time_sec: circulationTime,
      density: density,
    },
    vehicle_stats: {
      motorcycle: motorcycle,
      car: car,
      bus: bus,
      truck: truck,
    },
  };

  showLoading();

  try {
    const res = await fetch("/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(trafficData),
    });

    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }

    const json = await res.json();
    showResults([json]); // Wrap in array for consistency
  } catch (error) {
    hideLoading();
    alert(`Error: ${error.message}`);
    console.error("Error:", error);
  }
}

async function evaluateRandom() {
  const sensors = parseInt(document.getElementById("sensors").value);
  if (isNaN(sensors) || sensors <= 0) {
    alert("Enter a valid number of sensors.");
    return;
  }

  showLoading();

  try {
    const res = await fetch(`/evaluate/${sensors}`, { method: "POST" });

    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }

    const json = await res.json();
    // Backend returns an OptimizationBatch object with an `optimizations` array
    // Fall back to raw json if structure changes
    const resultsArray = Array.isArray(json) ? json : json.optimizations || [];
    showResults(resultsArray);
  } catch (error) {
    hideLoading();
    alert(`Error: ${error.message}`);
    console.error("Error:", error);
  }
}
