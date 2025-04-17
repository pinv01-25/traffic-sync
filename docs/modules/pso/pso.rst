Traffic Signal Optimization with PSO
====================================

This module implements a Particle Swarm Optimization (PSO) framework to optimize green light durations at traffic intersections. The system operates on traffic clusters generated from fuzzy congestion evaluation, aiming to reduce congestion levels using a Mamdani-type fuzzy inference engine.

Each traffic cluster is optimized independently by simulating green/red time configurations and minimizing the resulting congestion score. The optimization relies on real-world traffic parameters: vehicle density, speed, and flow rate (VPM).

.. toctree::
   :maxdepth: 1

   PSO Optimization Engine <optimization>
   Fitness and Green Time Estimation <fitness>
   Results Display and Table Generator <display>
