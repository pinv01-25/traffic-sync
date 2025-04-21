import random
from modules.fuzzy.system import VEHICLE_RANGE, SPEED_RANGE, DENSITY_RANGE
import pandas as pd


def generate_random_test_cases(n_cases: int) -> list:
    """
    Generate random traffic sensor test cases as a list of dicts.

    Args:
        n_cases (int): Number of test cases to generate.

    Returns:
        list: List of test case dictionaries.
    """

    test_cases = []

    for _ in range(n_cases):
        case = {
            "vpm": int(random.choice(VEHICLE_RANGE)),
            "spd": int(random.choice(SPEED_RANGE)),
            "den": int(random.choice(DENSITY_RANGE)),
            "expected": "random",
        }
        test_cases.append(case)

    return test_cases


def consolidate_results(
    sensors: pd.DataFrame,
    result: pd.DataFrame,
) -> pd.DataFrame:
    """
    Merge optimization results into the sensor-level dataset by matching cluster IDs
    and save the result to a CSV file.

    Args:
        sensors (pd.DataFrame): Original traffic sensor data. Must include a 'cluster' column.
        result (pd.DataFrame): PSO optimization results, indexed by cluster ID.
    Returns:
        pd.DataFrame: Consolidated DataFrame with sensor data and corresponding optimization metrics.
    """
    # Ensure result has 'cluster' as index name
    result_with_index = result.copy()
    result_with_index.index.name = "cluster"

    # Merge by 'cluster'
    merged = sensors.merge(result_with_index, how="left", on="cluster")

    return merged
