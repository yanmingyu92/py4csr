Clinical Plotting
==================

Advanced plotting capabilities for clinical trial visualizations.

Kaplan-Meier Plots
------------------

Basic KM Plot
~~~~~~~~~~~~~

.. code-block:: python

   from py4csr.plotting import ComprehensiveClinicalPlots
   import pandas as pd

   # Load time-to-event data
   adtte = pd.read_csv("data/adtte.csv")

   # Create plotter
   plotter = ComprehensiveClinicalPlots()

   # Create KM plot
   plot_result = plotter.create_km_plot(
       data=adtte,
       time_var="AVAL",
       event_var="CNSR",
       treatment_var="TRT01P",
       title="Overall Survival"
   )

   # Save as RTF and HTML
   plot_result.save("reports/km_plot.rtf", format="rtf")
   plot_result.save("reports/km_plot.html", format="html")

Forest Plots
------------

Subgroup Analysis
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Create forest plot
   plot_result = plotter.create_forest_plot(
       data=adeff,
       endpoint="CHG",
       subgroups=["SEX", "RACE", "AGEGR1"],
       treatment_var="TRT01P",
       title="Treatment Effect by Subgroup"
   )

   plot_result.save("reports/forest_plot.html", format="html")

Box Plots
---------

Distribution Analysis
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Create box plot
   plot_result = plotter.create_box_plot(
       data=adlb,
       value_var="CHG",
       treatment_var="TRT01P",
       visit_var="AVISIT",
       title="Change from Baseline by Visit"
   )

   plot_result.save("reports/box_plot.html", format="html")

Next Steps
----------

- :doc:`regulatory` - Regulatory compliance
- :doc:`performance` - Performance optimization

