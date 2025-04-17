"""
Hierarchical dendrogram visualization using Plotly.

This module provides tools to render a dendrogram based on the results of hierarchical
clustering over fuzzy system output values. It includes styling, parameter annotations,
threshold display, and result caching for performance.

Functions:
    - show_dendrogram: Generate and display a styled dendrogram using cached or computed data.
"""

import os
import joblib
import plotly.figure_factory as ff
from modules.cluster.clustering import METHOD, METRIC, DISSIMILARITY

# --------------------------------------------------
# Visualization
# --------------------------------------------------


def show_dendrogram(data, labels, cache_path="cache/dendogram.pkl"):
    """
    Generate and display a hierarchical dendrogram using Plotly.

    This function visualizes the linkage matrix as a dendrogram with custom
    styling. A dissimilarity threshold line is drawn, and clustering parameters
    are shown in the subtitle. The figure is cached locally for reuse.

    Args:
        data (np.ndarray): 2D numeric array representing the input to be clustered (e.g., fuzzy output values).
        labels (list of str): List of labels for each leaf node (e.g., sensor identifiers).
        cache_path (str): Path to store or load the cached dendrogram Plotly figure.

    Returns:
        None
    """
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)

    # Load cached figure if available
    if os.path.exists(cache_path):
        fig = joblib.load(cache_path)
        print("Plotly dendrogram loaded from cache.")
        fig.show()
        return

    # Create dendrogram from input data
    fig = ff.create_dendrogram(data, labels=labels, orientation="bottom")

    # Compute max vertical value (height) to set y-axis range
    max_distance = max(
        (trace.y.max() for trace in fig.data if hasattr(trace, "y")), default=1.0
    )

    # Add dissimilarity threshold line
    fig.add_shape(
        type="line",
        x0=0,
        x1=1,
        y0=DISSIMILARITY,
        y1=DISSIMILARITY,
        line=dict(color="crimson", width=2, dash="dash"),
        xref="paper",
        yref="y",
    )

    # Add annotation for the threshold
    fig.add_annotation(
        x=0,
        y=DISSIMILARITY,
        xref="paper",
        yref="y",
        text=f"Dissimilarity = {DISSIMILARITY}",
        showarrow=False,
        font=dict(color="crimson", size=12),
        xanchor="left",
        yanchor="bottom",
        align="left",
        bgcolor="rgba(255,255,255,0.8)",
    )

    # Subtitle with clustering details
    details = (
        f"Method: {METHOD.capitalize()} | "
        f"Metric: {METRIC.capitalize()} | "
        f"Dissimilarity: {DISSIMILARITY}"
    )

    # Apply layout styling
    fig.update_layout(
        autosize=True,
        height=650,
        title=dict(
            text=f"Hierarchical Relationship Between Sensors<br><sub>{details}</sub>",
            x=0.5,
            xanchor="center",
        ),
        font=dict(size=12),
        margin=dict(l=60, r=60, t=100, b=140),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )

    # X-axis formatting
    fig.update_xaxes(
        title_text="Sensors",
        tickangle=45,
        automargin=True,
        showgrid=True,
        showline=True,
        linecolor="gray",
        mirror=True,
    )

    # Y-axis formatting
    fig.update_yaxes(
        title_text="Distance",
        showgrid=True,
        showline=True,
        linecolor="gray",
        mirror=True,
        range=[0, max(max_distance, DISSIMILARITY) * 1.05],
    )

    # Save figure to cache
    joblib.dump(fig, cache_path)
    print("Plotly dendrogram generated and cached.")
    fig.show()
