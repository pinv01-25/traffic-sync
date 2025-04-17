"""
PSO-based optimization for traffic signal green time allocation.

This module implements the Particle Swarm Optimization (PSO) logic to optimize the
duration of green lights for traffic clusters. It evaluates congestion levels using
a Mamdani-type fuzzy logic system and iteratively minimizes congestion by adjusting
green times for each cluster.

Functions:
    - traffic_pso_optimization: Run PSO optimization on clustered traffic data.
"""

from tqdm import tqdm
import numpy as np
import pandas as pd
from modules.fuzzy.evaluation import get_congestion_category
from modules.pso.fitness import fitness_function, calculate_green_time
from modules.pso.fitness import T_MIN, CYCLE_TIME
from modules.pso.display import display_optimization_results

# --------------------------------------------------
# PSO Configuration Parameters
# --------------------------------------------------

#: Number of particles in the swarm.
PARTICLES = 30

#: Maximum number of iterations for PSO.
MAX_ITER = 100


# --------------------------------------------------
# PSO Optimization
# --------------------------------------------------


def traffic_pso_optimization(clusters_df):
    """
    Run Particle Swarm Optimization (PSO) for each traffic cluster.

    This function applies PSO to optimize green time allocation in a fixed traffic signal cycle.
    Each cluster is processed independently, using fuzzy logic to evaluate congestion,
    and the best configuration is stored.

    Args:
        clusters_df (pd.DataFrame): DataFrame containing per-cluster traffic statistics.
            It must include the following columns:
            - "Cluster": Cluster identifier.
            - "VPM Mean": Mean vehicles per minute.
            - "Speed Mean": Mean traffic speed (km/h).
            - "Density Mean": Mean vehicle density (veh/km).
            - "Expected Mode", "Predicted Mode", "Congestion Mean".

    Returns:
        pd.DataFrame: DataFrame indexed by cluster, including:
            - Green (float): Optimized green time (seconds).
            - Red (float): Remaining red time (seconds).
            - Cycle (float): Total cycle time (seconds).
            - Base Green (float): Green time from academic formula.
            - Optimized Congestion (float): Fuzzy output congestion level.
            - Optimized Category (str): Linguistic label ('none', 'mild', or 'severe').
    """
    # Dictionary to store optimization results per cluster
    results = {}

    # Iterate over unique cluster labels
    for cluster in tqdm(clusters_df["Cluster"].unique(), desc="Processing Clusters"):
        print(f"\nOptimizing Cluster: {cluster}")

        # Extract representative row for the cluster
        cluster_data = clusters_df[clusters_df["Cluster"] == cluster].iloc[0]

        # Initialize particle positions and velocities within valid range
        particles = np.random.uniform(T_MIN, CYCLE_TIME - 20, (PARTICLES, 1))
        velocities = np.zeros_like(particles)
        best_positions = particles.copy()

        # Evaluate initial fitness for each particle
        best_scores = np.array([fitness_function(p, cluster_data) for p in particles])

        # Determine global best solution
        global_best_idx = np.argmin(best_scores)
        global_best = particles[global_best_idx]

        # PSO adaptive parameters
        w = 0.8  # Inertia weight
        c1 = 1.5  # Cognitive learning factor
        c2 = 1.5  # Social learning factor

        # Run PSO loop
        for _ in tqdm(range(MAX_ITER), desc=f"PSO Cluster [{cluster}]", leave=False):
            for i in range(PARTICLES):
                current_score = fitness_function(particles[i], cluster_data)

                # Update personal best
                if current_score < best_scores[i]:
                    best_scores[i] = current_score
                    best_positions[i] = particles[i].copy()

                # Update global best
                if current_score < best_scores[global_best_idx]:
                    global_best_idx = i
                    global_best = particles[i].copy()

                # Velocity update with adaptive formula
                r1, r2 = np.random.rand(2)
                velocities[i] = (
                    w * velocities[i]
                    + c1 * r1 * (best_positions[i] - particles[i])
                    + c2 * r2 * (global_best - particles[i])
                )

                # Update particle position with boundary clipping
                particles[i] = np.clip(
                    particles[i] + velocities[i], T_MIN, CYCLE_TIME - 20
                )

        # Extract optimal green time from best global position
        green_time = float(global_best[0])

        ## Store results for the cluster
        results[cluster] = {
            "Green": green_time,
            "Red": CYCLE_TIME - green_time,
            "Cycle": CYCLE_TIME,
            "Base Green": calculate_green_time(cluster_data),
            "Optimized Congestion": float(best_scores[global_best_idx]),
            "Optimized Category": get_congestion_category(
                float(best_scores[global_best_idx])
            ),
        }

        print(
            f"Cluster {cluster} optimized: Green={green_time:.2f}, Congestion={best_scores[global_best_idx]:.2f}"
        )

    # Display results in tabular format
    display_optimization_results(pd.DataFrame(results).T, clusters_df)

    return pd.DataFrame(results).T
