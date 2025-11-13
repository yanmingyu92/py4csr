Working with Clinical Data
===========================

py4csr is designed to work with **CDISC ADaM datasets** (Analysis Data Model), the industry standard for clinical trial analysis datasets.

CDISC ADaM Overview
-------------------

What is ADaM?
~~~~~~~~~~~~~

**ADaM** (Analysis Data Model) is a CDISC standard that defines:

- Structure and content of analysis datasets
- Variable naming conventions
- Metadata requirements
- Traceability to source data (SDTM)

py4csr supports all major ADaM dataset types:

- **ADSL**: Subject-Level Analysis Dataset
- **ADAE**: Adverse Events Analysis Dataset
- **ADLB**: Laboratory Analysis Dataset
- **ADVS**: Vital Signs Analysis Dataset
- **ADEFF**: Efficacy Analysis Dataset
- **ADTTE**: Time-to-Event Analysis Dataset

Required Variables
~~~~~~~~~~~~~~~~~~

Each ADaM dataset must contain certain key variables:

**ADSL (Subject-Level)**:

.. code-block:: python

   # Required variables
   - USUBJID: Unique Subject Identifier
   - STUDYID: Study Identifier
   - SUBJID: Subject Identifier for the Study
   - TRT01P: Planned Treatment (character)
   - TRT01PN: Planned Treatment (numeric)
   - SAFFL: Safety Population Flag
   - EFFFL: Efficacy Population Flag
   - ITTFL: Intent-to-Treat Population Flag

**ADAE (Adverse Events)**:

.. code-block:: python

   # Required variables
   - USUBJID: Unique Subject Identifier
   - AEDECOD: Adverse Event Preferred Term
   - AEBODSYS: Body System or Organ Class
   - AESEV: Severity/Intensity
   - AESER: Serious Event Flag
   - AEREL: Causality

Loading Data
------------

From CSV Files
~~~~~~~~~~~~~~

.. code-block:: python

   import pandas as pd

   # Load ADSL
   adsl = pd.read_csv("data/adsl.csv")

   # Load ADAE
   adae = pd.read_csv("data/adae.csv")

   # Load ADLB
   adlb = pd.read_csv("data/adlb.csv")

From SAS Datasets
~~~~~~~~~~~~~~~~~

.. code-block:: python

   import pandas as pd

   # Using pandas (requires SAS7BDAT library)
   adsl = pd.read_sas("data/adsl.sas7bdat")

   # Using pyreadstat (recommended)
   import pyreadstat
   adsl, meta = pyreadstat.read_sas7bdat("data/adsl.sas7bdat")

From Excel Files
~~~~~~~~~~~~~~~~

.. code-block:: python

   import pandas as pd

   # Single sheet
   adsl = pd.read_excel("data/adam_datasets.xlsx", sheet_name="ADSL")

   # Multiple sheets
   with pd.ExcelFile("data/adam_datasets.xlsx") as xls:
       adsl = pd.read_excel(xls, "ADSL")
       adae = pd.read_excel(xls, "ADAE")
       adlb = pd.read_excel(xls, "ADLB")

Data Validation
---------------

Validating ADaM Datasets
~~~~~~~~~~~~~~~~~~~~~~~~~

py4csr includes built-in validation for ADaM datasets:

.. code-block:: python

   from py4csr.data import validate_adam_dataset

   # Validate ADSL
   is_valid, errors = validate_adam_dataset(adsl, dataset_type="ADSL")

   if not is_valid:
       print("Validation errors found:")
       for error in errors:
           print(f"  - {error}")
   else:
       print("✅ ADSL is valid")

Common Validation Checks
~~~~~~~~~~~~~~~~~~~~~~~~

The validator checks for:

1. **Required Variables**: Ensures all required variables are present
2. **Data Types**: Validates variable types (numeric, character, date)
3. **Value Ranges**: Checks for valid values in flag variables
4. **Missing Data**: Identifies critical missing values
5. **Duplicates**: Detects duplicate subject IDs
6. **Consistency**: Validates cross-variable consistency

Example Validation:

.. code-block:: python

   from py4csr.data import validate_adam_dataset

   # Comprehensive validation
   is_valid, errors = validate_adam_dataset(
       adsl,
       dataset_type="ADSL",
       check_required_vars=True,
       check_data_types=True,
       check_duplicates=True
   )

   # Print detailed report
   if errors:
       print(f"Found {len(errors)} validation errors:")
       for i, error in enumerate(errors, 1):
           print(f"{i}. {error}")

Data Preprocessing
------------------

Filtering Populations
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Safety population
   adsl_safety = adsl[adsl['SAFFL'] == 'Y'].copy()

   # Efficacy population
   adsl_efficacy = adsl[adsl['EFFFL'] == 'Y'].copy()

   # Multiple conditions
   adsl_subset = adsl[
       (adsl['SAFFL'] == 'Y') &
       (adsl['AGE'] >= 18) &
       (adsl['SEX'] == 'F')
   ].copy()

Merging Datasets
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Merge ADAE with ADSL for treatment information
   adae_merged = adae.merge(
       adsl[['USUBJID', 'TRT01P', 'TRT01PN', 'SAFFL']],
       on='USUBJID',
       how='left'
   )

   # Merge ADLB with ADSL
   adlb_merged = adlb.merge(
       adsl[['USUBJID', 'TRT01P', 'SAFFL']],
       on='USUBJID',
       how='left'
   )

Handling Missing Data
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Check for missing values
   missing_summary = adsl.isnull().sum()
   print(missing_summary[missing_summary > 0])

   # Fill missing values
   adsl['RACE'] = adsl['RACE'].fillna('NOT REPORTED')

   # Drop rows with missing critical variables
   adsl_clean = adsl.dropna(subset=['USUBJID', 'TRT01P'])

Creating Derived Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Age groups
   adsl['AGEGR1'] = pd.cut(
       adsl['AGE'],
       bins=[0, 18, 65, 120],
       labels=['<18', '18-65', '>65']
   )

   # BMI categories
   adsl['BMICAT'] = pd.cut(
       adsl['BMI'],
       bins=[0, 18.5, 25, 30, 100],
       labels=['Underweight', 'Normal', 'Overweight', 'Obese']
   )

   # Treatment duration in weeks
   adsl['TRTDUR_WK'] = adsl['TRTDUR'] / 7

Using Data in py4csr
--------------------

Clinical Session Interface
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from py4csr.clinical import ClinicalSession

   # Load and validate data
   adsl = pd.read_csv("data/adsl.csv")
   is_valid, errors = validate_adam_dataset(adsl, "ADSL")

   if not is_valid:
       raise ValueError(f"Invalid ADSL: {errors}")

   # Create session with validated data
   session = ClinicalSession(uri="STUDY001")
   session.define_report(
       dataset=adsl,
       subjid="USUBJID",
       title="Demographics Table"
   )

Functional Interface
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from py4csr.reporting import ReportBuilder
   from py4csr.config import ReportConfig

   # Load and validate data
   adsl = pd.read_csv("data/adsl.csv")
   adae = pd.read_csv("data/adae.csv")

   # Validate both datasets
   for dataset, name in [(adsl, "ADSL"), (adae, "ADAE")]:
       is_valid, errors = validate_adam_dataset(dataset, name)
       if not is_valid:
           raise ValueError(f"Invalid {name}: {errors}")

   # Create report with validated data
   config = ReportConfig()
   result = (ReportBuilder(config)
       .init_study(uri="STUDY001")
       .add_dataset("adsl", adsl)
       .add_dataset("adae", adae)
       .define_populations(safety="SAFFL=='Y'")
       .define_treatments(var="TRT01P")
       .add_demographics_table()
       .add_ae_summary_table()
       .generate_all()
   )

Best Practices
--------------

1. **Always Validate Data**

.. code-block:: python

   # Validate before using
   is_valid, errors = validate_adam_dataset(adsl, "ADSL")
   if not is_valid:
       raise ValueError(f"Data validation failed: {errors}")

2. **Use Standard Variable Names**

.. code-block:: python

   # Good - follows CDISC standards
   adsl['USUBJID']  # Unique Subject ID
   adsl['TRT01P']   # Planned Treatment

   # Avoid - non-standard names
   adsl['subject_id']
   adsl['treatment']

3. **Document Data Transformations**

.. code-block:: python

   # Document derived variables
   # AGE65FL: Age >= 65 years flag (Y/N)
   adsl['AGE65FL'] = adsl['AGE'].apply(lambda x: 'Y' if x >= 65 else 'N')

4. **Preserve Original Data**

.. code-block:: python

   # Good - work on a copy
   adsl_clean = adsl.copy()
   adsl_clean['RACE'] = adsl_clean['RACE'].fillna('NOT REPORTED')

   # Avoid - modifying original
   adsl['RACE'] = adsl['RACE'].fillna('NOT REPORTED')

5. **Check Data Quality**

.. code-block:: python

   # Check for duplicates
   duplicates = adsl[adsl.duplicated(subset=['USUBJID'])]
   if not duplicates.empty:
       print(f"Warning: {len(duplicates)} duplicate subjects found")

   # Check population flags
   safety_count = (adsl['SAFFL'] == 'Y').sum()
   print(f"Safety population: {safety_count} subjects")

Common Issues and Solutions
---------------------------

Issue: Missing Required Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Problem: SAFFL not in dataset
   # Solution: Create the flag
   adsl['SAFFL'] = 'Y'  # All subjects in safety population

Issue: Incorrect Data Types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Problem: TRT01PN is string instead of numeric
   # Solution: Convert to numeric
   adsl['TRT01PN'] = pd.to_numeric(adsl['TRT01PN'], errors='coerce')

Issue: Inconsistent Treatment Labels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Problem: Treatment labels vary
   # Solution: Standardize labels
   treatment_map = {
       'Placebo': 'Placebo',
       'PLACEBO': 'Placebo',
       'Drug 10mg': 'Drug 10 mg',
       'Drug10mg': 'Drug 10 mg'
   }
   adsl['TRT01P'] = adsl['TRT01P'].map(treatment_map)

Next Steps
----------

- :doc:`statistical_analysis` - Learn about statistical calculations
- :doc:`output_generation` - Generate reports from your data
- :doc:`../examples/demographics` - See complete data examples

