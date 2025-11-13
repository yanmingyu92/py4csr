Performance Optimization
=========================

Tips for optimizing py4csr performance with large datasets.

Data Optimization
-----------------

Filter Early
~~~~~~~~~~~~

.. code-block:: python

   # Good - filter before processing
   adsl_safety = adsl[adsl['SAFFL'] == 'Y']
   session.define_report(dataset=adsl_safety, subjid="USUBJID")

   # Avoid - processing all data
   session.define_report(dataset=adsl, subjid="USUBJID")

Use Appropriate Data Types
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Convert to categorical for memory efficiency
   adsl['TRT01P'] = adsl['TRT01P'].astype('category')
   adsl['SEX'] = adsl['SEX'].astype('category')

Batch Processing
----------------

Process Multiple Tables
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from py4csr.reporting import ReportBuilder

   # Generate all tables at once
   result = (ReportBuilder(config)
       .init_study(uri="STUDY001")
       .add_dataset("adsl", adsl)
       .add_demographics_table()
       .add_ae_summary_table()
       .add_efficacy_table()
       .generate_all()  # Batch generation
   )

Parallel Processing
-------------------

Use Multiple Cores
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from concurrent.futures import ProcessPoolExecutor

   def generate_table(table_spec):
       # Generate single table
       pass

   # Process tables in parallel
   with ProcessPoolExecutor(max_workers=4) as executor:
       results = executor.map(generate_table, table_specs)

Next Steps
----------

- :doc:`../user_guide/clinical_data` - Data handling
- :doc:`custom_statistics` - Custom calculations

