"""
Display optimization results for PSO-based traffic analysis.

This module provides a function to present the output of traffic signal timing
optimization using Particle Swarm Optimization (PSO). Results are shown in a
well-formatted table including both the base and optimized metrics for each cluster.

Functions:
    - display_optimization_results: Print a comparison of base and optimized values per cluster.
"""

from tabulate import tabulate
from modules.utils import print_section_title


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
        "Predicted Mode",
        "Optimized Category",
        "Congestion Mean",
        "Optimized Congestion",
        "Improvement",
        "Base Green",
        "Green",
        "Red",
        "Cycle",
    ]

    # Modify headers to use newline (\n) instead of spaces to allow multi-line column titles
    column_headers = {
        "Cluster": "Cluster",
        "Predicted Mode": "Original\nCategory",
        "Optimized Category": "Optimized\nCategory",
        "Congestion Mean": "Original\nCongestion",
        "Optimized Congestion": "Optimized\nCongestion",
        "Improvement": "Improvement\n(%)",
        "Base Green": "Base Green\nTime (s)",
        "Green": "Green\nTime (s)",
        "Red": "Red\nTime (s)",
        "Cycle": "Cycle\nTime (s)",
    }

    headers = [column_headers[col] for col in display_cols]

    # Render the formatted table using tabulate for clean CLI output
    print_section_title("🚦 PSO-Based Traffic Light Optimization Summary", width=142)
    print(
        tabulate(
            merged_data[display_cols],
            headers=headers,
            tablefmt="fancy_grid",
            floatfmt=".2f",
            showindex=False,
        )
    )


def display_optimization_comparison(optimization_results, clusters_df):
    """
    Display a comparison between original and optimized traffic data values.

    This includes both fuzzy congestion estimation and physical metrics (VPM, Speed, Density).

    Args:
        optimization_results (pd.DataFrame): Optimized PSO results.
        clusters_df (pd.DataFrame): Original cluster data.

    Returns:
        None
    """
    merged_data = clusters_df.merge(
        optimization_results, left_on="Cluster", right_index=True
    )

    display_cols = [
        "Cluster",
        "Predicted Mode",  # Renamed to "Original Category"
        "Optimized Category",
        "Improvement",
        "Congestion Mean",  # Renamed to "Original Congestion"
        "Optimized Congestion",
        "VPM Mean",  # Renamed to "Original VPM"
        "Optimized VPM",
        "Speed Mean",  # Renamed to "Original Speed"
        "Optimized Speed",
        "Density Mean",  # Renamed to "Original Density"
        "Optimized Density",
    ]

    column_headers = {
        "Cluster": "Cluster",
        "Predicted Mode": "Original\nCategory",
        "Optimized Category": "Optimized\nCategory",
        "Improvement": "Improvement\n(%)",
        "Congestion Mean": "Original\nCongestion",
        "Optimized Congestion": "Optimized\nCongestion",
        "VPM Mean": "Original\nVPM",
        "Optimized VPM": "Optimized\nVPM",
        "Speed Mean": "Original\nSpeed",
        "Optimized Speed": "Optimized\nSpeed",
        "Density Mean": "Original\nDensity",
        "Optimized Density": "Optimized\nDensity",
    }

    headers = [column_headers[col] for col in display_cols]

    # Render the formatted table using tabulate for clean CLI output
    print_section_title("📊 Final Summary: Optimized Traffic Signal Timings", width=167)
    print(
        tabulate(
            merged_data[display_cols],
            headers=headers,
            tablefmt="fancy_grid",
            floatfmt=".2f",
            showindex=False,
        )
    )
