# Traffic-Sync: Intelligent Traffic Management System

Traffic-Sync is an intelligent traffic management system that classifies congestion using fuzzy logic, groups sensors via hierarchical clustering, and optimizes traffic signal timing using Particle Swarm Optimization (PSO). It includes a RESTful API and a web frontend.

## Directory Structure

```
pinv01-25-traffic-sync/
├── README.md               # This file
├── LICENSE                 # MIT license
├── requirements.txt        # Python dependencies
├── run.sh                  # Shell script to launch the server
├── test_cases.json         # Predefined sample data
├── api/                    # FastAPI backend
│   └── server.py           # RESTful API logic
├── app/                    # Web frontend (HTML+JS)
│   └── index.html          # Dashboard interface
└── modules/                # Core logic
    ├── utils.py            # Test generation & results consolidation
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

Evaluates a single traffic observation.

Request Body:
```json
{
  "version": "1.0",
  "type": "data",
  "timestamp": "1682000000",
  "traffic_light_id": "TL-101",
  "controlled_edges": ["E1", "E2"],
  "metrics": {
    "vehicles_per_minute": 30,
    "avg_speed_kmh": 40.5,
    "avg_circulation_time_sec": 35.2,
    "density": 85.3
  },
  "vehicle_stats": {
    "motorcycle": 2,
    "car": 6,
    "bus": 1,
    "truck": 1
  }
}
```
Response:
```json
{
  "version": "1.0",
  "type": "optimization",
  "timestamp": "1682000000",
  "traffic_light_id": "TL-101",
  "optimization": {
    "green_time_sec": 42,
    "red_time_sec": 48
  },
  "impact": {
    "original_congestion": 6,
    "optimized_congestion": 3,
    "original_category": "severe",
    "optimized_category": "mild"
  }
}
```
### `POST /evaluate/{sensors}`

Generates and evaluates sensors random test cases.

Path Parameter:

`sensors (int)`: Number of sensors to simulate.

Response: List of optimization results.

---

## Architecture

`Fuzzy Logic (modules/fuzzy)`
- Mamdani inference
- Inputs: VPM, Speed, Density
- Output: Congestion (none, mild, severe)
- Rules: 27 predefined

`Clustering (modules/cluster)`
- Hierarchical clustering (Ward + Euclidean)
- Groups sensors by output congestion
- Outputs cluster stats

`Optimization (modules/pso)`
- Particle Swarm Optimization
- Minimizes congestion by tuning green time
- Per-cluster optimization

---

## License

MIT License © 2025 PINV01-25 BlockDAG

## Author

Kevin Galeano
