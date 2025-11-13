Quick Start Guide
=================

This guide will help you create your first clinical report with py4csr in just a few minutes.

Installation
------------

First, install py4csr using pip:

.. code-block:: bash

   pip install py4csr

For PDF output support, install with the pdf extra:

.. code-block:: bash

   pip install py4csr[pdf]

Your First Report
-----------------

Let's create a simple demographics table using the clinical session interface.

Step 1: Import and Load Data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from py4csr.clinical import ClinicalSession
   import pandas as pd

   # Load your ADSL dataset
   adsl = pd.read_csv("data/adsl.csv")

Step 2: Create a Clinical Session
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Create a new clinical session
   session = ClinicalSession(uri="STUDY001")

Step 3: Define the Report
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Define the report structure
   session.define_report(
       dataset=adsl,
       subjid="USUBJID",
       title="Table 14.1.1 Demographics and Baseline Characteristics",
       footnote="Source: ADSL dataset"
   )

Step 4: Add Treatment Groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Define treatment groups
   session.add_trt(
       name="TRT01PN",      # Treatment variable (numeric)
       decode="TRT01P",     # Treatment labels
       across="Y",          # Display treatments across columns
       totaltext="All Subjects"  # Label for total column
   )

Step 5: Add Variables
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Add continuous variable (Age)
   session.add_var(
       name="AGE",
       label="Age (years)",
       stats="n mean+sd median q1q3 min+max"
   )

   # Add categorical variable (Sex)
   session.add_catvar(
       name="SEX",
       label="Sex, n (%)",
       stats="npct",
       codelist="M='Male',F='Female'"
   )

   # Add another categorical variable (Race)
   session.add_catvar(
       name="RACE",
       label="Race, n (%)",
       stats="npct"
   )

Step 6: Generate and Save
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Generate the table
   session.generate()

   # Save to RTF format
   session.finalize(output_path="demographics.rtf", format="rtf")

   # Or save to CSV
   session.to_csv("demographics.csv")

Complete Example
----------------

Here's the complete code in one block:

.. code-block:: python

   from py4csr.clinical import ClinicalSession
   import pandas as pd

   # Load data
   adsl = pd.read_csv("data/adsl.csv")

   # Create session and define report
   session = ClinicalSession(uri="STUDY001")
   session.define_report(
       dataset=adsl,
       subjid="USUBJID",
       title="Table 14.1.1 Demographics and Baseline Characteristics",
       footnote="Source: ADSL dataset"
   )

   # Add treatment groups
   session.add_trt(
       name="TRT01PN",
       decode="TRT01P",
       across="Y",
       totaltext="All Subjects"
   )

   # Add variables
   session.add_var(
       name="AGE",
       label="Age (years)",
       stats="n mean+sd median q1q3 min+max"
   )

   session.add_catvar(
       name="SEX",
       label="Sex, n (%)",
       stats="npct",
       codelist="M='Male',F='Female'"
   )

   session.add_catvar(
       name="RACE",
       label="Race, n (%)",
       stats="npct"
   )

   # Generate and save
   session.generate()
   session.finalize(output_path="demographics.rtf", format="rtf")

   print("Demographics table created successfully!")

Using the Functional Interface
-------------------------------

py4csr also provides a functional programming interface with method chaining:

.. code-block:: python

   from py4csr.reporting import ReportBuilder
   from py4csr.config import ReportConfig
   import pandas as pd

   # Load data
   adsl = pd.read_csv("data/adsl.csv")

   # Create report using method chaining
   config = ReportConfig()
   builder = ReportBuilder(config)

   result = (builder
       .init_study(
           uri="STUDY001",
           title="Phase III Clinical Study Report",
           protocol="ABC-123-2024"
       )
       .add_dataset("adsl", adsl)
       .define_populations(safety="SAFFL=='Y'")
       .define_treatments(var="TRT01P")
       .add_demographics_table(
           title="Demographics and Baseline Characteristics",
           population="safety"
       )
       .generate_all(output_dir="reports")
       .finalize()
   )

   print(f"Generated {len(result.generated_files)} files")

Next Steps
----------

Now that you've created your first report, explore:

- :doc:`concepts` - Learn about py4csr's core concepts
- :doc:`user_guide/functional_system` - Deep dive into the functional reporting system
- :doc:`user_guide/statistical_analysis` - Learn about statistical templates
- :doc:`examples/demographics` - More detailed demographics examples
- :doc:`examples/adverse_events` - Safety reporting examples

Common Statistics
-----------------

Here are some commonly used statistics strings:

**Continuous Variables:**

- ``"n mean+sd"`` - Count, mean, and standard deviation
- ``"n mean+sd median q1q3 min+max"`` - Full summary statistics
- ``"n median q1q3"`` - Count, median, and quartiles

**Categorical Variables:**

- ``"npct"`` - Count and percentage
- ``"n"`` - Count only
- ``"pct"`` - Percentage only

**Condition-based:**

- ``"count"`` - Count of events/subjects meeting condition
- ``"npct"`` - Count and percentage meeting condition

Tips and Best Practices
------------------------

1. **Always validate your data** before creating reports
2. **Use meaningful labels** for better readability
3. **Follow CDISC standards** for variable names
4. **Test with small datasets** first
5. **Check output formats** match regulatory requirements
6. **Use version control** for your reporting scripts

Troubleshooting
---------------

**Issue: "Column not found" error**

Make sure the variable names in your code match the column names in your dataset exactly (case-sensitive).

**Issue: RTF output looks incorrect**

Check that your data doesn't contain special characters that need escaping. Use the ``to_csv()`` method first to verify the data.

**Issue: Statistics not calculating**

Ensure your data types are correct (numeric for continuous variables, categorical for categorical variables).

For more help, see the :doc:`development/contributing` page or open an issue on GitHub.

