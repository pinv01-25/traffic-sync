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
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger("traffic_sync")

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
    timestamp: str
    traffic_light_id: str
    controlled_edges: List[str]
    metrics: TrafficMetrics
    vehicle_stats: VehicleStats


class OptimizationDetails(BaseModel):
    green_time_sec: int
    red_time_sec: int

class ImpactDetails(BaseModel):
    original_congestion: int
    optimized_congestion: int
    original_category: str
    optimized_category: str

class OptimizationData(BaseModel):
    version: str
    type: str = "optimization"
    timestamp: str
    traffic_light_id: str
    optimization: OptimizationDetails
    impact: ImpactDetails


def run_pipeline(traffic_data: List[dict]):
    logger.info("Running traffic pipeline...")
    fuzzy = run_test_cases(traffic_data)
    clusters, sensors = hierarchical_clustering(fuzzy)
    result = pso(clusters)
    final_df = consolidate_results(sensors, result)
    logger.info("Pipeline completed successfully.")
    return final_df


@app.get("/")
def root():
    return FileResponse(os.path.join("app", "index.html"))


@app.post("/evaluate", response_model=OptimizationData)
async def evaluate_json(request: Request):
    try:
        body = await request.json()
        logger.info("Received /evaluate request:\n%s", json.dumps(body, indent=2))
        traffic_data = TrafficData(**body)
        logger.info("Payload validated successfully.")
    except Exception as e:
        logger.exception("Validation error")
        raise HTTPException(
            status_code=400, detail=f"Invalid input format or data: {str(e)}"
        )

    try:
        logger.info("Starting optimization pipeline for traffic_light_id=%s", traffic_data.traffic_light_id)
        result = run_pipeline([traffic_data.dict()])
        logger.info("Optimization result: %s", json.dumps(result[0], indent=2))
        return result[0]
    except Exception as e:
        logger.error("Pipeline error: %s", str(e))
        raise HTTPException(
            status_code=500, detail=f"Internal pipeline error: {str(e)}"
        )


@app.post("/evaluate/{sensors}", response_model=List[OptimizationData])
def evaluate_random(sensors: int):
    if sensors <= 0:
        raise HTTPException(
            status_code=400, detail="'sensors' must be a positive integer."
        )

    test_data = generate_random_test_cases(sensors)
    return run_pipeline(test_data)
