Configuration and Customization
================================

py4csr provides extensive configuration options to customize reports for your specific needs.

Configuration System
--------------------

py4csr uses two main configuration classes:

1. **ReportConfig**: General report settings (titles, paths, formats)
2. **FunctionalConfig**: Statistical templates and calculation settings

ReportConfig
------------

Basic Configuration
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from py4csr.config import ReportConfig

   # Create default configuration
   config = ReportConfig()

   # Customize configuration
   config = ReportConfig(
       study_id="STUDY001",
       protocol="PROTO-001",
       output_dir="reports",
       default_format="rtf",
       page_orientation="landscape"
   )

Configuration Options
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   config = ReportConfig(
       # Study information
       study_id="STUDY001",
       protocol="PROTO-001",
       sponsor="Acme Pharma",
       
       # Output settings
       output_dir="reports",
       default_format="rtf",
       
       # Page settings
       page_orientation="landscape",  # or "portrait"
       page_size="LETTER",  # or "A4", "LEGAL"
       
       # Font settings
       font_name="Times New Roman",
       font_size=9,
       
       # Margins (inches)
       margin_top=1.0,
       margin_bottom=1.0,
       margin_left=1.0,
       margin_right=1.0,
       
       # Headers and footers
       header_text="CONFIDENTIAL",
       footer_text="Page {page} of {total_pages}",
       
       # Table settings
       table_border_width=1,
       table_cell_padding=0.05,
       alternating_row_colors=True
   )

FunctionalConfig
----------------

Statistical Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from py4csr.functional import FunctionalConfig

   # Get standard clinical configuration
   config = FunctionalConfig.clinical_standard()

   # Access available statistics
   print(config.statistics.keys())
   # dict_keys(['n', 'mean', 'sd', 'median', 'q1', 'q3', 'min', 'max', ...])

Custom Statistics
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from py4csr.functional import StatisticDefinition

   # Add custom statistic
   config.statistics["cv"] = StatisticDefinition(
       name="cv",
       display_name="CV%",
       description="Coefficient of variation",
       precision=1,
       applicable_types=["continuous"]
   )

   # Define calculation function
   def calculate_cv(data):
       mean = data.mean()
       sd = data.std()
       return (sd / mean) * 100 if mean != 0 else 0

   # Register function
   config.register_statistic_function("cv", calculate_cv)

Custom Formats
~~~~~~~~~~~~~~

.. code-block:: python

   from py4csr.functional import FormatDefinition

   # Add custom format
   config.formats["pct1"] = FormatDefinition(
       name="pct1",
       display_name="Percentage (1 decimal)",
       pattern="{value:.1f}%",
       precision=1
   )

Table Templates
---------------

Creating Table Templates
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from py4csr.functional import TableTemplate

   # Define demographics template
   demographics_template = TableTemplate(
       name="demographics",
       title="Demographics and Baseline Characteristics",
       variables=[
           {"name": "AGE", "label": "Age (years)", "type": "continuous"},
           {"name": "SEX", "label": "Sex, n (%)", "type": "categorical"},
           {"name": "RACE", "label": "Race, n (%)", "type": "categorical"},
           {"name": "WEIGHT", "label": "Weight (kg)", "type": "continuous"},
           {"name": "HEIGHT", "label": "Height (cm)", "type": "continuous"}
       ],
       statistics={
           "continuous": ["n", "mean_sd", "median", "q1q3", "min_max"],
           "categorical": ["npct"]
       },
       population="safety"
   )

Using Templates
~~~~~~~~~~~~~~~

.. code-block:: python

   from py4csr.reporting import ReportBuilder

   # Apply template
   builder = (ReportBuilder(config)
       .init_study(uri="STUDY001")
       .add_dataset("adsl", adsl)
       .apply_template(demographics_template)
       .generate_all()
   )

Environment-Specific Configuration
-----------------------------------

Development vs Production
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import os

   # Development configuration
   if os.getenv("ENV") == "development":
       config = ReportConfig(
           output_dir="dev_reports",
           header_text="DRAFT - FOR REVIEW ONLY",
           watermark="DRAFT"
       )
   # Production configuration
   else:
       config = ReportConfig(
           output_dir="final_reports",
           header_text="CONFIDENTIAL",
           watermark=None
       )

Configuration Files
~~~~~~~~~~~~~~~~~~~

**config.yaml**:

.. code-block:: yaml

   study:
     id: STUDY001
     protocol: PROTO-001
     sponsor: Acme Pharma

   output:
     dir: reports
     format: rtf

   page:
     orientation: landscape
     size: LETTER

   fonts:
     name: Times New Roman
     size: 9

**Loading configuration**:

.. code-block:: python

   import yaml
   from py4csr.config import ReportConfig

   # Load from YAML
   with open("config.yaml") as f:
       config_dict = yaml.safe_load(f)

   # Create config from dictionary
   config = ReportConfig(
       study_id=config_dict["study"]["id"],
       protocol=config_dict["study"]["protocol"],
       output_dir=config_dict["output"]["dir"],
       default_format=config_dict["output"]["format"]
   )

Best Practices
--------------

1. **Use Configuration Files**

.. code-block:: python

   # Good - centralized configuration
   config = load_config_from_file("config.yaml")

   # Avoid - hardcoded values
   config = ReportConfig(study_id="STUDY001", ...)

2. **Validate Configuration**

.. code-block:: python

   # Validate before use
   if not config.is_valid():
       raise ValueError(f"Invalid configuration: {config.errors}")

3. **Use Environment Variables**

.. code-block:: python

   import os

   config = ReportConfig(
       study_id=os.getenv("STUDY_ID", "STUDY001"),
       output_dir=os.getenv("OUTPUT_DIR", "reports")
   )

4. **Document Custom Settings**

.. code-block:: python

   # Document why custom settings are used
   config = ReportConfig(
       font_size=8,  # Smaller font to fit wide tables
       page_orientation="landscape"  # Required for treatment comparison
   )

Next Steps
----------

- :doc:`../examples/demographics` - See configuration in action
- :doc:`../advanced/custom_statistics` - Advanced customization

