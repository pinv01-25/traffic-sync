"""
This module defines the fuzzy inference system used for traffic congestion classification.
It includes the input and output variables, their membership functions, and the fuzzy rules.
"""

import numpy as np
from skfuzzy import control as ctrl
import skfuzzy as fuzz

# --------------------------------------------------
# Ranges
# --------------------------------------------------

#: Universe of discourse for vehicle rate (vehicles per minute).
VEHICLE_RANGE = np.arange(0, 51, 1)

#: Universe of discourse for average speed (km/h).
SPEED_RANGE = np.arange(0, 61, 1)

#: Universe of discourse for vehicle density (vehicles/km).
DENSITY_RANGE = np.arange(0, 151, 1)

#: Universe of discourse for congestion level (0 to 10).
CONGESTION_RANGE = np.arange(0, 11, 1)

# --------------------------------------------------
# Fuzzy Variables
# --------------------------------------------------

#: Fuzzy variable representing number of vehicles per minute.
vehicles = ctrl.Antecedent(VEHICLE_RANGE, "vehicles")

#: Fuzzy variable representing average speed in km/h.
speed = ctrl.Antecedent(SPEED_RANGE, "speed")

#: Fuzzy variable representing vehicle density in vehicles/km.
density = ctrl.Antecedent(DENSITY_RANGE, "density")

#: Fuzzy output variable representing congestion level.
congestion = ctrl.Consequent(CONGESTION_RANGE, "congestion")

# --------------------------------------------------
# Membership Functions
# --------------------------------------------------

#: Membership functions for 'vehicles'
vehicles["low"] = fuzz.trapmf(vehicles.universe, [0, 0, 15, 25])
vehicles["mid"] = fuzz.gaussmf(vehicles.universe, 30, 5)
vehicles["high"] = fuzz.trapmf(vehicles.universe, [35, 40, 50, 50])

#: Membership functions for 'speed'
speed["low"] = fuzz.trapmf(speed.universe, [0, 0, 20, 30])
speed["mid"] = fuzz.gaussmf(speed.universe, 35, 5)
speed["high"] = fuzz.trapmf(speed.universe, [40, 50, 60, 60])

#: Membership functions for 'density'
density["low"] = fuzz.trapmf(density.universe, [0, 0, 50, 80])
density["mid"] = fuzz.gaussmf(density.universe, 100, 15)
density["high"] = fuzz.trapmf(density.universe, [120, 130, 150, 150])

#: Membership functions for 'congestion'
congestion["none"] = fuzz.trapmf(congestion.universe, [0, 0, 2, 4])
congestion["mild"] = fuzz.trimf(congestion.universe, [3, 5, 7])
congestion["severe"] = fuzz.trapmf(congestion.universe, [6, 8, 10, 10])

# --------------------------------------------------
# Fuzzy Rules
# --------------------------------------------------

"""List of fuzzy rules for traffic congestion inference."""
RULES = [
    # vehicles: low  |   speed: low   |   density: [low, mid, high]
    ctrl.Rule(vehicles["low"] & speed["low"] & density["low"], congestion["mild"]),
    ctrl.Rule(vehicles["low"] & speed["low"] & density["mid"], congestion["mild"]),
    ctrl.Rule(vehicles["low"] & speed["low"] & density["high"], congestion["severe"]),
    # vehicles: low  |   speed: mid   |   density: [low, mid, high]
    ctrl.Rule(vehicles["low"] & speed["mid"] & density["low"], congestion["none"]),
    ctrl.Rule(vehicles["low"] & speed["mid"] & density["mid"], congestion["mild"]),
    ctrl.Rule(vehicles["low"] & speed["mid"] & density["high"], congestion["mild"]),
    # vehicles: low  |   speed: high   |   density: [low, mid, high]
    ctrl.Rule(vehicles["low"] & speed["high"] & density["low"], congestion["none"]),
    ctrl.Rule(vehicles["low"] & speed["high"] & density["mid"], congestion["none"]),
    ctrl.Rule(vehicles["low"] & speed["high"] & density["high"], congestion["mild"]),
    # vehicles: mid  |   speed: low   |   density: [low, mid, high]
    ctrl.Rule(vehicles["mid"] & speed["low"] & density["low"], congestion["mild"]),
    ctrl.Rule(vehicles["mid"] & speed["low"] & density["mid"], congestion["severe"]),
    ctrl.Rule(vehicles["mid"] & speed["low"] & density["high"], congestion["severe"]),
    # vehicles: mid  |   speed: mid   |   density: [low, mid, high]
    ctrl.Rule(vehicles["mid"] & speed["mid"] & density["low"], congestion["mild"]),
    ctrl.Rule(vehicles["mid"] & speed["mid"] & density["mid"], congestion["mild"]),
    ctrl.Rule(vehicles["mid"] & speed["mid"] & density["high"], congestion["severe"]),
    # vehicles: mid  |   speed: high   |   density: [low, mid, high]
    ctrl.Rule(vehicles["mid"] & speed["high"] & density["low"], congestion["none"]),
    ctrl.Rule(vehicles["mid"] & speed["high"] & density["mid"], congestion["mild"]),
    ctrl.Rule(vehicles["mid"] & speed["high"] & density["high"], congestion["mild"]),
    # vehicles: high   |   speed: low   |   density: [low, mid, high]
    ctrl.Rule(vehicles["high"] & speed["low"] & density["low"], congestion["severe"]),
    ctrl.Rule(vehicles["high"] & speed["low"] & density["mid"], congestion["severe"]),
    ctrl.Rule(vehicles["high"] & speed["low"] & density["high"], congestion["severe"]),
    # vehicles: high   |   speed: mid   |   density: [low, mid, high]
    ctrl.Rule(vehicles["high"] & speed["mid"] & density["low"], congestion["mild"]),
    ctrl.Rule(vehicles["high"] & speed["mid"] & density["mid"], congestion["severe"]),
    ctrl.Rule(vehicles["high"] & speed["mid"] & density["high"], congestion["severe"]),
    # vehicles: high   |   speed: high   |   density: [low, mid, high]
    ctrl.Rule(vehicles["high"] & speed["high"] & density["low"], congestion["mild"]),
    ctrl.Rule(vehicles["high"] & speed["high"] & density["mid"], congestion["mild"]),
    ctrl.Rule(vehicles["high"] & speed["high"] & density["high"], congestion["severe"]),
]

# --------------------------------------------------
# Fuzzy System and Simulator
# --------------------------------------------------

#: The full fuzzy control system object.
congestion_system = ctrl.ControlSystem(RULES)

#: Fuzzy simulation engine used for evaluating new inputs.
simulator = ctrl.ControlSystemSimulation(congestion_system)
