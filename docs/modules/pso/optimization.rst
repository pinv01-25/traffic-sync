PSO Optimization Engine
=======================

This module defines the main Particle Swarm Optimization (PSO) routine for optimizing
traffic light green time allocations. It processes each cluster of traffic sensor data
independently and minimizes the fuzzy congestion output by adjusting green time values.

Core features:

- PSO loop with adaptive velocity updates (cognitive + social learning).
- Integration with fuzzy inference for congestion evaluation.
- Cluster-level results including green/red timings and congestion category.

.. automodule:: modules.pso.optimization
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:
   :special-members: __doc__
