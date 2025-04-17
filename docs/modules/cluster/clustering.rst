Hierarchical Clustering Core
============================

This module performs hierarchical clustering on crisp congestion values generated
by the fuzzy inference system. It groups traffic observations using **Ward linkage**
and **Euclidean distance**, and computes statistical summaries for each cluster.

The module includes:

- Clustering parameters: method, metric, dissimilarity threshold, etc.
- Core clustering function using SciPy's `linkage` and `fcluster`.
- Statistical aggregation for each identified cluster.
- Support for input and output formatting as pandas DataFrames.

.. automodule:: modules.cluster.clustering
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:
   :special-members: __doc__
