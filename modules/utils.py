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
    print("\n" + centered_title)
    print(underline * len(centered_title))
