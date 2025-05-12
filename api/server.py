from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List

from modules.fuzzy.evaluation import run_test_cases
from modules.cluster.evaluation import hierarchical_clustering
from modules.pso.optimization import pso
from modules.utils import generate_random_test_cases, consolidate_results
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="Traffic Sensor Analysis API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="app"), name="static")


class TrafficMetrics(BaseModel):
    vehicles_per_minute: int
    avg_speed_kmh: float
    avg_circulation_time_sec: float
    density: float


class VehicleStats(BaseModel):
    motorcycle: int
    car: int
    bus: int
    truck: int


class TrafficData(BaseModel):
    version: str
    type: str = "data"
    timestamp: int
    traffic_light_id: str
    controlled_edges: List[str]
    metrics: TrafficMetrics
    vehicle_stats: VehicleStats


class TrafficOptimization(BaseModel):
    cluster: int
    predicted_category: str
    congestion: float
    green_time: float
    red_time: float
    optimized_congestion: float
    optimized_category: str
    improvement: str
    optimized_vehicles_per_minute: float
    optimized_avg_speed_kmh: float
    optimized_density: float


class OptimizedTrafficData(BaseModel):
    version: str
    type: str = "data"
    timestamp: int
    traffic_light_id: str
    controlled_edges: List[str]
    metrics: TrafficMetrics
    vehicle_stats: VehicleStats
    optimization: TrafficOptimization


def run_pipeline(traffic_data: List[dict]):
    fuzzy = run_test_cases(traffic_data)
    clusters, sensors = hierarchical_clustering(fuzzy)
    result = pso(clusters)
    final_df = consolidate_results(sensors, result)
    return final_df


@app.get("/")
def root():
    return FileResponse(os.path.join("app", "index.html"))


@app.post("/evaluate", response_model=OptimizedTrafficData)
async def evaluate_json(request: Request):
    try:
        body = await request.json()
        traffic_data = TrafficData(**body)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid input format or data: {str(e)}"
        )

    try:
        result = run_pipeline([traffic_data.dict()])
        return result[0]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal pipeline error: {str(e)}"
        )


@app.post("/evaluate/{sensors}", response_model=List[OptimizedTrafficData])
def evaluate_random(sensors: int):
    if sensors <= 0:
        raise HTTPException(
            status_code=400, detail="'sensors' must be a positive integer."
        )

    test_data = generate_random_test_cases(sensors)
    return run_pipeline(test_data)
