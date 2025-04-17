"""
Main entry point for the traffic sensor analysis system.

This script orchestrates the full analysis pipeline, which includes:
- Fuzzy logic modeling for traffic congestion classification
- Hierarchical clustering (HC) of traffic sensor patterns
- Interactive visualization tools (membership functions and 3D surfaces)
- (Upcoming) Optimization with Particle Swarm Optimization (PSO)

Execution Order:
    1. Visualize fuzzy membership functions
    2. Explore the 3D fuzzy output surface
    3. Run fuzzy test cases for congestion inference
    4. Apply hierarchical clustering to fuzzy output results
"""

import json

from modules.fuzzy.visualization import (
    plot_memberships,
    plot_interactive_3d_surface,
)

from modules.fuzzy.evaluation import run_test_cases
from modules.cluster.evaluation import run_clustering_test

# --------------------------------------------------
# Main execution
# --------------------------------------------------

if __name__ == "__main__":
    """
    Execute the full traffic analysis pipeline.

    This includes fuzzy logic inference, visualization of the fuzzy system,
    execution of predefined test cases, and hierarchical clustering on
    the fuzzy output to identify sensor behavior patterns.
    """
    print("\n" + "=" * 60)
    print("Fuzzy Logic-Based Traffic Congestion Classification System")
    print("=" * 60 + "\n")

    # Step 1: Display fuzzy membership functions
    print("Displaying membership functions...")
    plot_memberships()

    # Step 2: Launch interactive 3D fuzzy output surface
    print("\nLaunching interactive 3D fuzzy output explorer...")
    plot_interactive_3d_surface()

    # Step 3: Load test cases from JSON file
    print("\nLoading test cases from JSON file...")
    with open("test_cases.json", "r") as f:
        test_data = json.load(f)

    # Step 4: Evaluate test cases using fuzzy logic
    print("\nRunning test cases for fuzzy evaluation...")
    fuzzy = run_test_cases(test_data)

    print("\n" + "=" * 60)
    print(" Traffic Sensor Clustering System ")
    print("=" * 60)

    # Step 5: Apply hierarchical clustering to fuzzy output
    print("\nRunning test cases for hierarchical clustering...")
    clusters = run_clustering_test(fuzzy)
