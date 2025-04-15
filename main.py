"""
Main entry point for the fuzzy traffic congestion classification system.

This script launches the full fuzzy logic pipeline including:
- Membership function visualization
- Interactive 3D exploration
- Automated test case evaluation
"""

from modules.fuzzy.visualization import (
    plot_memberships,
    plot_interactive_3d_surface,
)

from modules.fuzzy.evaluation import run_test_cases

# --------------------------------------------------
# Main execution
# --------------------------------------------------

if __name__ == "__main__":
    """
    Run the complete fuzzy logic congestion analysis workflow.

    Displays membership functions, 3D fuzzy output surface,
    interactive point evaluation, and test cases.
    """
    print("\n" + "=" * 60)
    print("Fuzzy Logic-Based Traffic Congestion Classification System")
    print("=" * 60 + "\n")

    # Display fuzzy membership functions
    print("Displaying membership functions...")
    plot_memberships()

    # Interactive 3D exploration of fuzzy output
    print("\nLaunching interactive 3D fuzzy output explorer...")
    plot_interactive_3d_surface()

    # Run predefined test cases
    print("\nRunning test cases for fuzzy evaluation...")
    run_test_cases()
