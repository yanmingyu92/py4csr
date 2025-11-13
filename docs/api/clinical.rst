Clinical Module
===============

The clinical module provides the main interface for creating clinical study reports using a session-based workflow.

ClinicalSession
---------------

.. autoclass:: py4csr.clinical.session.ClinicalSession
   :members:
   :undoc-members:
   :show-inheritance:

ClinicalStatisticalEngine
-------------------------

.. autoclass:: py4csr.clinical.statistical_engine.ClinicalStatisticalEngine
   :members:
   :undoc-members:
   :show-inheritance:

Example Usage
-------------

.. code-block:: python

   from py4csr.clinical import ClinicalSession
   import pandas as pd

   # Load your data
   adsl = pd.read_csv("data/adsl.csv")

   # Create a clinical session
   session = ClinicalSession(uri="STUDY001")
   
   # Define the report
   session.define_report(
       dataset=adsl,
       subjid="USUBJID",
       title="Table 14.1.1 Demographics and Baseline Characteristics",
       footnote="Source: ADSL"
   )
   
   # Add treatment groups
   session.add_trt(
       name="TRT01PN",
       decode="TRT01P",
       across="Y"
   )
   
   # Add demographic variables
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
   
   # Generate the table
   session.generate()
   
   # Save to RTF
   session.finalize(output_path="demographics.rtf", format="rtf")

