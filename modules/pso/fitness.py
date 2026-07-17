"""
Cycle-length estimation and PSO fitness evaluation for traffic optimization.

Under hierarchical control, traffic-sim splits green time locally per approach
by queue length; this service only decides the CYCLE LENGTH per cluster. The
fitness function is 1-D: it evaluates the fuzzy congestion the crossing would
serve at a given cycle length, penalizing long cycles (longer average wait)
so PSO does not degenerate to the upper bound.

Functions:
    - calculate_base_cycle: Compute the initial cycle-length seed for PSO.
    - fitness_function: Cycle-length congestion objective for a PSO particle.
"""

from modules.fuzzy.system import DENSITY_RANGE, SPEED_RANGE, VEHICLE_RANGE, simulator

# --------------------------------------------------
# Optimization Parameters
# --------------------------------------------------

#: Weight for density term in the base cycle formula.
ALPHA = 0.4

#: Weight for speed term in the base cycle formula.
BETA = 0.4

#: Weight for VPM (vehicles per minute) term in the base cycle formula.
GAMMA = 0.2

#: Minimum allowable cycle length (in seconds).
C_MIN = 60

#: Maximum allowable cycle length (in seconds).
C_MAX = 120

#: Reference cycle length: the observed metrics were measured under this
#: cycle, so the surrogate returns them unmodified at C = C_REF.
C_REF = 90

#: Total time lost to yellow/all-red clearance per cycle (in seconds).
YELLOW_TOTAL = 6

#: Weight of the average-wait penalty added to the fuzzy congestion.
WAIT_WEIGHT = 2.0


# --------------------------------------------------
# Fitness Evaluation
# --------------------------------------------------


def _cycle_congestion(cycle, vpm, speed, density, include_wait=True):
    """Congestión surrogate del cruce dado el largo de ciclo.

    cf = fracción de ciclo útil (crece con C: menos pérdida por amarillos).
    Normalizado a C_REF: en C=C_REF devuelve las métricas observadas.
    El término de espera penaliza ciclos largos (rojo medio más largo).
    """
    cf = (cycle - YELLOW_TOTAL) / cycle
    cf_ref = (C_REF - YELLOW_TOTAL) / C_REF
    density_adj = density * cf_ref / cf
    speed_adj = speed * cf / cf_ref

    simulator.input["vehicles"] = min(vpm, float(max(VEHICLE_RANGE)))
    simulator.input["speed"] = min(max(speed_adj, 0.0), float(max(SPEED_RANGE)))
    simulator.input["density"] = min(density_adj, float(max(DENSITY_RANGE)))
    simulator.compute()
    congestion = simulator.output["congestion"]

    if include_wait:
        congestion += WAIT_WEIGHT * (cycle - C_MIN) / (C_MAX - C_MIN)
    return congestion


def fitness_function(particle, cluster_data):
    """Objetivo 1-D del PSO: congestión total en función del largo de ciclo."""
    cycle = float(particle[0])
    return _cycle_congestion(
        cycle,
        cluster_data["VPM Mean"],
        cluster_data["Speed Mean"],
        cluster_data["Density Mean"],
    )


def calculate_base_cycle(cluster_data):
    """Semilla del PSO: ciclo inicial según la fórmula académica re-escalada."""
    D = cluster_data["Density Mean"]
    V = cluster_data["Speed Mean"]
    VPM = cluster_data["VPM Mean"]
    term1 = ALPHA * min(D / max(DENSITY_RANGE), 1.0)
    term2 = BETA * (1 - min(V / max(SPEED_RANGE), 1.0))
    term3 = GAMMA * min(VPM / max(VEHICLE_RANGE), 1.0)
    load = term1 + term2 + term3          # ∈ [0, 1]
    return min(max(C_REF + (load - 0.5) * 60.0, C_MIN), C_MAX)
