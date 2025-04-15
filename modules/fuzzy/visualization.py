"""
Visualization tools for the fuzzy traffic congestion system.

This module provides plotting utilities to display:
- Membership functions for all fuzzy variables.
- A 3D surface of the fuzzy output.

Functions:
    - plot_memberships
    - plot_interactive_3d_surface
"""

import numpy as np
import skfuzzy as fuzz
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import joblib
import os
from modules.fuzzy.system import (
    density_range,
    vehicle_range,
    speed_range,
    simulator,
)

# --------------------------------------------------
# Plot membership functions
# --------------------------------------------------


def plot_memberships(cache_path="cache/membership_plot.pkl"):
    """
    Plot membership functions for fuzzy system inputs and output.

    This function generates a 4-row Plotly chart showing the membership
    functions of the fuzzy system inputs (vehicles, speed, density) and
    the output (congestion). Results are cached for performance.

    Args:
        cache_path (str): Path to the cached figure.

    Returns:
        None
    """
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)

    if os.path.exists(cache_path):
        fig = joblib.load(cache_path)
        print("Membership plot loaded from cache.")
        fig.show()
        return

    fig = make_subplots(
        rows=4,
        cols=1,
        shared_xaxes=False,
        subplot_titles=[
            "Membership Function: Vehicles per Minute",
            "Membership Function: Average Speed",
            "Membership Function: Estimated Density",
            "Membership Function: Congestion Level",
        ],
    )

    # Vehicles per minute
    fig.add_trace(
        go.Scatter(
            x=vehicle_range,
            y=fuzz.trapmf(vehicle_range, [0, 0, 15, 25]),
            name="Low",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=vehicle_range, y=fuzz.gaussmf(vehicle_range, 30, 5), name="Mid"),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=vehicle_range,
            y=fuzz.trapmf(vehicle_range, [35, 40, 50, 50]),
            name="High",
        ),
        row=1,
        col=1,
    )

    # Speed
    fig.add_trace(
        go.Scatter(
            x=speed_range,
            y=fuzz.trapmf(speed_range, [0, 0, 20, 30]),
            name="Low",
            showlegend=False,
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=speed_range,
            y=fuzz.gaussmf(speed_range, 35, 5),
            name="Mid",
            showlegend=False,
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=speed_range,
            y=fuzz.trapmf(speed_range, [40, 50, 60, 60]),
            name="High",
            showlegend=False,
        ),
        row=2,
        col=1,
    )

    # Density
    fig.add_trace(
        go.Scatter(
            x=density_range,
            y=fuzz.trapmf(density_range, [0, 0, 50, 80]),
            name="Low",
            showlegend=False,
        ),
        row=3,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=density_range,
            y=fuzz.gaussmf(density_range, 100, 15),
            name="Mid",
            showlegend=False,
        ),
        row=3,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=density_range,
            y=fuzz.trapmf(density_range, [120, 130, 150, 150]),
            name="High",
            showlegend=False,
        ),
        row=3,
        col=1,
    )

    # Congestion
    rango_congestion_plot = np.linspace(0, 10, 1000)
    fig.add_trace(
        go.Scatter(
            x=rango_congestion_plot,
            y=fuzz.trapmf(rango_congestion_plot, [0, 0, 2, 4]),
            name="None",
            showlegend=False,
        ),
        row=4,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=rango_congestion_plot,
            y=fuzz.trimf(rango_congestion_plot, [3, 5, 7]),
            name="Mild",
            showlegend=False,
        ),
        row=4,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=rango_congestion_plot,
            y=fuzz.trapmf(rango_congestion_plot, [6, 8, 10, 10]),
            name="Severe",
            showlegend=False,
        ),
        row=4,
        col=1,
    )

    fig.update_layout(
        height=1000, title_text="Fuzzy System Membership Functions", showlegend=True
    )

    fig.update_xaxes(title_text="Vehicles/minute", row=1, col=1)
    fig.update_xaxes(title_text="Speed (km/h)", row=2, col=1)
    fig.update_xaxes(title_text="Density (veh/km)", row=3, col=1)
    fig.update_xaxes(title_text="Congestion Level", row=4, col=1)

    for i in range(1, 5):
        fig.update_yaxes(title_text="Membership Degree", range=[0, 1.1], row=i, col=1)

    joblib.dump(fig, cache_path)
    fig.show()


# --------------------------------------------------
# Interactive 3D surface plot
# --------------------------------------------------


def plot_interactive_3d_surface(density=100, cache_dir="cache/3d_surface"):
    """
    Display a 3D surface plot of congestion level as a function of vehicles and speed.

    The density value is passed as a parameter. The result is cached to avoid recomputation.

    Args:
        density (int or float): Density value in vehicles/km for which to compute the surface.
        cache_dir (str): Directory where the surface plots are cached.

    Returns:
        None

    Raises:
        ValueError: If the provided density is outside the allowed density_range.
    """
    if density < np.min(density_range) or density > np.max(density_range):
        raise ValueError(
            f"Density {density} is out of bounds. Must be within {np.min(density_range)} and {np.max(density_range)}."
        )

    res = 30
    vehicles = np.linspace(0, 50, res)
    speed = np.linspace(0, 60, res)

    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, f"density_{int(density)}.pkl")

    if os.path.exists(cache_path):
        fig = joblib.load(cache_path)
        print(f"Loaded surface from cache (density={density:.0f})")
        fig.show()
        return

    V, Spd = np.meshgrid(vehicles, speed)
    Cong = np.zeros_like(V)

    for i in range(res):
        for j in range(res):
            simulator.input["vehicles"] = V[i, j]
            simulator.input["speed"] = Spd[i, j]
            simulator.input["density"] = density
            simulator.compute()
            Cong[i, j] = simulator.output["congestion"]

    fig = go.Figure(
        data=[
            go.Surface(
                z=Cong,
                x=V,
                y=Spd,
                colorscale="Viridis",
                hovertemplate=(
                    "<b>Vehicles:</b> %{x:.0f}/min<br>"
                    "<b>Speed:</b> %{y:.0f} km/h<br>"
                    "<b>Congestion:</b> %{z:.2f}<extra></extra>"
                ),
            )
        ]
    )

    fig.update_layout(
        title=f"Congestion Surface (Density = {density:.0f} veh/km)",
        scene=dict(
            xaxis=dict(
                title="Vehicles/minute",
                backgroundcolor="rgb(240, 240, 240)",
                gridcolor="white",
            ),
            yaxis=dict(
                title="Speed (km/h)",
                backgroundcolor="rgb(240, 240, 240)",
                gridcolor="white",
            ),
            zaxis=dict(
                title="Congestion Level",
                backgroundcolor="rgb(240, 240, 240)",
                gridcolor="white",
            ),
            camera=dict(eye=dict(x=1.5, y=-1.5, z=0.8)),
        ),
        margin=dict(l=50, r=50, b=50, t=50),
    )

    joblib.dump(fig, cache_path)
    print(f"Saved surface to cache (density={density:.0f})")
    fig.show()
