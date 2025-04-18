"""
Green time estimation and PSO fitness evaluation for traffic optimization.

This module implements the academic formula for estimating initial green times,
as well as a fitness function used in Particle Swarm Optimization (PSO) to minimize
congestion levels predicted by a fuzzy inference system.

Functions:
    - calculate_green_time: Compute initial green time using academic weights.
    - fitness_function: Compute congestion level based on PSO particle and fuzzy logic.
"""

from modules.fuzzy.system import simulator, VEHICLE_RANGE, DENSITY_RANGE, SPEED_RANGE

# --------------------------------------------------
# Optimization Parameters
# --------------------------------------------------

#: Weight for density term in green time formula.
ALPHA = 0.4

#: Weight for speed term in green time formula.
BETA = 0.4

#: Weight for VPM (vehicles per minute) term in green time formula.
GAMMA = 0.2

#: Minimum allowable green time (in seconds).
T_MIN = 10

#: Default cycle time for traffic signals (in seconds).
CYCLE_TIME = 90


# --------------------------------------------------
# Green Time Calculation
# --------------------------------------------------
def calculate_green_time(cluster_data):
    """
    Compute initial green time using the academic formula.

    Applies a weighted sum of normalized traffic parameters (density, speed, VPM)
    to determine a recommended green time for a traffic signal, based on research heuristics.

    Args:
        cluster_data (pd.Series): Row of cluster-level statistics with the following fields:
            - 'Density Mean': Mean vehicle density in veh/km.
            - 'Speed Mean': Mean traffic speed in km/h.
            - 'VPM Mean': Mean vehicles per minute.

    Returns:
        float: Estimated green time (in seconds).
    """
    D = cluster_data["Density Mean"]
    V = cluster_data["Speed Mean"]
    VPM = cluster_data["VPM Mean"]

    # Weighted components of the green time formula
    term1 = ALPHA * (D / max(DENSITY_RANGE))
    term2 = BETA * (1 - V / max(SPEED_RANGE))
    term3 = GAMMA * (VPM / max(VEHICLE_RANGE))

    return T_MIN + term1 + term2 + term3


# --------------------------------------------------
# Fitness Evaluation
# --------------------------------------------------


def fitness_function(particle, cluster_data):
    """
    Evaluate congestion level for a given green time using fuzzy logic.

    Simulates how a green time (from a PSO particle) affects traffic behavior.
    The resulting fuzzy congestion value is used as a fitness score (to minimize).

    Args:
        particle (np.ndarray): PSO particle containing a green time value.
        cluster_data (pd.Series): Row of cluster-level statistics with the following fields:
            - 'Density Mean'
            - 'Speed Mean'
            - 'VPM Mean'

    Returns:
        float: Fuzzy congestion level (the lower, the better).
    """
    green_time = particle[0]
    red_time = CYCLE_TIME - green_time

    # Adjust traffic parameters based on green/red time allocation
    adjusted_vpm = cluster_data["VPM Mean"] * (green_time / CYCLE_TIME)
    adjusted_speed = cluster_data["Speed Mean"] * (1 + 0.01 * (green_time - T_MIN))
    adjusted_density = cluster_data["Density Mean"] * (red_time / CYCLE_TIME)

    # Simulate using fuzzy inference system
    simulator.input["vehicles"] = adjusted_vpm
    simulator.input["speed"] = adjusted_speed
    simulator.input["density"] = adjusted_density
    simulator.compute()

    return simulator.output["congestion"]
