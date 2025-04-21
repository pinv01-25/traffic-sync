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

from modules.cluster.clustering import apply_clustering, compute_cluster_stats

# --------------------------------------------------
# Main Clustering Function
# --------------------------------------------------


def hierarchical_clustering(df):
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
    clusters, _ = apply_clustering(df)

    # Compute cluster-level statistics
    df_results, stats = compute_cluster_stats(df, clusters)

    return stats, df_results
