"""
Scatter plot generator for py4csr functional plotting system.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from .base_generator import BasePlotGenerator
from ..plot_specification import PlotSpecification
from ..plot_result import PlotResult


class ScatterGenerator(BasePlotGenerator):
    """Generator for scatter plots."""
    
    def generate(self, spec: PlotSpecification) -> PlotResult:
        """Generate scatter plot."""
        data = spec.get_data()
        validation_result = self.validate_data(data, spec)
        
        fig = self.create_figure(spec)
        ax = fig.add_subplot(111)
        
        # Create scatter plot
        if spec.x_var and spec.y_var:
            ax.scatter(data[spec.x_var], data[spec.y_var], alpha=0.7)
            ax.set_xlabel(spec.x_var)
            ax.set_ylabel(spec.y_var)
        
        fig = self.post_process_figure(fig, spec)
        metadata = self.generate_metadata(spec)
        
        return PlotResult(
            figure=fig,
            metadata=metadata,
            validation_results=validation_result
        ) 