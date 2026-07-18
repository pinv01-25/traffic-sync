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

#: Umbrales de gridlock: densidad alta Y velocidad casi nula a la vez. Un
#: cruce "ocupado pero fluyendo" (densidad alta, velocidad moderada) no es
#: lo mismo que un atasco real (nadie se mueve) — la fórmula de carga
#: original mezcla ambos en un único término y empuja a ciclos LARGOS en
#: los dos casos por igual. Bajo un atasco de verdad, un ciclo largo
#: empeora las cosas: alimenta más vehículos por verde hacia un corredor
#: que ya no puede drenarlos (deadlock de corredor observado en
#: demanda_alta/demanda_saturada con Max-Pressure). Distinguir el caso y
#: recortar el ciclo ahí es lo que le da a esta capa un rol real de
#: anti-gridlock, no solo de ajuste de throughput en régimen fluido.
GRIDLOCK_DENSITY_THRESHOLD = 0.6   # fracción de DENSITY_RANGE
GRIDLOCK_SPEED_THRESHOLD = 0.05    # fracción de SPEED_RANGE


def is_gridlocked(vpm, speed, density):
    """True si el patrón es 'nadie se mueve', no solo 'mucha demanda'."""
    density_frac = min(density / max(DENSITY_RANGE), 1.0)
    speed_frac = min(speed / max(SPEED_RANGE), 1.0)
    return density_frac >= GRIDLOCK_DENSITY_THRESHOLD and speed_frac <= GRIDLOCK_SPEED_THRESHOLD


# --------------------------------------------------
# Fitness Evaluation
# --------------------------------------------------


def _load(vpm, speed, density):
    """Carga normalizada del cruce en [0,1] (fórmula académica de pesos)."""
    term1 = ALPHA * min(density / max(DENSITY_RANGE), 1.0)
    term2 = BETA * (1 - min(speed / max(SPEED_RANGE), 1.0))
    term3 = GAMMA * min(vpm / max(VEHICLE_RANGE), 1.0)
    return term1 + term2 + term3


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
        load = _load(vpm, speed, density)
        wait_cost = (1.0 - load) * (cycle - C_MIN) / (C_MAX - C_MIN)
        capacity_cost = load * (YELLOW_TOTAL / cycle) / (YELLOW_TOTAL / C_MIN)
        congestion += WAIT_WEIGHT * (wait_cost + capacity_cost)
    return congestion


def fitness_function(particle, cluster_data):
    """Objetivo 1-D del PSO: congestión total en función del largo de ciclo."""
    cycle = float(particle[0])
    vpm = cluster_data["VPM Mean"]
    speed = cluster_data["Speed Mean"]
    density = cluster_data["Density Mean"]
    congestion = _cycle_congestion(cycle, vpm, speed, density)
    if is_gridlocked(vpm, speed, density):
        # Bajo atasco real, un ciclo largo alimenta más vehículos por verde
        # hacia un corredor que no drena: penalizar el largo de ciclo en
        # vez de recompensarlo invierte el sesgo de _cycle_congestion.
        congestion += WAIT_WEIGHT * (cycle - C_MIN) / (C_MAX - C_MIN)
    return congestion


def calculate_base_cycle(cluster_data):
    """Semilla del PSO: ciclo inicial según la fórmula académica re-escalada."""
    D = cluster_data["Density Mean"]
    V = cluster_data["Speed Mean"]
    VPM = cluster_data["VPM Mean"]
    if is_gridlocked(VPM, V, D):
        return C_MIN
    load = _load(VPM, V, D)          # ∈ [0, 1]
    return min(max(C_REF + (load - 0.5) * 60.0, C_MIN), C_MAX)
