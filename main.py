"""
Main entry point for the traffic sensor analysis system.

This script orchestrates the full analysis pipeline, which includes:
- Fuzzy logic modeling for traffic congestion classification
- Hierarchical clustering (HC) of traffic sensor patterns
- Interactive visualization tools (membership functions and 3D surfaces)
- Optimization with Particle Swarm Optimization (PSO)

Execution Order:
    1. Visualize fuzzy membership functions
    2. Explore the 3D fuzzy output surface
    3. Load test cases from a JSON file
    4. Run fuzzy test cases for congestion inference
    5. Apply hierarchical clustering to fuzzy output results
    6. Optimize traffic signal timing using PSO
"""

from argparse import ArgumentParser
import json

from modules.fuzzy.visualization import (
    plot_memberships,
    plot_interactive_3d_surface,
)

from modules.fuzzy.evaluation import run_test_cases
from modules.cluster.evaluation import run_clustering_test
from modules.pso.optimization import pso, pso_optimized
import shutil
import os
from modules.utils import generate_random_test_cases

# --------------------------------------------------
# Main execution
# --------------------------------------------------


def main():
    """
    Execute the full traffic analysis pipeline.

    This includes fuzzy logic inference, visualization of the fuzzy system,
    execution of predefined test cases, and hierarchical clustering on
    the fuzzy output to identify sensor behavior patterns.
    """
    parser = ArgumentParser(description="Traffic Sensor Analysis System")
    parser.add_argument("--no-plot", action="store_true", help="Disable plotting")
    parser.add_argument(
        "--no-cache", action="store_true", help="Delete cache folder if it exists"
    )
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("Fuzzy Logic-Based Traffic Congestion Classification System")
    print("=" * 60 + "\n")

    if not args.no_plot:
        # Step 1: Display fuzzy membership functions
        print("Displaying membership functions...")
        plot_memberships()

        # Step 2: Launch interactive 3D fuzzy output surface
        print("\nLaunching interactive 3D fuzzy output explorer...")
        plot_interactive_3d_surface()
    else:
        print("Plotting is disabled via --no-plot.")

    if args.no_cache:
        cache_folder = "cache"
        if os.path.exists(cache_folder):
            print("\nDeleting cache folder...")
            shutil.rmtree(cache_folder)
        else:
            print("\nNo cache folder found to delete.")

    # Step 3: Load or generate test cases
    print("\nWould you like to use default test cases or generate random ones?")
    print("1. Use default test cases")
    print("2. Generate random test cases")

    choice = input("Enter your choice (1 or 2): ").strip()

    if choice == "1":
        print("\nLoading test cases from JSON file...")
        with open("test_cases.json", "r") as f:
            test_data = json.load(f)
    elif choice == "2":
        num_cases = input("Enter the number of random test cases to generate: ").strip()
        while not num_cases.isdigit() or int(num_cases) <= 0:
            print("Please enter a valid positive integer.")
            num_cases = input(
                "Enter the number of random test cases to generate: "
            ).strip()

        num_cases = int(num_cases)
        print(f"\nGenerating {num_cases} random test cases...")
        test_data = generate_random_test_cases(num_cases)
    else:
        print("\nInvalid choice. Defaulting to using default test cases.")

    # Step 4: Evaluate test cases using fuzzy logic
    print("\nRunning test cases for fuzzy evaluation...")
    fuzzy = run_test_cases(test_data)

    print("\n" + "=" * 60)
    print(" Traffic Sensor Clustering System ")
    print("=" * 60)

    # Step 5: Apply hierarchical clustering to fuzzy output
    print("\nRunning test cases for hierarchical clustering...")
    clusters = run_clustering_test(fuzzy, no_plot=args.no_plot)

    print("\n" + "=" * 60)
    print(" PSO Traffic Light Optimization ")
    print("=" * 60)

    print("Select the PSO optimization method:")
    print(
        "1. PSO with early stopping and partial results restarts (very fast, less accurate)"
    )
    print("2. PSO without optimizations (very slow, more accurate)")

    option = input("Enter your choice (1 or 2): ").strip()

    # Step 6: Optimize traffic signal timing using PSO
    if option == "1":
        print("\nRunning PSO with early stopping and partial results restarts...")
    elif option == "2":
        print("\nRunning PSO without optimizations...")
    else:
        print("\nInvalid option selected. Defaulting to PSO with early stopping.")
        option = "1"
    pso_optimized(clusters) if option == "1" else pso(clusters)


if __name__ == "__main__":
    main()
