Functional Reporting System
============================

The functional reporting system in py4csr provides a modern, Pythonic interface for creating clinical study reports using method chaining and functional composition.

Overview
--------

The functional system is built around the **ReportBuilder** class, which allows you to:

- Chain methods together for readable, declarative code
- Build complex reports from simple, composable components
- Leverage immutable data structures for reproducibility
- Generate multiple tables with consistent configuration

Key Advantages
--------------

**Method Chaining**
~~~~~~~~~~~~~~~~~~~

Build reports through elegant function composition:

.. code-block:: python

   result = (ReportBuilder(config)
       .init_study(uri="STUDY001")
       .add_dataset("adsl", adsl)
       .define_treatments(var="TRT01P")
       .add_demographics_table()
       .generate_all()
       .finalize()
   )

**Immutable Transformations**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each method returns a new builder instance, ensuring data integrity:

.. code-block:: python

   # Original builder unchanged
   builder1 = ReportBuilder(config).init_study("STUDY001")
   
   # New builder with additional configuration
   builder2 = builder1.add_dataset("adsl", adsl)
   
   # builder1 still only has study initialization

**Reusable Components**
~~~~~~~~~~~~~~~~~~~~~~~

Create reusable report templates:

.. code-block:: python

   def create_safety_report(builder, adsl, adae):
       return (builder
           .add_dataset("adsl", adsl)
           .add_dataset("adae", adae)
           .define_populations(safety="SAFFL=='Y'")
           .add_demographics_table(population="safety")
           .add_ae_summary_table(population="safety")
           .add_ae_detail_table(population="safety")
       )

Getting Started
---------------

Basic Workflow
~~~~~~~~~~~~~~

1. **Create Configuration**

.. code-block:: python

   from py4csr.config import ReportConfig
   from py4csr.reporting import ReportBuilder

   config = ReportConfig()

2. **Initialize Study**

.. code-block:: python

   builder = ReportBuilder(config)
   builder = builder.init_study(
       uri="STUDY001",
       title="Phase III Clinical Study Report",
       protocol="PROTO-001"
   )

3. **Add Datasets**

.. code-block:: python

   import pandas as pd

   adsl = pd.read_csv("data/adsl.csv")
   adae = pd.read_csv("data/adae.csv")
   adlb = pd.read_csv("data/adlb.csv")

   builder = (builder
       .add_dataset("adsl", adsl)
       .add_dataset("adae", adae)
       .add_dataset("adlb", adlb)
   )

4. **Define Populations**

.. code-block:: python

   builder = builder.define_populations(
       safety="SAFFL=='Y'",
       efficacy="EFFFL=='Y'",
       itt="ITTFL=='Y'",
       pp="PPFL=='Y'"
   )

5. **Define Treatments**

.. code-block:: python

   builder = builder.define_treatments(
       var="TRT01P",
       order=["Placebo", "Drug 10mg", "Drug 20mg"]
   )

6. **Add Tables**

.. code-block:: python

   builder = (builder
       .add_demographics_table(
           title="Table 14.1.1 Demographics",
           population="safety"
       )
       .add_ae_summary_table(
           title="Table 14.3.1 Adverse Events Summary",
           population="safety"
       )
   )

7. **Generate and Save**

.. code-block:: python

   result = builder.generate_all(output_dir="reports")
   result = result.finalize()

   print(f"Generated {len(result.generated_files)} files")

Complete Example
~~~~~~~~~~~~~~~~

.. code-block:: python

   from py4csr.config import ReportConfig
   from py4csr.reporting import ReportBuilder
   import pandas as pd

   # Load data
   adsl = pd.read_csv("data/adsl.csv")
   adae = pd.read_csv("data/adae.csv")

   # Create report
   config = ReportConfig()
   result = (ReportBuilder(config)
       .init_study(
           uri="STUDY001",
           title="Phase III Clinical Study Report"
       )
       .add_dataset("adsl", adsl)
       .add_dataset("adae", adae)
       .define_populations(
           safety="SAFFL=='Y'",
           efficacy="EFFFL=='Y'"
       )
       .define_treatments(var="TRT01P")
       .add_demographics_table(
           title="Demographics and Baseline Characteristics",
           population="safety"
       )
       .add_ae_summary_table(
           title="Adverse Events Summary",
           population="safety"
       )
       .generate_all(output_dir="reports")
       .finalize()
   )

   print(f"✅ Generated {len(result.generated_files)} report files")

Advanced Features
-----------------

Custom Table Specifications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create custom tables with specific variables and statistics:

.. code-block:: python

   from py4csr.reporting import TableSpecification

   custom_spec = TableSpecification(
       title="Custom Vital Signs Analysis",
       dataset="advs",
       population="safety",
       variables=[
           {"name": "SYSBP", "label": "Systolic BP (mmHg)", "type": "continuous"},
           {"name": "DIABP", "label": "Diastolic BP (mmHg)", "type": "continuous"},
           {"name": "PULSE", "label": "Pulse (bpm)", "type": "continuous"}
       ],
       statistics=["n", "mean", "sd", "median", "min", "max"],
       by_visit=True
   )

   builder = builder.add_custom_table(custom_spec)

Conditional Logic
~~~~~~~~~~~~~~~~~

Add tables conditionally based on data:

.. code-block:: python

   builder = ReportBuilder(config).init_study("STUDY001")
   
   # Add demographics (always)
   builder = builder.add_demographics_table()
   
   # Add AE tables only if AE data exists
   if not adae.empty:
       builder = (builder
           .add_ae_summary_table()
           .add_ae_detail_table()
       )
   
   # Add efficacy tables only if efficacy population exists
   if (adsl['EFFFL'] == 'Y').any():
       builder = builder.add_efficacy_table()

Multiple Output Formats
~~~~~~~~~~~~~~~~~~~~~~~~

Generate reports in multiple formats:

.. code-block:: python

   # Generate RTF for regulatory submission
   result_rtf = builder.generate_all(
       output_dir="reports/rtf",
       format="rtf"
   )

   # Generate HTML for internal review
   result_html = builder.generate_all(
       output_dir="reports/html",
       format="html"
   )

   # Generate CSV for data review
   result_csv = builder.generate_all(
       output_dir="reports/csv",
       format="csv"
   )

Statistical Templates
~~~~~~~~~~~~~~~~~~~~~

Use pre-configured statistical templates:

.. code-block:: python

   from py4csr.functional import FunctionalConfig

   # Get standard clinical configuration
   config = FunctionalConfig.clinical_standard()

   # Access available statistics
   print(config.statistics.keys())
   # ['n', 'mean', 'sd', 'median', 'q1', 'q3', 'min', 'max', ...]

   # Use in table specification
   builder = builder.add_demographics_table(
       statistics=["n", "mean_sd", "median", "q1q3", "min_max"]
   )

Best Practices
--------------

1. **Use Method Chaining**

.. code-block:: python

   # Good - readable and concise
   result = (builder
       .init_study("STUDY001")
       .add_dataset("adsl", adsl)
       .add_demographics_table()
       .generate_all()
   )

   # Avoid - verbose and harder to read
   builder = builder.init_study("STUDY001")
   builder = builder.add_dataset("adsl", adsl)
   builder = builder.add_demographics_table()
   result = builder.generate_all()

2. **Validate Data Early**

.. code-block:: python

   from py4csr.data import validate_adam_dataset

   # Validate before adding to builder
   is_valid, errors = validate_adam_dataset(adsl, "ADSL")
   if not is_valid:
       raise ValueError(f"Invalid ADSL: {errors}")

   builder = builder.add_dataset("adsl", adsl)

3. **Use Descriptive Titles**

.. code-block:: python

   # Good - clear and regulatory-compliant
   builder = builder.add_demographics_table(
       title="Table 14.1.1 Demographics and Baseline Characteristics - Safety Population"
   )

   # Avoid - vague
   builder = builder.add_demographics_table(title="Demographics")

4. **Organize by Population**

.. code-block:: python

   # Safety tables
   safety_builder = (builder
       .add_demographics_table(population="safety")
       .add_ae_summary_table(population="safety")
   )

   # Efficacy tables
   efficacy_builder = (safety_builder
       .add_efficacy_table(population="efficacy")
       .add_response_table(population="efficacy")
   )

Next Steps
----------

- :doc:`clinical_data` - Learn about CDISC dataset handling
- :doc:`statistical_analysis` - Explore statistical templates
- :doc:`output_generation` - Master output formats
- :doc:`../examples/demographics` - See complete examples

