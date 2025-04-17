"""
Fuzzy logic congestion evaluation and test cases.

This module contains functions to evaluate the output of the Mamdani-type fuzzy system,
based on specific traffic parameters, and to validate it with predefined test cases.

Functions:
    - evaluate_congestion: Runs the fuzzy inference engine.
    - run_test_cases: Evaluates a set of test cases and prints the results in table format.
"""

from modules.fuzzy.system import simulator, congestion
import skfuzzy as fuzz
from tabulate import tabulate
import pandas as pd


# --------------------------------------------------
# Evaluation function
# --------------------------------------------------


def evaluate_congestion(vpm, spd, den):
    """
    Evaluate traffic congestion using fuzzy logic.

    This function sets the input values into the fuzzy simulator, performs inference,
    and returns the crisp result and its corresponding linguistic category.

    Args:
        vpm (int | float): Vehicles per minute.
        spd (int | float): Average speed in km/h.
        den (int | float): Vehicle density (vehicles per km).

    Returns:
        dict: Dictionary with the following keys:
            - value (float): Crisp output from the fuzzy system.
            - category (str): Dominant linguistic category ('none', 'mild', or 'severe').
            - membership (dict): Membership degrees for each category.
                - 'none' (float)
                - 'mild' (float)
                - 'severe' (float)
            - error (str, optional): Error message if the simulation fails.
    """
    simulator.input["vehicles"] = vpm
    simulator.input["speed"] = spd
    simulator.input["density"] = den

    try:
        simulator.compute()
        value = simulator.output["congestion"]

        m_ninguna = fuzz.interp_membership(
            congestion.universe, congestion["none"].mf, value
        )
        m_leve = fuzz.interp_membership(
            congestion.universe, congestion["mild"].mf, value
        )
        m_severa = fuzz.interp_membership(
            congestion.universe, congestion["severe"].mf, value
        )

        return {
            "value": round(value, 2),
            "category": max(
                zip([m_ninguna, m_leve, m_severa], ["none", "mild", "severe"])
            )[1],
            "membership": {
                "none": round(m_ninguna, 2),
                "mild": round(m_leve, 2),
                "severe": round(m_severa, 2),
            },
        }
    except Exception as e:
        return {"error": str(e)}


# --------------------------------------------------
# Test cases
# --------------------------------------------------


def run_test_cases():
    """
    Run predefined test cases to validate the fuzzy congestion system.

    Each test case includes input values (vehicles, speed, density) and an expected
    linguistic category. The results are printed in a formatted table.

    Returns:
        pd.DataFrame: DataFrame containing test inputs, predictions, and membership values.
    """
    test_inputs = [
        {"vpm": 15, "spd": 50, "den": 60, "expected": "none"},  # Normal traffic
        {"vpm": 30, "spd": 35, "den": 90, "expected": "mild"},  # Mild congestion
        {"vpm": 45, "spd": 20, "den": 130, "expected": "severe"},  # Severe congestion
        {"vpm": 25, "spd": 40, "den": 70, "expected": "mild"},  # Mild congestion
        {"vpm": 30, "spd": 50, "den": 60, "expected": "none"},  # Normal traffic
        {"vpm": 20, "spd": 30, "den": 140, "expected": "mild"},  # Mild congestion
        {"vpm": 35, "spd": 15, "den": 100, "expected": "severe"},  # Severe congestion
    ]

    results = []
    for test in test_inputs:
        result = evaluate_congestion(test["vpm"], test["spd"], test["den"])

        membresias_str = " | ".join(
            f"{k}: {v:.2f}" for k, v in result["membership"].items()
        )

        results.append(
            {
                "VPM": test["vpm"],
                "Speed (km/h)": test["spd"],
                "Density (veh/km)": test["den"],
                "Expected": test["expected"],
                "Predicted": result["category"],
                "value": round(result["value"], 2),
                "Memberships": membresias_str,
            }
        )

    df_results = pd.DataFrame(results)
    print("\nTest Case Results:\n")
    print(tabulate(df_results, headers="keys", tablefmt="fancy_grid", showindex=True))

    return df_results
