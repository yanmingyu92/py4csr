Functional Module
=================

The functional module provides a functional programming interface for building clinical reports with method chaining.

FunctionalConfig
----------------

.. autoclass:: py4csr.functional.config.FunctionalConfig
   :members:
   :undoc-members:
   :show-inheritance:

StatisticalTemplates
--------------------

.. autoclass:: py4csr.functional.statistical_templates.StatisticalTemplates
   :members:
   :undoc-members:
   :show-inheritance:

TableBuilder
------------

.. autoclass:: py4csr.functional.table_builder.TableBuilder
   :members:
   :undoc-members:
   :show-inheritance:

OutputGenerators
----------------

.. automodule:: py4csr.functional.output_generators
   :members:
   :undoc-members:
   :show-inheritance:

Example Usage
-------------

.. code-block:: python

   from py4csr.functional import FunctionalConfig, StatisticalTemplates
   import pandas as pd

   # Create configuration
   config = FunctionalConfig.clinical_standard()
   
   # Create statistical templates
   templates = StatisticalTemplates(config)
   
   # Load data
   data = pd.DataFrame({
       "AGE": [25, 30, 35, 40, 45, 50, 55, 60],
       "TRT": [1, 1, 1, 1, 2, 2, 2, 2]
   })
   
   # Calculate continuous statistics
   result = templates.calculate_continuous_statistics(
       data=data,
       variable="AGE",
       treatment_var="TRT",
       statistics=["n", "mean", "std", "median", "min", "max"]
   )
   
   print(result)

