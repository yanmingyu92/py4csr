Demographics Table Examples
============================

This page provides complete examples for creating demographics and baseline characteristics tables.

Basic Demographics Table
-------------------------

Simple Example
~~~~~~~~~~~~~~

.. code-block:: python

   from py4csr.clinical import ClinicalSession
   import pandas as pd

   # Load data
   adsl = pd.read_csv("data/adsl.csv")

   # Create session
   session = ClinicalSession(uri="STUDY001")
   session.define_report(
       dataset=adsl,
       subjid="USUBJID",
       title="Table 14.1.1 Demographics and Baseline Characteristics"
   )

   # Add treatment groups
   session.add_trt(name="TRT01PN", decode="TRT01P", across="Y")

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

   session.add_catvar(
       name="RACE",
       label="Race, n (%)",
       stats="npct"
   )

   # Generate and save
   session.generate()
   session.finalize(output_path="reports/demographics.rtf", format="rtf")

Expected Output
~~~~~~~~~~~~~~~

.. code-block:: text

   Table 14.1.1 Demographics and Baseline Characteristics

                                    Placebo      Drug 10mg    Drug 20mg    Total
                                    (N=50)       (N=50)       (N=50)       (N=150)
   ─────────────────────────────────────────────────────────────────────────────
   Age (years)
     n                             50           50           50           150
     Mean (SD)                     45.3 (12.1)  46.2 (11.8)  44.8 (12.5)  45.4 (12.1)
     Median                        44.0         45.5         43.0         44.0
     Q1, Q3                        36.0, 54.0   37.0, 55.0   35.0, 53.0   36.0, 54.0
     Min, Max                      22, 68       23, 70       21, 69       21, 70

   Sex, n (%)
     Male                          28 (56.0)    26 (52.0)    29 (58.0)    83 (55.3)
     Female                        22 (44.0)    24 (48.0)    21 (42.0)    67 (44.7)

   Race, n (%)
     White                         35 (70.0)    34 (68.0)    36 (72.0)    105 (70.0)
     Black or African American     10 (20.0)    11 (22.0)    9 (18.0)     30 (20.0)
     Asian                         5 (10.0)     5 (10.0)     5 (10.0)     15 (10.0)

Complete Demographics Table
---------------------------

With All Standard Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from py4csr.clinical import ClinicalSession
   import pandas as pd

   adsl = pd.read_csv("data/adsl.csv")

   session = ClinicalSession(uri="STUDY001")
   session.define_report(
       dataset=adsl,
       subjid="USUBJID",
       title="Table 14.1.1 Demographics and Baseline Characteristics - Safety Population"
   )

   session.add_trt(name="TRT01PN", decode="TRT01P", across="Y")

   # Age
   session.add_var(name="AGE", label="Age (years)", stats="n mean+sd median q1q3 min+max")
   session.add_catvar(
       name="AGEGR1",
       label="Age Group, n (%)",
       stats="npct",
       codelist="<18='<18 years',18-65='18-65 years',>65='>65 years'"
   )

   # Sex
   session.add_catvar(
       name="SEX",
       label="Sex, n (%)",
       stats="npct",
       codelist="M='Male',F='Female'"
   )

   # Race
   session.add_catvar(name="RACE", label="Race, n (%)", stats="npct")

   # Ethnicity
   session.add_catvar(
       name="ETHNIC",
       label="Ethnicity, n (%)",
       stats="npct",
       codelist="HISPANIC OR LATINO='Hispanic or Latino',NOT HISPANIC OR LATINO='Not Hispanic or Latino'"
   )

   # Weight
   session.add_var(name="WEIGHT", label="Weight (kg)", stats="n mean+sd median min+max")

   # Height
   session.add_var(name="HEIGHT", label="Height (cm)", stats="n mean+sd median min+max")

   # BMI
   session.add_var(name="BMI", label="BMI (kg/m²)", stats="n mean+sd median min+max")
   session.add_catvar(
       name="BMICAT",
       label="BMI Category, n (%)",
       stats="npct",
       codelist="<18.5='Underweight',18.5-25='Normal',25-30='Overweight',>=30='Obese'"
   )

   session.generate()
   session.finalize(output_path="reports/demographics_complete.rtf", format="rtf")

Using Functional Interface
---------------------------

ReportBuilder Example
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from py4csr.reporting import ReportBuilder
   from py4csr.config import ReportConfig
   import pandas as pd

   # Load data
   adsl = pd.read_csv("data/adsl.csv")

   # Create configuration
   config = ReportConfig(
       study_id="STUDY001",
       output_dir="reports",
       page_orientation="landscape"
   )

   # Build report
   result = (ReportBuilder(config)
       .init_study(
           uri="STUDY001",
           title="Phase III Clinical Study Report"
       )
       .add_dataset("adsl", adsl)
       .define_populations(safety="SAFFL=='Y'")
       .define_treatments(var="TRT01P")
       .add_demographics_table(
           title="Table 14.1.1 Demographics and Baseline Characteristics",
           population="safety"
       )
       .generate_all(output_dir="reports")
       .finalize()
   )

   print(f"✅ Generated {len(result.generated_files)} files")

Advanced Examples
-----------------

By Subgroup
~~~~~~~~~~~

.. code-block:: python

   # Demographics by sex subgroup
   for sex in ['M', 'F']:
       subset = adsl[adsl['SEX'] == sex]
       
       session = ClinicalSession(uri=f"STUDY001_SEX_{sex}")
       session.define_report(
           dataset=subset,
           subjid="USUBJID",
           title=f"Demographics - {sex} Subgroup"
       )
       session.add_trt(name="TRT01PN", decode="TRT01P")
       session.add_var(name="AGE", stats="n mean+sd median")
       session.generate()
       session.finalize(output_path=f"reports/demographics_sex_{sex}.rtf")

Multiple Populations
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Safety population
   adsl_safety = adsl[adsl['SAFFL'] == 'Y']
   session_safety = ClinicalSession(uri="STUDY001_SAFETY")
   session_safety.define_report(
       dataset=adsl_safety,
       subjid="USUBJID",
       title="Demographics - Safety Population"
   )
   # ... add variables ...
   session_safety.generate()
   session_safety.finalize(output_path="reports/demographics_safety.rtf")

   # Efficacy population
   adsl_efficacy = adsl[adsl['EFFFL'] == 'Y']
   session_efficacy = ClinicalSession(uri="STUDY001_EFFICACY")
   session_efficacy.define_report(
       dataset=adsl_efficacy,
       subjid="USUBJID",
       title="Demographics - Efficacy Population"
   )
   # ... add variables ...
   session_efficacy.generate()
   session_efficacy.finalize(output_path="reports/demographics_efficacy.rtf")

With Statistical Tests
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from py4csr.clinical import ClinicalSession, ClinicalStatisticalEngine

   session = ClinicalSession(uri="STUDY001")
   session.define_report(dataset=adsl, subjid="USUBJID")
   session.add_trt(name="TRT01PN", decode="TRT01P")
   session.add_var(name="AGE", stats="n mean+sd median")
   session.generate()

   # Perform ANOVA for age
   engine = ClinicalStatisticalEngine()
   anova_result = engine.perform_anova(
       data=adsl,
       variable="AGE",
       treatment="TRT01PN"
   )

   print(f"ANOVA p-value: {anova_result['p_value']:.4f}")

   # Add footnote with p-value
   session.add_footnote(f"ANOVA p-value for Age: {anova_result['p_value']:.4f}")
   session.finalize(output_path="reports/demographics_with_tests.rtf")

Next Steps
----------

- :doc:`adverse_events` - Adverse events examples
- :doc:`efficacy` - Efficacy analysis examples
- :doc:`../user_guide/statistical_analysis` - Statistical methods

