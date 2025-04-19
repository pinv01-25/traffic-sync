"""
Execution and display of hierarchical clustering on fuzzy congestion outputs.

This module provides functions to:
- Perform hierarchical clustering using crisp fuzzy outputs
- Display cluster summaries and detailed sensor assignments
- Visualize results using a dendrogram

Functions:
    - hierarchical_clustering: Execute clustering and optionally display results
    - run_clustering_test: Run a test dataset through the clustering pipeline
"""

import pandas as pd
from tabulate import tabulate
from modules.cluster.clustering import apply_clustering, compute_cluster_stats
from modules.cluster.visualization import show_dendrogram

# --------------------------------------------------
# Main Clustering Function
# --------------------------------------------------


def hierarchical_clustering(df, no_plot=True):
    """
    Perform hierarchical clustering on fuzzy output values.

    This function applies clustering to the crisp 'value' column in the input DataFrame.
    It optionally prints a summary table of the clusters, a detailed sensor-level view,
    and generates a dendrogram visualization.

    Args:
        df (pd.DataFrame): DataFrame containing the following columns:
            - 'value': Crisp output value from fuzzy inference
            - 'VPM': Vehicles per minute
            - 'Speed (km/h)': Average speed in km/h
            - 'Density (veh/km)': Vehicle density
            - 'Expected': Ground truth congestion label
            - 'Predicted': Label inferred from fuzzy system
        no_plot (bool): If True, suppresses plotting of the dendrogram.

    Returns:
        pd.DataFrame: DataFrame with cluster analysis results.
    """
    # Apply hierarchical clustering
    clusters, Z = apply_clustering(df)

    # Compute cluster-level statistics
    df_results, stats = compute_cluster_stats(df, clusters)

    # Generate sensor labels for dendrogram
    labels = [f"Sensor {i + 1}" for i in range(len(df))]

    # Print cluster summary
    print("\nCluster Analysis:")
    print(
        tabulate(
            stats,
            headers="keys",
            tablefmt="fancy_grid",
            showindex=False,
            numalign="center",
        )
    )

    # Print detailed results per sensor
    print("\nSensor Details:")
    print(
        tabulate(
            df_results[
                [
                    "VPM",
                    "Speed (km/h)",
                    "Density (veh/km)",
                    "Expected",
                    "Predicted",
                    "cluster",
                ]
            ].head(),
            headers=[
                "VPM",
                "Speed (km/h)",
                "Density",
                "Expected",
                "Predicted",
                "Cluster",
            ],
            tablefmt="fancy_grid",
            showindex=False,
        )
    )
    if not no_plot:
        # Visualize dendrogram
        show_dendrogram(df[["value"]].values, labels)

    return stats


# --------------------------------------------------
# Clustering Test Execution
# --------------------------------------------------


def run_clustering_test(df=None, no_plot=True):
    """
    Run predefined test cases to validate hierarchical clustering.

    This function uses a small fixed dataset of traffic inputs and expected
    congestion labels to demonstrate and validate the clustering process.

    Args:
        df (pd.DataFrame, optional): Optional custom DataFrame to override test set.

    Returns:
        pd.DataFrame: Final DataFrame with cluster assignments and original inputs.
    """
    if df is None:
        # Sample traffic dataset with expected categories
        data = [
            {"vpm": 15, "spd": 50, "den": 60, "expected": "none"},
            {"vpm": 30, "spd": 35, "den": 90, "expected": "mild"},
            {"vpm": 45, "spd": 20, "den": 130, "expected": "severe"},
            {"vpm": 25, "spd": 40, "den": 70, "expected": "mild"},
            {"vpm": 30, "spd": 50, "den": 60, "expected": "none"},
            {"vpm": 20, "spd": 30, "den": 140, "expected": "mild"},
            {"vpm": 35, "spd": 15, "den": 100, "expected": "severe"},
        ]

        df = pd.DataFrame(data)

    return hierarchical_clustering(df, no_plot)
