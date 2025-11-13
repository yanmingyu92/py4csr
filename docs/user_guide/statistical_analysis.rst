Statistical Analysis
====================

py4csr provides comprehensive statistical analysis capabilities through pre-configured templates and customizable calculations.

Statistical Templates
---------------------

Overview
~~~~~~~~

py4csr includes **statistical templates** that define:

- Standard clinical trial statistics
- Formatting rules for each statistic
- Applicable data types (continuous, categorical)
- Precision and display options

Available Statistics
~~~~~~~~~~~~~~~~~~~~

**Continuous Statistics**:

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Statistic
     - Code
     - Description
   * - Count
     - ``n``
     - Number of non-missing observations
   * - Mean
     - ``mean``
     - Arithmetic mean
   * - Standard Deviation
     - ``sd``
     - Standard deviation
   * - Mean (SD)
     - ``mean_sd``
     - Mean (SD) formatted together
   * - Median
     - ``median``
     - Median value
   * - Q1
     - ``q1``
     - First quartile (25th percentile)
   * - Q3
     - ``q3``
     - Third quartile (75th percentile)
   * - Q1, Q3
     - ``q1q3``
     - Q1, Q3 formatted together
   * - Minimum
     - ``min``
     - Minimum value
   * - Maximum
     - ``max``
     - Maximum value
   * - Min, Max
     - ``min_max``
     - Min, Max formatted together
   * - CV%
     - ``cv``
     - Coefficient of variation (%)
   * - Geometric Mean
     - ``geomean``
     - Geometric mean
   * - Standard Error
     - ``se``
     - Standard error of the mean

**Categorical Statistics**:

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Statistic
     - Code
     - Description
   * - Count
     - ``n``
     - Number of subjects
   * - Percentage
     - ``pct``
     - Percentage of subjects
   * - n (%)
     - ``npct``
     - Count and percentage formatted together

Using Statistical Templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Basic Usage**:

.. code-block:: python

   from py4csr.clinical import ClinicalSession

   session = ClinicalSession(uri="STUDY001")
   session.define_report(dataset=adsl, subjid="USUBJID")
   session.add_trt(name="TRT01PN", decode="TRT01P")

   # Continuous variable with multiple statistics
   session.add_var(
       name="AGE",
       label="Age (years)",
       stats="n mean+sd median q1q3 min+max"
   )

   # Categorical variable
   session.add_catvar(
       name="SEX",
       label="Sex, n (%)",
       stats="npct"
   )

**Functional Interface**:

.. code-block:: python

   from py4csr.functional import StatisticalTemplates, FunctionalConfig

   # Get standard configuration
   config = FunctionalConfig.clinical_standard()

   # Calculate continuous statistics
   templates = StatisticalTemplates(config)
   stats = templates.calculate_continuous_statistics(
       data=adsl['AGE'],
       statistics=["n", "mean", "sd", "median", "min", "max"]
   )

   print(stats)
   # {'n': 150, 'mean': 45.3, 'sd': 12.1, 'median': 44.0, ...}

Continuous Variable Analysis
-----------------------------

Descriptive Statistics
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from py4csr.clinical import ClinicalSession

   session = ClinicalSession(uri="STUDY001")
   session.define_report(dataset=adsl, subjid="USUBJID")
   session.add_trt(name="TRT01PN", decode="TRT01P")

   # Age analysis
   session.add_var(
       name="AGE",
       label="Age (years)",
       stats="n mean+sd median q1q3 min+max"
   )

   # Weight analysis
   session.add_var(
       name="WEIGHT",
       label="Weight (kg)",
       stats="n mean+sd median min+max"
   )

   # Height analysis
   session.add_var(
       name="HEIGHT",
       label="Height (cm)",
       stats="n mean+sd median min+max"
   )

Change from Baseline
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Calculate change from baseline
   adlb['CHG'] = adlb['AVAL'] - adlb['BASE']

   # Analyze change
   session.add_var(
       name="CHG",
       label="Change from Baseline",
       stats="n mean+sd median q1q3 min+max"
   )

Percent Change from Baseline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Calculate percent change
   adlb['PCHG'] = ((adlb['AVAL'] - adlb['BASE']) / adlb['BASE']) * 100

   # Analyze percent change
   session.add_var(
       name="PCHG",
       label="Percent Change from Baseline (%)",
       stats="n mean+sd median q1q3 min+max"
   )

Categorical Variable Analysis
------------------------------

Frequency Counts
~~~~~~~~~~~~~~~~

.. code-block:: python

   from py4csr.clinical import ClinicalSession

   session = ClinicalSession(uri="STUDY001")
   session.define_report(dataset=adsl, subjid="USUBJID")
   session.add_trt(name="TRT01PN", decode="TRT01P")

   # Sex distribution
   session.add_catvar(
       name="SEX",
       label="Sex, n (%)",
       stats="npct",
       codelist="M='Male',F='Female'"
   )

   # Race distribution
   session.add_catvar(
       name="RACE",
       label="Race, n (%)",
       stats="npct"
   )

Nested Categories
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Adverse events by system organ class and preferred term
   session.add_catvar(
       name="AEBODSYS",
       label="System Organ Class",
       stats="npct",
       nested_var="AEDECOD",
       nested_label="  Preferred Term"
   )

Custom Categories
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Age groups with custom categories
   session.add_catvar(
       name="AGEGR1",
       label="Age Group, n (%)",
       stats="npct",
       codelist="<18='<18 years',18-65='18-65 years',>65='>65 years'"
   )

Statistical Tests
-----------------

Continuous Variables
~~~~~~~~~~~~~~~~~~~~

**ANOVA (Analysis of Variance)**:

.. code-block:: python

   from py4csr.clinical import ClinicalStatisticalEngine

   engine = ClinicalStatisticalEngine()

   # Perform ANOVA
   result = engine.perform_anova(
       data=adsl,
       variable="AGE",
       treatment="TRT01PN"
   )

   print(f"F-statistic: {result['f_statistic']:.3f}")
   print(f"p-value: {result['p_value']:.4f}")

**t-test**:

.. code-block:: python

   from scipy import stats

   # Two-sample t-test
   group1 = adsl[adsl['TRT01P'] == 'Placebo']['AGE']
   group2 = adsl[adsl['TRT01P'] == 'Drug 10mg']['AGE']

   t_stat, p_value = stats.ttest_ind(group1, group2)
   print(f"t-statistic: {t_stat:.3f}, p-value: {p_value:.4f}")

Categorical Variables
~~~~~~~~~~~~~~~~~~~~~

**Chi-Square Test**:

.. code-block:: python

   from py4csr.clinical import ClinicalStatisticalEngine

   engine = ClinicalStatisticalEngine()

   # Perform chi-square test
   result = engine.perform_chi_square(
       data=adsl,
       variable="SEX",
       treatment="TRT01P"
   )

   print(f"Chi-square: {result['chi_square']:.3f}")
   print(f"p-value: {result['p_value']:.4f}")

**Fisher's Exact Test**:

.. code-block:: python

   # For small sample sizes
   result = engine.perform_fisher_exact(
       data=adsl,
       variable="RACE",
       treatment="TRT01P"
   )

   print(f"p-value: {result['p_value']:.4f}")

Custom Statistics
-----------------

Defining Custom Statistics
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from py4csr.functional import FunctionalConfig, StatisticDefinition

   # Create custom configuration
   config = FunctionalConfig.clinical_standard()

   # Add custom statistic
   config.statistics["range"] = StatisticDefinition(
       name="range",
       display_name="Range",
       description="Max - Min",
       precision=1,
       applicable_types=["continuous"]
   )

   # Define calculation function
   def calculate_range(data):
       return data.max() - data.min()

   # Register function
   config.register_statistic_function("range", calculate_range)

Using Custom Statistics
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from py4csr.functional import StatisticalTemplates

   templates = StatisticalTemplates(config)

   # Calculate with custom statistic
   stats = templates.calculate_continuous_statistics(
       data=adsl['AGE'],
       statistics=["n", "mean", "sd", "range"]
   )

   print(f"Range: {stats['range']}")

Advanced Analysis
-----------------

Subgroup Analysis
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Analyze by subgroup
   for sex in ['M', 'F']:
       subset = adsl[adsl['SEX'] == sex]
       
       stats = templates.calculate_continuous_statistics(
           data=subset['AGE'],
           statistics=["n", "mean", "sd"]
       )
       
       print(f"{sex}: n={stats['n']}, mean={stats['mean']:.1f}")

Stratified Analysis
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Stratify by multiple factors
   for sex in ['M', 'F']:
       for race in adsl['RACE'].unique():
           subset = adsl[(adsl['SEX'] == sex) & (adsl['RACE'] == race)]
           
           if len(subset) > 0:
               stats = templates.calculate_continuous_statistics(
                   data=subset['AGE'],
                   statistics=["n", "mean"]
               )
               print(f"{sex}/{race}: n={stats['n']}, mean={stats['mean']:.1f}")

Time-to-Event Analysis
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from lifelines import KaplanMeierFitter

   # Kaplan-Meier analysis
   kmf = KaplanMeierFitter()
   kmf.fit(
       durations=adtte['AVAL'],
       event_observed=adtte['CNSR'] == 0
   )

   # Get median survival
   median_survival = kmf.median_survival_time_
   print(f"Median survival: {median_survival:.1f} days")

Best Practices
--------------

1. **Choose Appropriate Statistics**

.. code-block:: python

   # For normally distributed data
   stats="n mean+sd median q1q3"

   # For skewed data
   stats="n median q1q3 min+max"

   # For categorical data
   stats="npct"

2. **Report Precision Appropriately**

.. code-block:: python

   # Age (whole years)
   precision=0

   # Lab values (1 decimal)
   precision=1

   # p-values (3-4 decimals)
   precision=4

3. **Include Sample Sizes**

.. code-block:: python

   # Always include 'n' in statistics
   stats="n mean+sd median"  # Good
   stats="mean+sd median"     # Avoid

4. **Document Statistical Methods**

.. code-block:: python

   # Document in table footnotes
   footnotes = [
       "ANOVA used for continuous variables",
       "Chi-square test used for categorical variables",
       "p-values <0.05 considered statistically significant"
   ]

Next Steps
----------

- :doc:`output_generation` - Generate formatted reports
- :doc:`../examples/demographics` - See statistical analysis examples
- :doc:`../advanced/custom_statistics` - Create custom statistics

