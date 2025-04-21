"""
Hierarchical clustering and cluster-level statistics for fuzzy output analysis.

This module provides functionality to perform 1D hierarchical clustering on the
crisp output values produced by the fuzzy inference system, and to compute
descriptive statistics for each resulting cluster.

Functions:
    - apply_clustering: Perform hierarchical clustering on congestion output values.
    - compute_cluster_stats: Compute summary statistics per cluster.
"""

from scipy.cluster.hierarchy import linkage, fcluster

# --------------------------------------------------
# Clustering Parameters
# --------------------------------------------------

#: Linkage method used for hierarchical clustering (e.g., 'ward', 'average', 'complete').
METHOD = "ward"

#: Distance metric used for clustering (e.g., 'euclidean', 'cityblock').
METRIC = "euclidean"

#: Threshold value used to cut the dendrogram and form flat clusters.
DISSIMILARITY = 2

#: Criterion for forming flat clusters from the linkage matrix (typically 'distance').
CRITERION = "distance"

#: Number of decimal places to round numeric outputs in statistical summaries.
ROUND = 2

# --------------------------------------------------
# Clustering
# --------------------------------------------------


def apply_clustering(df):
    """
    Apply hierarchical clustering to congestion output values.

    Extracts the 'value' column from the input DataFrame and performs
    1D hierarchical clustering using the configured method and metric.

    Args:
        df (pd.DataFrame): DataFrame containing the column 'value' (crisp output from fuzzy logic).

    Returns:
        tuple:
            - np.ndarray: Array of cluster labels assigned to each row.
            - np.ndarray: Linkage matrix representing the hierarchical tree.
    """
    # Convertir a array 2D para el clustering
    values = df[["value"]].values
    Z = linkage(values, method=METHOD, metric=METRIC)
    return fcluster(Z, DISSIMILARITY, criterion=CRITERION), Z


# --------------------------------------------------
# Cluster Statistics
# --------------------------------------------------


def compute_cluster_stats(df, clusters):
    """
    Compute descriptive statistics for each cluster.

    Assigns each row to a cluster and calculates:
        - Mode of 'Expected' and 'Predicted' labels
        - Mean and standard deviation of fuzzy output value
        - Mean of original traffic features (VPM, Speed, Density)

    Args:
        df (pd.DataFrame): DataFrame with fuzzy output and traffic features.
        clusters (np.ndarray): Array of cluster labels.

    Returns:
        tuple:
            - pd.DataFrame: Original DataFrame with a new 'cluster' column.
            - pd.DataFrame: Cluster-level statistics with the following columns:
                - Cluster
                - Expected Mode
                - Predicted Mode
                - Congestion Mean
                - Congestion Std
                - VPM Mean
                - Speed Mean
                - Density Mean
    """
    df_results = df.copy()
    df_results["cluster"] = clusters

    stats = (
        df_results.groupby("cluster")
        .agg(
            {
                "Expected": lambda x: x.mode().iloc[0] if not x.mode().empty else None,
                "Predicted": lambda x: x.mode()[0],
                "value": ["mean", lambda x: x.std(ddof=0)],
                "VPM": "mean",
                "Speed (km/h)": "mean",
                "Density (veh/km)": "mean",
            }
        )
        .reset_index()
    )

    stats.columns = [
        "Cluster",
        "Expected Mode",
        "Predicted Mode",
        "Congestion Mean",
        "Congestion Std",
        "VPM Mean",
        "Speed Mean",
        "Density Mean",
    ]

    return df_results, stats.round(ROUND)
