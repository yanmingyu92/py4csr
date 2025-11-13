Reporting Module
================

The reporting module provides classes for building and generating clinical study reports.

ReportBuilder
-------------

.. autoclass:: py4csr.reporting.report_builder.ReportBuilder
   :members:
   :undoc-members:
   :show-inheritance:

TableSpecification
------------------

.. autoclass:: py4csr.reporting.table_specification.TableSpecification
   :members:
   :undoc-members:
   :show-inheritance:

TableResult
-----------

.. autoclass:: py4csr.reporting.table_result.TableResult
   :members:
   :undoc-members:
   :show-inheritance:

Example Usage
-------------

.. code-block:: python

   from py4csr.reporting import ReportBuilder
   from py4csr.config import ReportConfig
   import pandas as pd

   # Create configuration
   config = ReportConfig()
   
   # Create report builder
   builder = ReportBuilder(config)
   
   # Initialize study
   builder.init_study(
       uri="STUDY001",
       title="Phase III Clinical Study Report",
       protocol="ABC-123-2024"
   )
   
   # Add datasets
   adsl = pd.read_csv("data/adsl.csv")
   builder.add_dataset("adsl", adsl)
   
   # Define populations
   builder.define_populations(
       safety="SAFFL=='Y'",
       efficacy="EFFFL=='Y'"
   )
   
   # Define treatments
   builder.define_treatments(var="TRT01P")
   
   # Add demographics table
   builder.add_demographics_table(
       title="Demographics and Baseline Characteristics",
       population="safety"
   )
   
   # Generate all tables
   builder.generate_all(output_dir="reports")
   
   # Finalize
   builder.finalize()

