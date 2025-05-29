"""
Boxplot generator for py4csr functional plotting system.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from .base_generator import BasePlotGenerator
from ..plot_specification import PlotSpecification
from ..plot_result import PlotResult


class BoxplotGenerator(BasePlotGenerator):
    """Generator for box plots."""
    
    def generate(self, spec: PlotSpecification) -> PlotResult:
        """Generate box plot."""
        data = spec.get_data()
        validation_result = self.validate_data(data, spec)
        
        fig = self.create_figure(spec)
        ax = fig.add_subplot(111)
        
        # Create box plot
        if spec.y_var and spec.group_var:
            groups = data[spec.group_var].unique()
            plot_data = [data[data[spec.group_var] == group][spec.y_var].dropna() for group in groups]
            
            ax.boxplot(plot_data, labels=groups)
            ax.set_xlabel(spec.group_var)
            ax.set_ylabel(spec.y_var)
        
        fig = self.post_process_figure(fig, spec)
        metadata = self.generate_metadata(spec)
        
        return PlotResult(
            figure=fig,
            metadata=metadata,
            validation_results=validation_result
        ) 