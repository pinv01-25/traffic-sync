.. traffic-sync documentation master file.

traffic-sync
============

Intelligent Traffic Management System
-------------------------------------

**traffic-sync** is a traffic management system designed to detect congestion levels (none, mild, or severe) using fuzzy logic and hierarchical clustering, and to optimize traffic light timing through Particle Swarm Optimization (PSO), a population-based metaheuristic algorithm.

The project leverages techniques from soft computing and optimization to dynamically improve urban traffic flow, aiming for more responsive and efficient signal control in real-time traffic scenarios.

.. note::

   This documentation provides technical insights into the architecture, modules, and logic behind the system.

Project Contents
----------------

This documentation includes:

- Descriptions of the methods and algorithms used.
- Implementation details of the FL (Fuzzy Logic), HC (Hierarchical Clustering), and PSO (Particle Swarm Optimization) modules.
- The structure and purpose of the main execution script.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules/fuzzy/fuzzy
   modules/cluster/cluster
   modules/PSO
