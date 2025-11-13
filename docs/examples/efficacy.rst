Efficacy Analysis Examples
===========================

Complete examples for creating efficacy analysis tables.

Primary Endpoint Analysis
--------------------------

Continuous Endpoint
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from py4csr.clinical import ClinicalSession
   import pandas as pd

   # Load data
   adsl = pd.read_csv("data/adsl.csv")
   adeff = pd.read_csv("data/adeff.csv")

   # Merge datasets
   adeff_merged = adeff.merge(
       adsl[['USUBJID', 'TRT01P', 'TRT01PN', 'EFFFL']],
       on='USUBJID'
   )

   # Filter to efficacy population
   adeff_eff = adeff_merged[adeff_merged['EFFFL'] == 'Y']

   # Create efficacy table
   session = ClinicalSession(uri="STUDY001_EFF")
   session.define_report(
       dataset=adeff_eff,
       subjid="USUBJID",
       title="Table 14.2.1 Primary Efficacy Endpoint - Change from Baseline"
   )

   session.add_trt(name="TRT01PN", decode="TRT01P", across="Y")

   # Change from baseline
   session.add_var(
       name="CHG",
       label="Change from Baseline",
       stats="n mean+sd median q1q3 min+max"
   )

   session.generate()
   session.finalize(output_path="reports/efficacy_primary.rtf", format="rtf")

Binary Endpoint
~~~~~~~~~~~~~~~

.. code-block:: python

   # Response rate analysis
   session = ClinicalSession(uri="STUDY001_RESP")
   session.define_report(
       dataset=adeff_eff,
       subjid="USUBJID",
       title="Table 14.2.2 Response Rate - Efficacy Population"
   )

   session.add_trt(name="TRT01PN", decode="TRT01P", across="Y")

   # Response categories
   session.add_catvar(
       name="AVALC",
       label="Best Overall Response, n (%)",
       stats="npct",
       codelist="CR='Complete Response',PR='Partial Response',SD='Stable Disease',PD='Progressive Disease'"
   )

   # Overall response rate (CR + PR)
   session.add_cond(
       label="Overall Response Rate (CR + PR), n (%)",
       condition="AVALC in ['CR', 'PR']",
       stats="npct"
   )

   session.generate()
   session.finalize(output_path="reports/efficacy_response.rtf", format="rtf")

Secondary Endpoints
-------------------

Multiple Endpoints
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   session = ClinicalSession(uri="STUDY001_SEC")
   session.define_report(
       dataset=adeff_eff,
       subjid="USUBJID",
       title="Table 14.2.3 Secondary Efficacy Endpoints"
   )

   session.add_trt(name="TRT01PN", decode="TRT01P", across="Y")

   # Endpoint 1: Change in symptom score
   session.add_var(
       name="CHG_SYMPTOM",
       label="Change in Symptom Score",
       stats="n mean+sd median"
   )

   # Endpoint 2: Change in quality of life
   session.add_var(
       name="CHG_QOL",
       label="Change in Quality of Life Score",
       stats="n mean+sd median"
   )

   # Endpoint 3: Time to response
   session.add_var(
       name="TTR",
       label="Time to Response (days)",
       stats="n mean+sd median min+max"
   )

   session.generate()
   session.finalize(output_path="reports/efficacy_secondary.rtf", format="rtf")

By Visit Analysis
-----------------

Longitudinal Analysis
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Analyze by visit
   for visit in ['Week 4', 'Week 8', 'Week 12', 'Week 24']:
       visit_data = adeff_eff[adeff_eff['AVISIT'] == visit]
       
       session = ClinicalSession(uri=f"STUDY001_EFF_{visit.replace(' ', '_')}")
       session.define_report(
           dataset=visit_data,
           subjid="USUBJID",
           title=f"Efficacy Analysis - {visit}"
       )
       
       session.add_trt(name="TRT01PN", decode="TRT01P", across="Y")
       session.add_var(name="CHG", label="Change from Baseline", stats="n mean+sd")
       session.generate()
       session.finalize(output_path=f"reports/efficacy_{visit.lower().replace(' ', '_')}.rtf")

Using Functional Interface
---------------------------

Complete Efficacy Report
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from py4csr.reporting import ReportBuilder
   from py4csr.config import ReportConfig

   config = ReportConfig(study_id="STUDY001")

   result = (ReportBuilder(config)
       .init_study(uri="STUDY001")
       .add_dataset("adsl", adsl)
       .add_dataset("adeff", adeff)
       .define_populations(efficacy="EFFFL=='Y'")
       .define_treatments(var="TRT01P")
       .add_efficacy_table(
           title="Primary Efficacy Endpoint",
           population="efficacy"
       )
       .add_response_table(
           title="Response Rate Analysis",
           population="efficacy"
       )
       .generate_all(output_dir="reports")
       .finalize()
   )

Next Steps
----------

- :doc:`../user_guide/statistical_analysis` - Statistical methods
- :doc:`../advanced/plotting` - Efficacy visualizations

