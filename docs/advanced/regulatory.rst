Regulatory Compliance
======================

Ensuring py4csr outputs meet regulatory requirements.

ICH E3 Guidelines
-----------------

py4csr outputs follow ICH E3 guidelines for clinical study reports:

- Standard table numbering (14.x.x)
- Required demographic variables
- Safety analysis standards
- Efficacy analysis standards

FDA Submission
--------------

RTF Format
~~~~~~~~~~

.. code-block:: python

   # Generate FDA-compliant RTF
   session.finalize(
       output_path="submission/t_dem.rtf",
       format="rtf",
       options={
           "page_orientation": "landscape",
           "font_name": "Times New Roman",
           "font_size": 9,
           "margins": {"top": 1.0, "bottom": 1.0, "left": 1.0, "right": 1.0}
       }
   )

CDISC Standards
---------------

ADaM Compliance
~~~~~~~~~~~~~~~

py4csr validates ADaM datasets for:

- Required variables (USUBJID, STUDYID, etc.)
- Variable naming conventions
- Data types and formats
- Population flags (SAFFL, EFFFL, etc.)

Next Steps
----------

- :doc:`performance` - Performance optimization
- :doc:`../user_guide/clinical_data` - CDISC data handling

