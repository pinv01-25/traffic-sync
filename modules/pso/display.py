"""
Display optimization results for PSO-based traffic analysis.

This module provides a function to present the output of traffic signal timing
optimization using Particle Swarm Optimization (PSO). Results are shown in a
well-formatted table including both the base and optimized metrics for each cluster.

Functions:
    - display_optimization_results: Print a comparison of base and optimized values per cluster.
"""

from tabulate import tabulate


def display_optimization_results(optimization_results, clusters_df):
    """
    Display traffic signal optimization results in a tabular format.

    This function merges the original cluster data with the PSO optimization results
    and prints a table comparing key metrics such as congestion levels, base vs. optimized
    green/red timing, and congestion categories.

    Args:
        optimization_results (pd.DataFrame): DataFrame containing the optimized values for each cluster.
            It must include the following columns:
            - "Green"
            - "Red"
            - "Cycle"
            - "Base Green"
            - "Optimized Congestion"
            - "Optimized Category"
        clusters_df (pd.DataFrame): DataFrame with original cluster statistics, including:
            - "Cluster"
            - "Expected Mode"
            - "Predicted Mode"
            - "Congestion Mean"

    Returns:
        None
    """
    # Merge original cluster data with optimization results by matching cluster ID
    merged_data = clusters_df.merge(
        optimization_results, left_on="Cluster", right_index=True
    )

    # Define the columns to include in the output table
    display_cols = [
        "Cluster",
        "Expected Mode",
        "Predicted Mode",
        "Congestion Mean",
        "Base Green",
        "Green",
        "Red",
        "Cycle",
        "Optimized Congestion",
        "Optimized Category",
        "Improvement",
    ]
    
    # Modify headers to use newline (\n) instead of spaces to allow multi-line column titles
    formatted_headers = [col.replace(" ", "\n").title() for col in display_cols]

    # Render the formatted table using tabulate for clean CLI output
    print(
        tabulate(
            merged_data[display_cols],
            headers=formatted_headers,
            tablefmt="fancy_grid",
            floatfmt=".2f",
            showindex=False,
        )
    )
