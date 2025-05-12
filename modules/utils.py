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
            "timestamp": int(datetime.now(timezone.utc).timestamp()),
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
) -> list:
    """
    Merge optimization results into the sensor-level dataset by matching cluster IDs,
    and convert each row into a structured Optimization dictionary.

    Args:
        sensors (pd.DataFrame): Sensor data with traffic metrics and vehicle stats.
        result (pd.DataFrame): Optimization results with cluster IDs and metrics.
    Returns:
        list: List of structured optimization dictionaries.
    """
    result_with_index = result.copy()
    result_with_index.index.name = "cluster"

    # Merge by cluster
    merged = sensors.merge(result_with_index, how="left", on="cluster")

    response = []

    for _, row in merged.iterrows():
        optimization = {
            "version": row.get("version", "1.0"),
            "type": "optimization",
            "timestamp": row.get("timestamp", 0),
            "traffic_light_id": row["traffic_light_id"],
            "controlled_edges": row.get("controlled_edges", []),
            "metrics": {
                "vehicles_per_minute": int(row["VPM"]),
                "avg_speed_kmh": float(row["Speed (km/h)"]),
                "avg_circulation_time_sec": float(
                    row.get("avg_circulation_time_sec", 30.0)
                ),
                "density": float(row["Density (veh/km)"]),
            },
            "vehicle_stats": {
                "motorcycle": int(row.get("motorcycle", 0)),
                "car": int(row.get("car", 0)),
                "bus": int(row.get("bus", 0)),
                "truck": int(row.get("truck", 0)),
            },
            "optimization": {
                "cluster": int(row["cluster"]),
                "predicted_category": row["Predicted"],
                "congestion": float(row["value"]),
                "green_time": float(row["Green"]),
                "red_time": float(row["Red"]),
                "optimized_congestion": float(row["Optimized Congestion"]),
                "optimized_category": row["Optimized Category"],
                "improvement": row["Improvement"],
                "optimized_vehicles_per_minute": float(row["Optimized VPM"]),
                "optimized_avg_speed_kmh": float(row["Optimized Speed"]),
                "optimized_density": float(row["Optimized Density"]),
            },
        }

        response.append(optimization)

    return response
