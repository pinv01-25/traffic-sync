import sys
sys.path.insert(0, '.')
import numpy as np
import pandas as pd
from modules.pso.optimization import pso


def _df(vpm, speed, density):
    return pd.DataFrame([{
        "Cluster": "c", "VPM Mean": vpm, "Speed Mean": speed,
        "Density Mean": density, "Congestion Mean": 5.0,
    }])


def test_cycle_optimum_monotone():
    """Demanda pesada pero fluyendo (no atascada) pide ciclo más largo que
    demanda liviana — el caso 'nadie se mueve' es distinto, ver
    test_gridlock_shortens_cycle."""
    np.random.seed(0)
    heavy = pso(_df(vpm=40, speed=8.0, density=150.0)).iloc[0]
    light = pso(_df(vpm=2, speed=45.0, density=8.0)).iloc[0]
    assert heavy["Cycle"] > light["Cycle"]
    assert 60 <= light["Cycle"] <= 120
    assert 60 <= heavy["Cycle"] <= 120


def test_gridlock_shortens_cycle():
    """Densidad alta Y velocidad casi nula = atasco real, no solo demanda
    alta: un ciclo largo alimenta más vehículos hacia un corredor que no
    drena, así que el PSO debe converger al ciclo mínimo, no al máximo."""
    np.random.seed(0)
    gridlocked = pso(_df(vpm=40, speed=1.0, density=150.0)).iloc[0]
    heavy_flowing = pso(_df(vpm=40, speed=8.0, density=150.0)).iloc[0]
    assert gridlocked["Cycle"] == 60
    assert gridlocked["Cycle"] < heavy_flowing["Cycle"]


def test_green_red_sum_is_useful_budget():
    np.random.seed(0)
    r = pso(_df(vpm=12, speed=14.0, density=90.0)).iloc[0]
    assert abs((r["Green"] + r["Red"]) - (r["Cycle"] - 6)) < 1e-6
