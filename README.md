# Traffic-Sync: Traffic Optimization Service

Traffic-Sync is a focused traffic optimization service that uses fuzzy logic, clustering, and Particle Swarm Optimization (PSO) to optimize traffic signal timing. It provides a simple RESTful API for traffic optimization.

## Directory Structure

```
traffic-sync/
├── README.md               # This file
├── LICENSE                 # MIT license
├── requirements.txt        # Python dependencies
├── run.sh                  # Shell script to launch the server
├── api/                    # FastAPI backend
│   └── server.py           # RESTful API logic
├── app/                    # Web frontend (HTML+JS)
│   └── index.html          # Dashboard interface
└── modules/                # Core logic
    ├── utils.py            # Results consolidation
    ├── cluster/            # Clustering logic
    ├── fuzzy/              # Fuzzy inference system
    └── pso/                # PSO optimization logic
```

## Getting Started

Install Dependencies
```python
pip install -r requirements.txt
```
Run the API Server
```bash
./run.sh
```
Visit: http://localhost:8002

---

## REST API

### `POST /evaluate`

Evaluates traffic data and returns optimization results. Handles batches of 1-10 sensors.

**Request Body (Batch Format):**
```json
{
  "version": "2.0",
  "type": "data",
  "timestamp": "2025-07-14T00:33:55Z",
  "traffic_light_id": "03",
  "sensors": [
    {
      "traffic_light_id": "03",
      "controlled_edges": ["edge05", "edge01", "edge14"],
      "metrics": {
        "vehicles_per_minute": 34,
        "avg_speed_kmh": 34.6,
        "avg_circulation_time_sec": 20,
        "density": 0.49
      },
      "vehicle_stats": {
        "motorcycle": 25,
        "car": 44,
        "bus": 4,
        "truck": 10
      }
    },
    {
      "traffic_light_id": "07",
      "controlled_edges": ["edge12", "edge08", "edge03"],
  "metrics": {
        "vehicles_per_minute": 28,
        "avg_speed_kmh": 42.1,
        "avg_circulation_time_sec": 18,
        "density": 0.31
  },
  "vehicle_stats": {
        "motorcycle": 18,
        "car": 52,
        "bus": 2,
        "truck": 8
  }
    }
  ]
}
```

**Response (Batch Format):**
```json
{
  "version": "2.0",
  "type": "optimization",
  "timestamp": "2025-07-14T00:33:55Z",
  "traffic_light_id": "03",
  "optimizations": [
    {
      "version": "2.0",
      "type": "optimization",
      "timestamp": "2025-07-14T00:33:55Z",
      "traffic_light_id": "03",
      "cluster_sensors": ["03", "07"],
  "optimization": {
        "green_time_sec": 14,
        "red_time_sec": 75
  },
  "impact": {
        "original_congestion": 4,
        "optimized_congestion": 1,
        "original_category": "mild",
        "optimized_category": "none"
  }
    }
  ]
}
```

### `GET /health`

Health check endpoint.

---

## Architecture

### Fuzzy Logic (modules/fuzzy)
- Mamdani inference system
- Inputs: VPM, Speed, Density
- Output: Congestion (none, mild, severe)
- 27 predefined rules

### Clustering (modules/cluster)
- Hierarchical clustering (Ward + Euclidean)
- Groups sensors by congestion output
- Handles single sensor cases

### Optimization (modules/pso)
- Particle Swarm Optimization
- 20 particles, 50 iterations
- Minimizes congestion by tuning green time
- Per-cluster optimization

---

## Batch Processing

The service processes batches of 1-10 sensors through the following pipeline:

1. **Fuzzy Evaluation**: Each sensor is evaluated for congestion using fuzzy logic
2. **Clustering**: Sensors are grouped by similar congestion patterns
3. **PSO Optimization**: Each cluster is optimized independently
4. **Response**: Returns one optimization per cluster formed

**Key Features:**
- **Gas Efficient**: Single JSON input/output reduces smart contract interactions
- **Clustering**: Automatically groups similar sensors for coordinated optimization
- **Scalable**: Handles 1-10 sensors in a single request
- **Cluster Information**: Response includes which sensors belong to each cluster

---

## Service Focus

This service is designed to be **optimization-focused** and **validation-light**:

- **No input validation**: Assumes data is pre-validated by the control service
- **Simple PSO**: Basic implementation without complex features
- **Minimal logging**: Essential logs only
- **Fast processing**: Optimized for speed over complexity
- **Single responsibility**: Only handles optimization

## Integration

The sync service is designed to work with the **traffic-control** service, which handles:
- Input validation
- Data storage
- Error handling
- Response validation
- Service coordination

---

## License

MIT License © 2025 PINV01-25 BlockDAG

## Author

Kevin Galeano
