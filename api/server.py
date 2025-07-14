from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Union

from modules.fuzzy.evaluation import run_test_cases
from modules.cluster.evaluation import hierarchical_clustering
from modules.pso.optimization import pso
from modules.utils import consolidate_results
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("traffic_sync")

app = FastAPI(title="Traffic Optimization API")
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


class SensorData(BaseModel):
    traffic_light_id: str
    controlled_edges: List[str]
    metrics: TrafficMetrics
    vehicle_stats: VehicleStats


# Updated models for batch processing (1-10 sensors)
class DataBatch(BaseModel):
    version: str
    type: str = "data"
    timestamp: str
    traffic_light_id: str
    sensors: List[SensorData]


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
    cluster_sensors: List[str]  # List of sensor IDs in this cluster
    optimization: OptimizationDetails
    impact: ImpactDetails


class OptimizationBatch(BaseModel):
    version: str
    type: str = "optimization"
    timestamp: str
    traffic_light_id: str
    optimizations: List[OptimizationData]


def run_pipeline(traffic_data: List[dict]):
    """
    Run optimization pipeline for batch of sensors (1-10).
    
    This function processes multiple sensors through fuzzy evaluation,
    clustering, and PSO optimization. Returns one optimization per cluster formed.
    """
    # Run fuzzy evaluation on all sensors
    fuzzy = run_test_cases(traffic_data)
    
    # Apply clustering to group sensors by congestion similarity
    clusters, sensors = hierarchical_clustering(fuzzy)
    
    # TEMPORARY DEBUG LOGGING - CLUSTER DATA STRUCTURE
    logger.info("=== CLUSTER DATA DEBUG ===")
    logger.info(f"Clusters DataFrame shape: {clusters.shape}")
    logger.info(f"Clusters DataFrame columns: {list(clusters.columns)}")
    logger.info(f"Clusters DataFrame index: {list(clusters.index)}")
    logger.info(f"First cluster data: {clusters.iloc[0].to_dict() if len(clusters) > 0 else 'No clusters'}")
    logger.info(f"Sensors DataFrame shape: {sensors.shape}")
    logger.info(f"Sensors DataFrame columns: {list(sensors.columns)}")
    logger.info(f"First sensor data: {sensors.iloc[0].to_dict() if len(sensors) > 0 else 'No sensors'}")
    logger.info("=== END CLUSTER DATA DEBUG ===")
    
    # Run PSO optimization on each cluster
    result = pso(clusters)
    
    # TEMPORARY DEBUG LOGGING - PSO RESULT STRUCTURE
    logger.info("=== PSO RESULT DEBUG ===")
    logger.info(f"PSO result DataFrame shape: {result.shape}")
    logger.info(f"PSO result DataFrame columns: {list(result.columns)}")
    logger.info(f"PSO result DataFrame index: {list(result.index)}")
    logger.info(f"First PSO result: {result.iloc[0].to_dict() if len(result) > 0 else 'No results'}")
    logger.info("=== END PSO RESULT DEBUG ===")
    
    # Get original timestamp for response
    original_timestamp = traffic_data[0]["timestamp"] if traffic_data else None
    
    # Consolidate results and format for batch response
    final_results = consolidate_results(sensors, result, original_timestamp)
    
    # Convert to batch format with cluster information
    optimizations = []
    for cluster_id, cluster_data in result.iterrows():
        # Find sensors that belong to this cluster
        cluster_sensors = sensors[sensors['cluster'] == cluster_id]['traffic_light_id'].tolist()
        
        # Get original congestion from cluster data using cluster number instead of index
        cluster_row = clusters[clusters['Cluster'] == cluster_id]
        original_congestion = cluster_row['Congestion Mean'].iloc[0]
        original_category = cluster_row['Predicted Mode'].iloc[0]
        
        optimization = {
            "version": traffic_data[0]["version"],
            "type": "optimization",
            "timestamp": original_timestamp,
            "traffic_light_id": cluster_sensors[0],  # Use first sensor as reference
            "cluster_sensors": cluster_sensors,
            "optimization": {
                "green_time_sec": int(cluster_data["Green"]),
                "red_time_sec": int(cluster_data["Red"])
            },
            "impact": {
                "original_congestion": int(original_congestion),
                "optimized_congestion": int(cluster_data["Optimized Congestion"]),
                "original_category": original_category,
                "optimized_category": cluster_data["Optimized Category"]
            }
        }
        optimizations.append(optimization)
    
    return optimizations


@app.get("/")
def root():
    return FileResponse("app/index.html")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "traffic-sync"}


@app.post("/evaluate", response_model=OptimizationBatch)
async def evaluate_json(request: Request):
    """
    Evaluate traffic data - handles batches of 1-10 sensors.
    
    The clustering module groups sensors by congestion similarity,
    and PSO optimizes each cluster. Returns one optimization per cluster formed.
    """
    try:
        body = await request.json()
        
        # TEMPORARY DEBUG LOGGING
        logger.info("=== SYNC SERVICE DEBUG ===")
        logger.info(f"Received request body: {body}")
        logger.info(f"Request body type: {type(body)}")
        logger.info(f"Request body keys: {list(body.keys()) if isinstance(body, dict) else 'Not a dict'}")
        if isinstance(body, dict) and 'sensors' in body:
            logger.info(f"Number of sensors: {len(body['sensors'])}")
            logger.info(f"First sensor keys: {list(body['sensors'][0].keys()) if body['sensors'] else 'No sensors'}")
        logger.info("=== END DEBUG ===")
        
        # Validate batch format
        batch_data = DataBatch(**body)
        
        # Convert batch data to list of dictionaries for processing
        sensors_data = []
        for sensor in batch_data.sensors:
            sensor_dict = {
                "version": batch_data.version,
                "type": "data",
                "timestamp": batch_data.timestamp,
                "traffic_light_id": sensor.traffic_light_id,
                "controlled_edges": sensor.controlled_edges,
                "metrics": sensor.metrics.dict(),
                "vehicle_stats": sensor.vehicle_stats.dict()
            }
            sensors_data.append(sensor_dict)
        
        # Run batch optimization pipeline
        optimizations = run_pipeline(sensors_data)
        
        # Return batch format
        return OptimizationBatch(
            version=batch_data.version,
            type="optimization",
            timestamp=batch_data.timestamp,
            traffic_light_id=batch_data.traffic_light_id,
            optimizations=optimizations
        )
            
    except Exception as e:
        # TEMPORARY DEBUG LOGGING
        logger.error("=== SYNC SERVICE ERROR DEBUG ===")
        logger.error(f"Exception type: {type(e)}")
        logger.error(f"Exception message: {str(e)}")
        logger.error(f"Exception details: {e}")
        if hasattr(e, 'errors'):
            logger.error(f"Validation errors: {e.errors()}")
        logger.error("=== END ERROR DEBUG ===")
        
        raise HTTPException(
            status_code=400, detail=f"Invalid input format or data: {str(e)}"
        )
