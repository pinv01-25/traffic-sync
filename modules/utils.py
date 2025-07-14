import random
from modules.fuzzy.system import VEHICLE_RANGE, SPEED_RANGE, DENSITY_RANGE
import pandas as pd
from datetime import datetime, timezone


def generate_random_test_cases(n_cases: int) -> list:
    """
    Generate random structured traffic sensor test cases as a list of TrafficData-style dicts.

    Args:
        n_cases (int): Number of test cases to generate.

    Returns:
        list: List of structured traffic data dictionaries.
    """
    test_cases = []

    for i in range(n_cases):
        case = {
            "version": "1.0",
            "type": "data",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "traffic_light_id": f"TL-{1000 + i}",
            "controlled_edges": [f"E{i}-{j}" for j in range(1, 4)],
            "metrics": {
                "vehicles_per_minute": int(random.choice(VEHICLE_RANGE)),
                "avg_speed_kmh": float(random.choice(SPEED_RANGE)),
                "avg_circulation_time_sec": round(random.uniform(20.0, 60.0), 1),
                "density": float(random.choice(DENSITY_RANGE))
                / 10.0,  # simulate decimal densities
            },
            "vehicle_stats": {
                "motorcycle": random.randint(0, 5),
                "car": random.randint(0, 10),
                "bus": random.randint(0, 2),
                "truck": random.randint(0, 3),
            },
        }
        test_cases.append(case)

    return test_cases


def consolidate_results(
    sensors: pd.DataFrame,
    result: pd.DataFrame,
    timestamp: str = None,
) -> list:
    """
    Merge optimization results into the sensor-level dataset by matching cluster IDs,
    and convert each row into a structured Optimization dictionary.

    Args:
        sensors (pd.DataFrame): Sensor data with traffic metrics and vehicle stats.
        result (pd.DataFrame): Optimization results with cluster IDs and metrics.
        timestamp (str): Optional timestamp to use for all results.
    Returns:
        list: List of structured optimization dictionaries.
    """
    result_with_index = result.copy()
    result_with_index.index.name = "cluster"

    # Merge by cluster
    merged = sensors.merge(result_with_index, how="left", on="cluster")

    response = []

    for _, row in merged.iterrows():
        # Use provided timestamp or existing timestamp (already in ISO format from control service)
        result_timestamp = timestamp if timestamp else row["timestamp"]
        
        optimization_dict = {
            "version": row["version"],
            "type": "optimization",
            "timestamp": result_timestamp,
            "traffic_light_id": row["traffic_light_id"],
            "optimization": {
                "green_time_sec": int(row["Green"]),
                "red_time_sec": int(row["Red"]),
            },
            "impact": {
                "original_congestion": int(row["value"]),
                "optimized_congestion": int(row["Optimized Congestion"]),
                "original_category": row["Predicted"],
                "optimized_category": row["Optimized Category"],
            },
        }
        response.append(optimization_dict)

    return response
