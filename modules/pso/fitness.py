"""
Green time estimation and PSO fitness evaluation for traffic optimization.

This module implements the academic formula for estimating initial green times,
as well as a fitness function used in Particle Swarm Optimization (PSO) to minimize
congestion levels predicted by a fuzzy inference system.

The fitness is two-sided: an intersection shares its cycle between the served
(congested) approach and the cross traffic, so the objective is the sum of the
fuzzy congestion of both sides. A one-sided objective has no trade-off and PSO
degenerates to the upper bound (always max green), which starves cross streets.

Functions:
    - calculate_green_time: Compute initial green time using academic weights.
    - fitness_function: Two-sided congestion objective for a PSO particle.
"""

from modules.fuzzy.system import DENSITY_RANGE, SPEED_RANGE, VEHICLE_RANGE, simulator

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

#: Maximum allowable green time: the cross approach keeps at least T_MIN.
T_MAX = CYCLE_TIME - T_MIN

#: Assumed demand of the cross approach relative to the served one. The
#: pipeline optimizes the approach where a bottleneck was DETECTED, so by
#: construction the cross street is at most as loaded as the served one.
CROSS_DEMAND_RATIO = 0.5


# --------------------------------------------------
# Green Time Calculation
# --------------------------------------------------
def calculate_green_time(cluster_data):
    """
    Compute initial green time using the academic formula.

    Applies a weighted sum of normalized traffic parameters (density, speed, VPM)
    scaled to the feasible green range [T_MIN, T_MAX]. The weighted sum lies in
    [0, ALPHA+BETA+GAMMA] = [0, 1]; without the scaling the formula could only
    ever add one second to T_MIN.

    Args:
        cluster_data (pd.Series): Row of cluster-level statistics with the following fields:
            - 'Density Mean': Mean vehicle density in veh/km.
            - 'Speed Mean': Mean traffic speed in km/h.
            - 'VPM Mean': Mean vehicles per minute.

    Returns:
        float: Estimated green time (in seconds), in [T_MIN, T_MAX].
    """
    D = cluster_data["Density Mean"]
    V = cluster_data["Speed Mean"]
    VPM = cluster_data["VPM Mean"]

    # Weighted components of the green time formula (each in [0, weight])
    term1 = ALPHA * min(D / max(DENSITY_RANGE), 1.0)
    term2 = BETA * (1 - min(V / max(SPEED_RANGE), 1.0))
    term3 = GAMMA * min(VPM / max(VEHICLE_RANGE), 1.0)

    return T_MIN + (T_MAX - T_MIN) * (term1 + term2 + term3)


# --------------------------------------------------
# Fitness Evaluation
# --------------------------------------------------


def _approach_congestion(green_time, vpm, speed, density):
    """
    Fuzzy congestion of one approach given its green time within the cycle.

    Surrogate normalized to the balanced split: the observed metrics were
    measured under (roughly) balanced timing, so at green = CYCLE/2 the
    model returns the observations. Less green accumulates density and
    reduces served flow proportionally; more green does the opposite.
    Inputs are clipped to the fuzzy universes.
    """
    half_cycle = CYCLE_TIME / 2.0
    red_time = CYCLE_TIME - green_time

    adjusted_vpm = vpm * (green_time / half_cycle)
    adjusted_speed = speed * (1 + 0.01 * (green_time - half_cycle))
    adjusted_density = density * (red_time / half_cycle)

    simulator.input["vehicles"] = min(adjusted_vpm, float(max(VEHICLE_RANGE)))
    simulator.input["speed"] = min(max(adjusted_speed, 0.0), float(max(SPEED_RANGE)))
    simulator.input["density"] = min(adjusted_density, float(max(DENSITY_RANGE)))
    simulator.compute()

    return simulator.output["congestion"]


def fitness_function(particle, cluster_data):
    """
    Evaluate total intersection congestion for a given green time split.

    Two-sided objective: the served (detected bottleneck) approach receives
    `green_time` and the cross approach receives the remainder of the cycle.
    Cross demand is modeled as CROSS_DEMAND_RATIO of the served one (the
    detection pipeline guarantees the served side is the most loaded).

    Args:
        particle (np.ndarray): PSO particle containing a green time value.
        cluster_data (pd.Series): Row of cluster-level statistics with the following fields:
            - 'Density Mean'
            - 'Speed Mean'
            - 'VPM Mean'

    Returns:
        float: Sum of fuzzy congestion of both approaches (the lower, the better).
    """
    green_time = float(particle[0])

    vpm = cluster_data["VPM Mean"]
    speed = cluster_data["Speed Mean"]
    density = cluster_data["Density Mean"]

    served = _approach_congestion(green_time, vpm, speed, density)
    cross = _approach_congestion(
        CYCLE_TIME - green_time,
        vpm * CROSS_DEMAND_RATIO,
        speed,  # velocidad libre similar; la congestión la aportan flujo y densidad
        density * CROSS_DEMAND_RATIO,
    )

    return served + cross
