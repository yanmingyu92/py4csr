Adverse Events Examples
========================

Complete examples for creating adverse events (AE) summary and detail tables.

AE Summary Table
----------------

Basic AE Summary
~~~~~~~~~~~~~~~~

.. code-block:: python

   from py4csr.clinical import ClinicalSession
   import pandas as pd

   # Load data
   adsl = pd.read_csv("data/adsl.csv")
   adae = pd.read_csv("data/adae.csv")

   # Merge for treatment information
   adae_merged = adae.merge(
       adsl[['USUBJID', 'TRT01P', 'TRT01PN', 'SAFFL']],
       on='USUBJID'
   )

   # Filter to safety population
   adae_safety = adae_merged[adae_merged['SAFFL'] == 'Y']

   # Create AE summary
   session = ClinicalSession(uri="STUDY001_AE")
   session.define_report(
       dataset=adae_safety,
       subjid="USUBJID",
       title="Table 14.3.1 Adverse Events Summary - Safety Population"
   )

   session.add_trt(name="TRT01PN", decode="TRT01P", across="Y")

   # Overall AE summary
   session.add_cond(
       label="Any adverse event",
       condition="AEDECOD != ''",
       stats="npct"
   )

   session.add_cond(
       label="Any serious adverse event",
       condition="AESER == 'Y'",
       stats="npct"
   )

   session.add_cond(
       label="Any adverse event leading to discontinuation",
       condition="AEACN == 'DRUG WITHDRAWN'",
       stats="npct"
   )

   session.add_cond(
       label="Any adverse event leading to death",
       condition="AEOUT == 'FATAL'",
       stats="npct"
   )

   session.generate()
   session.finalize(output_path="reports/ae_summary.rtf", format="rtf")

AE by System Organ Class
-------------------------

SOC and Preferred Term
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from py4csr.clinical import ClinicalSession

   session = ClinicalSession(uri="STUDY001_AE_SOC")
   session.define_report(
       dataset=adae_safety,
       subjid="USUBJID",
       title="Table 14.3.2 Adverse Events by System Organ Class and Preferred Term"
   )

   session.add_trt(name="TRT01PN", decode="TRT01P", across="Y")

   # Add SOC with nested PT
   session.add_catvar(
       name="AEBODSYS",
       label="System Organ Class",
       stats="npct",
       nested_var="AEDECOD",
       nested_label="  Preferred Term"
   )

   session.generate()
   session.finalize(output_path="reports/ae_by_soc.rtf", format="rtf")

AE by Severity
--------------

Severity Analysis
~~~~~~~~~~~~~~~~~

.. code-block:: python

   session = ClinicalSession(uri="STUDY001_AE_SEV")
   session.define_report(
       dataset=adae_safety,
       subjid="USUBJID",
       title="Table 14.3.3 Adverse Events by Maximum Severity"
   )

   session.add_trt(name="TRT01PN", decode="TRT01P", across="Y")

   # AE by severity
   session.add_catvar(
       name="AESEV",
       label="Maximum Severity, n (%)",
       stats="npct",
       codelist="MILD='Mild',MODERATE='Moderate',SEVERE='Severe'"
   )

   session.generate()
   session.finalize(output_path="reports/ae_by_severity.rtf", format="rtf")

AE by Relationship
------------------

Causality Analysis
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   session = ClinicalSession(uri="STUDY001_AE_REL")
   session.define_report(
       dataset=adae_safety,
       subjid="USUBJID",
       title="Table 14.3.4 Treatment-Related Adverse Events"
   )

   session.add_trt(name="TRT01PN", decode="TRT01P", across="Y")

   # Filter to treatment-related AEs
   adae_related = adae_safety[adae_safety['AEREL'].isin(['RELATED', 'PROBABLY RELATED', 'POSSIBLY RELATED'])]

   session.define_report(dataset=adae_related, subjid="USUBJID")

   # Add SOC and PT for related AEs
   session.add_catvar(
       name="AEBODSYS",
       label="System Organ Class",
       stats="npct",
       nested_var="AEDECOD",
       nested_label="  Preferred Term"
   )

   session.generate()
   session.finalize(output_path="reports/ae_related.rtf", format="rtf")

Using Functional Interface
---------------------------

Complete AE Report
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from py4csr.reporting import ReportBuilder
   from py4csr.config import ReportConfig

   config = ReportConfig(study_id="STUDY001")

   result = (ReportBuilder(config)
       .init_study(uri="STUDY001")
       .add_dataset("adsl", adsl)
       .add_dataset("adae", adae)
       .define_populations(safety="SAFFL=='Y'")
       .define_treatments(var="TRT01P")
       .add_ae_summary_table(
           title="Adverse Events Summary",
           population="safety"
       )
       .add_ae_detail_table(
           title="Adverse Events by SOC and PT",
           population="safety"
       )
       .generate_all(output_dir="reports")
       .finalize()
   )

Next Steps
----------

- :doc:`efficacy` - Efficacy analysis examples
- :doc:`../user_guide/statistical_analysis` - Statistical methods

