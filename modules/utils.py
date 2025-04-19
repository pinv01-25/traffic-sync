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


def print_section_title(title: str, width: int = 120, underline: str = "="):
    """
    Print a centered and stylized title above a table.

    Args:
        title (str): The title text to display.
        width (int): Total width to center the title (default is 120 characters).
        underline (str): Character used for underlining (default is '=').

    Returns:
        None
    """
    centered_title = title.center(width)
    print(underline * len(centered_title))
    print("\n" + centered_title + "\n")
    print(underline * len(centered_title))


def consolidate_results(
    sensors: pd.DataFrame,
    result: pd.DataFrame,
    output_path: str = "consolidated_results.csv",
) -> pd.DataFrame:
    """
    Merge optimization results into the sensor-level dataset by matching cluster IDs
    and save the result to a CSV file.

    Args:
        sensors (pd.DataFrame): Original traffic sensor data. Must include a 'cluster' column.
        result (pd.DataFrame): PSO optimization results, indexed by cluster ID.
        output_path (str): Path to save the resulting CSV file.

    Returns:
        pd.DataFrame: Consolidated DataFrame with sensor data and corresponding optimization metrics.
    """
    # Ensure result has 'cluster' as index name
    result_with_index = result.copy()
    result_with_index.index.name = "cluster"

    # Merge by 'cluster'
    merged = sensors.merge(result_with_index, how="left", on="cluster")

    # Save to CSV
    merged.to_csv(output_path, index=False)
    print(f"✅ Consolidated results saved to: {output_path}")
