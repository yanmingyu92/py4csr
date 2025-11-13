Core Concepts
=============

This page explains the core concepts and design principles of py4csr.

Design Philosophy
-----------------

py4csr is designed around three key principles:

1. **SAS RRG Compatibility**: Provide equivalent functionality to SAS RRG macros
2. **Functional Programming**: Use method chaining and immutable data structures
3. **Clinical Trial Focus**: Built specifically for regulatory-compliant clinical reporting

Two Interfaces
--------------

py4csr provides two complementary interfaces:

Clinical Session Interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The **ClinicalSession** interface is designed for users familiar with SAS RRG. It uses a session-based workflow where you:

1. Create a session
2. Define the report structure
3. Add treatment groups
4. Add variables
5. Generate the table
6. Save the output

.. code-block:: python

   from py4csr.clinical import ClinicalSession

   session = ClinicalSession(uri="STUDY001")
   session.define_report(dataset=adsl, subjid="USUBJID")
   session.add_trt(name="TRT01PN", decode="TRT01P")
   session.add_var(name="AGE", stats="n mean+sd")
   session.generate()
   session.finalize(output_path="table.rtf")

Functional Interface
~~~~~~~~~~~~~~~~~~~~

The **ReportBuilder** interface uses method chaining for a more Pythonic workflow:

.. code-block:: python

   from py4csr.reporting import ReportBuilder

   result = (ReportBuilder(config)
       .init_study(uri="STUDY001")
       .add_dataset("adsl", adsl)
       .define_treatments(var="TRT01P")
       .add_demographics_table()
       .generate_all()
       .finalize()
   )

Both interfaces produce identical output - choose the one that fits your workflow.

Key Components
--------------

Datasets
~~~~~~~~

py4csr works with **ADaM datasets** (Analysis Data Model) following CDISC standards:

- **ADSL**: Subject-Level Analysis Dataset (demographics, baseline)
- **ADAE**: Adverse Events Analysis Dataset
- **ADLB**: Laboratory Analysis Dataset
- **ADVS**: Vital Signs Analysis Dataset
- **ADEFF**: Efficacy Analysis Dataset

Populations
~~~~~~~~~~~

**Populations** define subsets of subjects for analysis:

.. code-block:: python

   builder.define_populations(
       safety="SAFFL=='Y'",      # Safety population
       efficacy="EFFFL=='Y'",    # Efficacy population
       itt="ITTFL=='Y'"          # Intent-to-treat population
   )

Treatments
~~~~~~~~~~

**Treatments** define how subjects are grouped for comparison:

.. code-block:: python

   session.add_trt(
       name="TRT01PN",      # Numeric treatment variable
       decode="TRT01P",     # Character labels
       across="Y"           # Display across columns
   )

Variables
~~~~~~~~~

**Variables** are the data elements to analyze:

- **Continuous variables**: Age, weight, lab values (use ``add_var()``)
- **Categorical variables**: Sex, race, adverse events (use ``add_catvar()``)
- **Condition variables**: Counts based on conditions (use ``add_cond()``)

Statistics
~~~~~~~~~~

**Statistics** define what to calculate:

.. code-block:: python

   # Continuous statistics
   stats="n mean+sd median q1q3 min+max"

   # Categorical statistics
   stats="npct"  # Count and percentage

   # Custom statistics
   stats="n mean median"

Output Formats
~~~~~~~~~~~~~~

py4csr supports multiple output formats:

- **RTF**: Rich Text Format (regulatory standard)
- **PDF**: Portable Document Format (requires reportlab)
- **CSV**: Comma-Separated Values (for data review)
- **HTML**: Web-based output (for interactive review)

Workflow Patterns
-----------------

Single Table Workflow
~~~~~~~~~~~~~~~~~~~~~

For creating a single table:

.. code-block:: python

   session = ClinicalSession(uri="STUDY001")
   session.define_report(dataset=adsl, subjid="USUBJID")
   session.add_trt(name="TRT01PN", decode="TRT01P")
   session.add_var(name="AGE", stats="n mean+sd")
   session.generate()
   session.finalize(output_path="demographics.rtf")

Multiple Tables Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~

For creating multiple related tables:

.. code-block:: python

   builder = ReportBuilder(config)
   builder.init_study(uri="STUDY001")
   builder.add_dataset("adsl", adsl)
   builder.add_dataset("adae", adae)
   builder.define_populations(safety="SAFFL=='Y'")
   builder.define_treatments(var="TRT01P")
   
   # Add multiple tables
   builder.add_demographics_table()
   builder.add_ae_summary_table()
   builder.add_ae_detail_table()
   
   # Generate all at once
   builder.generate_all(output_dir="reports")

Statistical Templates
---------------------

py4csr includes pre-defined statistical templates for common analyses:

Continuous Statistics
~~~~~~~~~~~~~~~~~~~~~

- ``n``: Count of non-missing values
- ``mean``: Arithmetic mean
- ``sd``: Standard deviation
- ``mean_sd``: Mean (SD) formatted
- ``median``: Median value
- ``q1``, ``q3``: First and third quartiles
- ``q1q3``: Q1, Q3 formatted
- ``min``, ``max``: Minimum and maximum
- ``min_max``: Min, Max formatted

Categorical Statistics
~~~~~~~~~~~~~~~~~~~~~~

- ``n``: Count
- ``pct``: Percentage
- ``npct``: n (%) formatted

Custom Statistics
~~~~~~~~~~~~~~~~~

You can define custom statistics using the FunctionalConfig:

.. code-block:: python

   from py4csr.functional import FunctionalConfig, StatisticDefinition

   config = FunctionalConfig.clinical_standard()
   
   # Add custom statistic
   config.statistics["cv"] = StatisticDefinition(
       name="cv",
       display_name="CV%",
       description="Coefficient of variation",
       precision=1,
       applicable_types=["continuous"]
   )

Data Validation
---------------

py4csr includes built-in data validation:

.. code-block:: python

   from py4csr.data import validate_adam_dataset

   # Validate ADSL dataset
   is_valid, errors = validate_adam_dataset(adsl, dataset_type="ADSL")
   
   if not is_valid:
       for error in errors:
           print(f"Validation error: {error}")

Error Handling
--------------

py4csr uses custom exceptions for clear error messages:

.. code-block:: python

   from py4csr.exceptions import (
       DataValidationError,
       ConfigurationError,
       OutputFormatError
   )

   try:
       session.generate()
   except DataValidationError as e:
       print(f"Data validation failed: {e}")
   except ConfigurationError as e:
       print(f"Configuration error: {e}")

Best Practices
--------------

1. **Validate data first**: Always validate your datasets before creating reports
2. **Use standard variable names**: Follow CDISC naming conventions
3. **Document your code**: Add comments explaining the analysis
4. **Version control**: Use git to track changes to reporting scripts
5. **Test with small data**: Develop with a subset before running on full data
6. **Review outputs**: Always review generated tables before submission
7. **Follow regulatory guidelines**: Ensure outputs meet ICH E3 and CTD requirements

Next Steps
----------

- :doc:`quickstart` - Create your first report
- :doc:`user_guide/functional_system` - Learn the functional interface
- :doc:`user_guide/statistical_analysis` - Explore statistical templates
- :doc:`examples/demographics` - See detailed examples

