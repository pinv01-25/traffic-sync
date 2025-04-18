import random
from modules.fuzzy.system import VEHICLE_RANGE, SPEED_RANGE, DENSITY_RANGE


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
