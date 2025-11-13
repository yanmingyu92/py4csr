.. py4csr documentation master file

Welcome to py4csr's documentation!
===================================

**py4csr** is a comprehensive Python package for clinical study reporting that brings the power and flexibility of SAS RRG (Rapid Report Generator) to the Python ecosystem.

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart
   concepts

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   user_guide/functional_system
   user_guide/clinical_data
   user_guide/statistical_analysis
   user_guide/output_generation
   user_guide/configuration

.. toctree::
   :maxdepth: 2
   :caption: Advanced Topics

   advanced/custom_statistics
   advanced/plotting
   advanced/regulatory
   advanced/performance

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/clinical
   api/functional
   api/reporting
   api/analysis
   api/data
   api/plotting
   api/config
   api/exceptions

.. toctree::
   :maxdepth: 2
   :caption: Examples

   examples/demographics
   examples/adverse_events
   examples/efficacy
   examples/real_data

.. toctree::
   :maxdepth: 2
   :caption: Development

   development/contributing
   development/testing
   development/releases

What is py4csr?
===============

py4csr is designed to bridge the gap between SAS-based clinical reporting and modern Python data science workflows.

Key Features
------------

📊 **SAS RRG Equivalent Functionality**
   - Functional programming approach similar to SAS RRG macros
   - Method chaining for building complex reports step-by-step
   - Statistical templates for common clinical calculations
   - Multiple output formats (RTF, PDF, HTML, Excel)

🏥 **Clinical Trial Focus**
   - CDISC compliance with built-in ADaM dataset support
   - Regulatory standards following ICH E3 and CTD guidelines
   - Real data validation tested with actual pharmaceutical datasets
   - Industry best practices for clinical reporting

🔧 **Production Ready**
   - Comprehensive testing including real clinical trial data
   - Performance optimized for large datasets
   - Extensible architecture for custom requirements
   - Professional documentation and examples

Quick Example
=============

.. code-block:: python

   from py4csr.functional import ReportSession

   # Create a complete clinical study report
   result = (ReportSession()
       .init_study(
           uri="STUDY001", 
           title="Phase III Efficacy and Safety Study",
           protocol="ABC-123-2024"
       )
       .load_datasets(data_path="data/")
       .define_populations(
           safety="SAFFL=='Y'", 
           efficacy="EFFFL=='Y'"
       )
       .define_treatments(var="TRT01P")
       .add_demographics_table()
       .add_ae_summary()
       .add_efficacy_analysis()
       .generate_all(output_dir="clinical_reports")
       .finalize()
   )

   print(f"Generated {len(result.generated_files)} report files")

Tested with Real Data
======================

py4csr has been extensively tested with real clinical trial data:

- **CDISC Pilot Study**: 254 subjects, 10 ADaM datasets (~92MB)
- **Multiple domains**: Demographics, AE, Laboratory, Vital Signs, Questionnaires
- **Complex scenarios**: Multiple visits, missing data, regulatory requirements
- **Production quality**: Ready for pharmaceutical industry use

Installation
============

Install py4csr using pip:

.. code-block:: bash

   pip install py4csr

For PDF output support:

.. code-block:: bash

   pip install py4csr[pdf]

For development:

.. code-block:: bash

   pip install py4csr[dev]

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

