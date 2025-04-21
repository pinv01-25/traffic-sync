"""
PSO-based optimization for traffic signal green time allocation.

This module implements the Particle Swarm Optimization (PSO) logic to optimize
the allocation of green light durations in traffic clusters. Congestion levels
are evaluated using a Mamdani-type fuzzy logic system, and PSO iteratively
minimizes congestion by adjusting green time per cluster.

Functions:
    - pso_optimized: Enhanced PSO with early stopping and partial restarts.
    - pso: Baseline PSO implementation.
"""

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from modules.fuzzy.evaluation import get_congestion_category
from modules.pso.fitness import fitness_function, calculate_green_time
from modules.pso.fitness import T_MIN, CYCLE_TIME

# --------------------------------------------------
# PSO Configuration Parameters
# --------------------------------------------------

#: Number of particles in the swarm.
PARTICLES = 30

#: Maximum number of iterations for PSO.
MAX_ITER = 100

#: Inertia weight (controls the impact of previous velocity on the current one).
W = 0.8

#: Cognitive component (particle's memory of its best-known position).
C1 = 1.5

#: Social component (swarm-wide memory of best-known position).
C2 = 1.5


# --------------------------------------------------
# Early Stopping Parameters
# --------------------------------------------------

#: Number of iterations allowed without improvement before early stopping.
PATIENCE = 10

#: Minimum required improvement between iterations to avoid triggering early stopping.
IMPROVEMENT_THRESHOLD = 1e-3

# --------------------------------------------------
# PSO Optimization
# --------------------------------------------------


def pso(clusters_df):
    """
    Execute PSO optimization for traffic signal timing with early stopping and restart mechanisms.

    This function applies Particle Swarm Optimization to determine optimal green light durations
    for each traffic cluster. It minimizes congestion estimated by a Mamdani fuzzy inference system.
    The algorithm incorporates early stopping based on stagnation and re-diversification when stuck
    in poor local minima.

    Args:
        clusters_df (pd.DataFrame): DataFrame containing per-cluster traffic metrics. Required columns:
            - 'Cluster'
            - 'VPM Mean'
            - 'Speed Mean'
            - 'Density Mean'
            - 'Expected Mode'
            - 'Predicted Mode'
            - 'Congestion Mean'

    Returns:
        pd.DataFrame: Optimized results indexed by cluster, containing:
            - Green: Optimal green time (s)
            - Red: Remaining red time (s)
            - Cycle: Total cycle time (s)
            - Base Green: Initial green time estimated by traffic formula
            - Optimized Congestion: Congestion level from fuzzy output
            - Optimized Category: Linguistic category of congestion
    """
    # Dictionary to store optimization results per cluster
    results = {}

    # Iterate over unique cluster labels
    for cluster in clusters_df["Cluster"].unique():
        # Extract representative row for the cluster
        cluster_data = clusters_df[clusters_df["Cluster"] == cluster].iloc[0]

        # Initialize particles around base green time estimate
        base_green = calculate_green_time(cluster_data)
        particles = np.random.normal(loc=base_green, scale=5.0, size=(PARTICLES, 1))
        particles = np.clip(particles, T_MIN, CYCLE_TIME - 20)
        velocities = np.zeros_like(particles)
        best_positions = particles.copy()

        # Evaluate fitness of initial particles in parallel
        best_scores = np.array(
            Parallel(n_jobs=-1)(
                delayed(fitness_function)(p, cluster_data) for p in particles
            )
        )

        # Determine global best solution
        global_best_idx = np.argmin(best_scores)
        global_best = particles[global_best_idx]

        # Early stopping configuration
        no_improvement = 0
        last_best = best_scores[global_best_idx]

        # Run PSO loop
        for _ in range(MAX_ITER):
            for i in range(PARTICLES):
                # Velocity update with adaptive formula
                r1, r2 = np.random.rand(2)
                velocities[i] = (
                    W * velocities[i]
                    + C1 * r1 * (best_positions[i] - particles[i])
                    + C2 * r2 * (global_best - particles[i])
                )
                particles[i] = np.clip(
                    particles[i] + velocities[i], T_MIN, CYCLE_TIME - 20
                )
            # Re-evaluate fitness after updates
            scores = np.array(
                Parallel(n_jobs=-1)(
                    delayed(fitness_function)(p, cluster_data) for p in particles
                )
            )

            for i in range(PARTICLES):
                current_score = scores[i]
                if current_score < best_scores[i]:
                    best_scores[i] = current_score
                    best_positions[i] = particles[i].copy()
                if current_score < best_scores[global_best_idx]:
                    global_best_idx = i
                    global_best = particles[i].copy()

            current_best = best_scores[global_best_idx]
            if abs(last_best - current_best) < IMPROVEMENT_THRESHOLD:
                no_improvement += 1
            else:
                no_improvement = 0
            last_best = current_best

            # Restart particles if stuck in poor minima
            if no_improvement >= PATIENCE:
                if best_scores[global_best_idx] > 5:
                    restart_idx = np.random.choice(
                        PARTICLES, size=PARTICLES // 5, replace=False
                    )
                    for idx in restart_idx:
                        particles[idx] = np.random.normal(loc=base_green, scale=10.0)
                        particles[idx] = np.clip(particles[idx], T_MIN, CYCLE_TIME - 20)
                        velocities[idx] = 0
                    no_improvement = 0
                else:
                    break

        # Extract optimal green time from best global position
        green_time = float(global_best[0])

        # Store results for the cluster
        results[cluster] = {
            "Green": green_time,
            "Red": CYCLE_TIME - green_time,
            "Cycle": CYCLE_TIME,
            "Base Green": base_green,
            "Optimized Congestion": float(best_scores[global_best_idx]),
            "Optimized Category": get_congestion_category(
                float(best_scores[global_best_idx])
            ),
            "Improvement": f"{(cluster_data['Congestion Mean'] - best_scores[global_best_idx]) * 10:.2f}%",
            "Optimized VPM": cluster_data["VPM Mean"] * (green_time / CYCLE_TIME),
            "Optimized Speed": cluster_data["Speed Mean"]
            * (1 + 0.01 * (green_time - T_MIN)),
            "Optimized Density": cluster_data["Density Mean"]
            * ((CYCLE_TIME - green_time) / CYCLE_TIME),
        }
    return pd.DataFrame(results).T
