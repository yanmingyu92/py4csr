Custom Statistics
==================

Learn how to create and use custom statistical calculations in py4csr.

Creating Custom Statistics
---------------------------

Define Statistic
~~~~~~~~~~~~~~~~

.. code-block:: python

   from py4csr.functional import FunctionalConfig, StatisticDefinition

   # Get standard configuration
   config = FunctionalConfig.clinical_standard()

   # Define custom statistic
   config.statistics["cv"] = StatisticDefinition(
       name="cv",
       display_name="CV%",
       description="Coefficient of variation (%)",
       precision=1,
       applicable_types=["continuous"]
   )

Implement Calculation
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def calculate_cv(data):
       """Calculate coefficient of variation."""
       mean = data.mean()
       sd = data.std()
       if mean == 0:
           return 0
       return (sd / mean) * 100

   # Register function
   config.register_statistic_function("cv", calculate_cv)

Use Custom Statistic
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from py4csr.functional import StatisticalTemplates

   templates = StatisticalTemplates(config)
   stats = templates.calculate_continuous_statistics(
       data=adsl['AGE'],
       statistics=["n", "mean", "sd", "cv"]
   )

   print(f"CV%: {stats['cv']:.1f}%")

Advanced Examples
-----------------

Geometric Mean
~~~~~~~~~~~~~~

.. code-block:: python

   import numpy as np

   # Define geometric mean
   config.statistics["geomean"] = StatisticDefinition(
       name="geomean",
       display_name="Geometric Mean",
       description="Geometric mean",
       precision=2,
       applicable_types=["continuous"]
   )

   def calculate_geomean(data):
       """Calculate geometric mean."""
       positive_data = data[data > 0]
       if len(positive_data) == 0:
           return np.nan
       return np.exp(np.log(positive_data).mean())

   config.register_statistic_function("geomean", calculate_geomean)

Confidence Intervals
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from scipy import stats

   # Define 95% CI
   config.statistics["ci95"] = StatisticDefinition(
       name="ci95",
       display_name="95% CI",
       description="95% confidence interval",
       precision=2,
       applicable_types=["continuous"]
   )

   def calculate_ci95(data):
       """Calculate 95% confidence interval."""
       mean = data.mean()
       se = stats.sem(data)
       ci = stats.t.interval(0.95, len(data)-1, loc=mean, scale=se)
       return f"({ci[0]:.2f}, {ci[1]:.2f})"

   config.register_statistic_function("ci95", calculate_ci95)

Next Steps
----------

- :doc:`plotting` - Custom visualizations
- :doc:`regulatory` - Regulatory compliance

