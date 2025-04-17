import random
from modules.fuzzy.system import vehicle_range, speed_range, density_range


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
            "vpm": int(random.choice(vehicle_range)),
            "spd": int(random.choice(speed_range)),
            "den": int(random.choice(density_range)),
            "expected": "random",
        }
        test_cases.append(case)

    return test_cases
