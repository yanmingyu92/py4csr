Output Generation
=================

py4csr supports multiple output formats for clinical study reports, each optimized for different use cases.

Supported Formats
-----------------

py4csr generates outputs in four formats:

.. list-table::
   :header-rows: 1
   :widths: 15 25 30 30

   * - Format
     - Use Case
     - Advantages
     - Requirements
   * - **RTF**
     - Regulatory submission
     - Industry standard, editable
     - None (built-in)
   * - **PDF**
     - Final reports, archival
     - Professional, portable
     - reportlab package
   * - **HTML**
     - Interactive review
     - Interactive plots, web-based
     - None (built-in)
   * - **CSV**
     - Data review, QC
     - Easy to review in Excel
     - None (built-in)

RTF Output
----------

Overview
~~~~~~~~

**RTF (Rich Text Format)** is the industry standard for regulatory submissions:

- Accepted by FDA, EMA, and other regulatory agencies
- Editable in Microsoft Word
- Preserves formatting and tables
- Supports headers, footers, and page numbers

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from py4csr.clinical import ClinicalSession

   session = ClinicalSession(uri="STUDY001")
   session.define_report(dataset=adsl, subjid="USUBJID")
   session.add_trt(name="TRT01PN", decode="TRT01P")
   session.add_var(name="AGE", stats="n mean+sd")
   session.generate()

   # Save as RTF
   session.finalize(
       output_path="reports/demographics.rtf",
       format="rtf"
   )

Advanced RTF Options
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Customize RTF output
   session.finalize(
       output_path="reports/demographics.rtf",
       format="rtf",
       options={
           "page_orientation": "landscape",  # or "portrait"
           "font_name": "Times New Roman",
           "font_size": 10,
           "margins": {
               "top": 1.0,    # inches
               "bottom": 1.0,
               "left": 1.0,
               "right": 1.0
           },
           "header": "CONFIDENTIAL - Study PROTO-001",
           "footer": "Page {page} of {total_pages}",
           "title_page": True
       }
   )

RTF Table Formatting
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Customize table appearance
   session.finalize(
       output_path="reports/demographics.rtf",
       format="rtf",
       options={
           "table_style": {
               "border_width": 1,
               "cell_padding": 0.05,
               "header_background": "#E0E0E0",
               "alternating_rows": True,
               "row_colors": ["#FFFFFF", "#F5F5F5"]
           }
       }
   )

PDF Output
----------

Overview
~~~~~~~~

**PDF (Portable Document Format)** provides professional, non-editable reports:

- Consistent appearance across platforms
- Suitable for archival and distribution
- Supports embedded fonts and images
- Requires reportlab package

Installation
~~~~~~~~~~~~

.. code-block:: bash

   # Install with PDF support
   pip install py4csr[pdf]

   # Or install reportlab separately
   pip install reportlab

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from py4csr.clinical import ClinicalSession

   session = ClinicalSession(uri="STUDY001")
   session.define_report(dataset=adsl, subjid="USUBJID")
   session.add_trt(name="TRT01PN", decode="TRT01P")
   session.add_var(name="AGE", stats="n mean+sd")
   session.generate()

   # Save as PDF
   session.finalize(
       output_path="reports/demographics.pdf",
       format="pdf"
   )

Advanced PDF Options
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Customize PDF output
   session.finalize(
       output_path="reports/demographics.pdf",
       format="pdf",
       options={
           "page_size": "A4",  # or "LETTER", "LEGAL"
           "page_orientation": "landscape",
           "font_name": "Helvetica",
           "font_size": 10,
           "margins": {
               "top": 72,    # points (1 inch = 72 points)
               "bottom": 72,
               "left": 72,
               "right": 72
           },
           "header": "Study PROTO-001 - Demographics",
           "footer": "Page {page}",
           "watermark": "DRAFT",
           "metadata": {
               "title": "Demographics Table",
               "author": "Clinical Team",
               "subject": "Phase III Study"
           }
       }
   )

HTML Output
-----------

Overview
~~~~~~~~

**HTML (HyperText Markup Language)** provides interactive, web-based reports:

- Interactive plots with zoom, pan, hover
- Responsive design for different screen sizes
- Easy to share via email or web
- No special software required to view

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from py4csr.clinical import ClinicalSession

   session = ClinicalSession(uri="STUDY001")
   session.define_report(dataset=adsl, subjid="USUBJID")
   session.add_trt(name="TRT01PN", decode="TRT01P")
   session.add_var(name="AGE", stats="n mean+sd")
   session.generate()

   # Save as HTML
   session.finalize(
       output_path="reports/demographics.html",
       format="html"
   )

Interactive Plots
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from py4csr.plotting import ComprehensiveClinicalPlots

   # Create interactive Kaplan-Meier plot
   plotter = ComprehensiveClinicalPlots()
   plot_result = plotter.create_km_plot(
       data=adtte,
       time_var="AVAL",
       event_var="CNSR",
       treatment_var="TRT01P",
       title="Overall Survival"
   )

   # Save as interactive HTML
   plot_result.save(
       output_path="reports/km_plot.html",
       format="html"
   )

HTML Customization
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Customize HTML output
   session.finalize(
       output_path="reports/demographics.html",
       format="html",
       options={
           "theme": "light",  # or "dark"
           "interactive": True,
           "include_css": True,
           "include_js": True,
           "responsive": True,
           "table_options": {
               "sortable": True,
               "filterable": True,
               "searchable": True
           }
       }
   )

CSV Output
----------

Overview
~~~~~~~~

**CSV (Comma-Separated Values)** provides simple, tabular data:

- Easy to open in Excel or other spreadsheet software
- Useful for data review and quality control
- No formatting, just raw data
- Small file size

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from py4csr.clinical import ClinicalSession

   session = ClinicalSession(uri="STUDY001")
   session.define_report(dataset=adsl, subjid="USUBJID")
   session.add_trt(name="TRT01PN", decode="TRT01P")
   session.add_var(name="AGE", stats="n mean+sd")
   session.generate()

   # Save as CSV
   session.finalize(
       output_path="reports/demographics.csv",
       format="csv"
   )

CSV Options
~~~~~~~~~~~

.. code-block:: python

   # Customize CSV output
   session.finalize(
       output_path="reports/demographics.csv",
       format="csv",
       options={
           "delimiter": ",",  # or "\t" for TSV
           "quoting": "minimal",
           "encoding": "utf-8",
           "include_header": True,
           "include_metadata": False
       }
   )

Multiple Formats
----------------

Generating All Formats
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from py4csr.clinical import ClinicalSession

   session = ClinicalSession(uri="STUDY001")
   session.define_report(dataset=adsl, subjid="USUBJID")
   session.add_trt(name="TRT01PN", decode="TRT01P")
   session.add_var(name="AGE", stats="n mean+sd")
   session.generate()

   # Generate all formats
   for fmt in ["rtf", "pdf", "html", "csv"]:
       session.finalize(
           output_path=f"reports/demographics.{fmt}",
           format=fmt
       )

Using Functional Interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from py4csr.reporting import ReportBuilder
   from py4csr.config import ReportConfig

   config = ReportConfig()
   builder = (ReportBuilder(config)
       .init_study(uri="STUDY001")
       .add_dataset("adsl", adsl)
       .define_treatments(var="TRT01P")
       .add_demographics_table()
   )

   # Generate RTF for submission
   result_rtf = builder.generate_all(
       output_dir="reports/rtf",
       format="rtf"
   )

   # Generate HTML for review
   result_html = builder.generate_all(
       output_dir="reports/html",
       format="html"
   )

   # Generate CSV for QC
   result_csv = builder.generate_all(
       output_dir="reports/csv",
       format="csv"
   )

Output Organization
-------------------

Directory Structure
~~~~~~~~~~~~~~~~~~~

Organize outputs by format and type:

.. code-block:: text

   reports/
   ├── rtf/              # Regulatory submission
   │   ├── t_dem.rtf
   │   ├── t_ae.rtf
   │   └── t_eff.rtf
   ├── pdf/              # Final reports
   │   ├── t_dem.pdf
   │   ├── t_ae.pdf
   │   └── t_eff.pdf
   ├── html/             # Interactive review
   │   ├── t_dem.html
   │   ├── t_ae.html
   │   └── figures/
   │       ├── km_plot.html
   │       └── forest_plot.html
   └── csv/              # Data review
       ├── t_dem.csv
       ├── t_ae.csv
       └── t_eff.csv

Automated Organization
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import os
   from pathlib import Path

   # Create directory structure
   base_dir = Path("reports")
   for fmt in ["rtf", "pdf", "html", "csv"]:
       (base_dir / fmt).mkdir(parents=True, exist_ok=True)

   # Generate reports in organized structure
   for fmt in ["rtf", "pdf", "html", "csv"]:
       session.finalize(
           output_path=base_dir / fmt / f"demographics.{fmt}",
           format=fmt
       )

Best Practices
--------------

1. **Use RTF for Regulatory Submission**

.. code-block:: python

   # Generate RTF for FDA/EMA submission
   session.finalize(
       output_path="submission/t_dem.rtf",
       format="rtf",
       options={
           "page_orientation": "landscape",
           "font_name": "Times New Roman",
           "font_size": 9
       }
   )

2. **Use HTML for Internal Review**

.. code-block:: python

   # Generate interactive HTML for team review
   session.finalize(
       output_path="review/t_dem.html",
       format="html",
       options={"interactive": True}
   )

3. **Use CSV for Quality Control**

.. code-block:: python

   # Generate CSV for data verification
   session.finalize(
       output_path="qc/t_dem.csv",
       format="csv"
   )

4. **Include Metadata**

.. code-block:: python

   # Add metadata to outputs
   session.finalize(
       output_path="reports/demographics.rtf",
       format="rtf",
       options={
           "header": f"Study {study_id} - {table_title}",
           "footer": f"Generated: {datetime.now():%Y-%m-%d %H:%M}",
           "metadata": {
               "study": study_id,
               "date": datetime.now().isoformat(),
               "version": "1.0"
           }
       }
   )

5. **Validate Outputs**

.. code-block:: python

   import os

   # Check file was created
   output_path = "reports/demographics.rtf"
   session.finalize(output_path=output_path, format="rtf")

   if os.path.exists(output_path):
       file_size = os.path.getsize(output_path)
       print(f"✅ Output created: {output_path} ({file_size:,} bytes)")
   else:
       print(f"❌ Output failed: {output_path}")

Next Steps
----------

- :doc:`configuration` - Customize output settings
- :doc:`../examples/demographics` - See complete output examples
- :doc:`../advanced/regulatory` - Learn about regulatory compliance

