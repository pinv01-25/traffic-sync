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
import pandas as pd


# --------------------------------------------------
# Evaluation functions
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


def get_congestion_category(value):
    """
    Get the linguistic category for a given congestion value.

    Args:
        value (float): Congestion value.

    Returns:
        str: Linguistic category ('none', 'mild', or 'severe').
    """
    m_ninguna = fuzz.interp_membership(
        congestion.universe, congestion["none"].mf, value
    )
    m_leve = fuzz.interp_membership(congestion.universe, congestion["mild"].mf, value)
    m_severa = fuzz.interp_membership(
        congestion.universe, congestion["severe"].mf, value
    )

    return max(zip([m_ninguna, m_leve, m_severa], ["none", "mild", "severe"]))[1]


# --------------------------------------------------
# Test cases
# --------------------------------------------------


def run_test_cases(json_data):
    """
    Run fuzzy evaluation on traffic test cases loaded from JSON.

    This function takes a list of dictionaries representing traffic observations,
    evaluates fuzzy congestion, and prints the results in tabular format.

    Args:
        json_data (list[dict]): List of traffic input samples. Each item must contain:
            - 'vpm': Vehicles per minute
            - 'spd': Average speed (km/h)
            - 'den': Vehicle density (veh/km)
            - 'expected': Expected linguistic congestion category

    Returns:
        pd.DataFrame: DataFrame with fuzzy outputs and membership breakdown.
    """
    results = []

    for test in json_data:
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

    return df_results
