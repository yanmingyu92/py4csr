"""
Waterfall plot generator for py4csr functional plotting system.

This module generates waterfall plots showing individual patient responses,
commonly used in oncology studies to visualize tumor response data.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Optional
from datetime import datetime

from .base_generator import BasePlotGenerator
from ..plot_specification import PlotSpecification
from ..plot_result import PlotResult


class WaterfallGenerator(BasePlotGenerator):
    """
    Generator for waterfall plots.
    
    This generator creates waterfall plots showing individual patient
    responses, typically used for tumor response visualization.
    """
    
    def __init__(self):
        super().__init__()
        self._register_templates()
    
    def generate(self, spec: PlotSpecification) -> PlotResult:
        """
        Generate waterfall plot.
        
        Parameters
        ----------
        spec : PlotSpecification
            Plot specification
            
        Returns
        -------
        PlotResult
            Generated waterfall plot
        """
        # Get and validate data
        data = spec.get_data()
        validation_result = self.validate_data(data, spec)
        
        if not validation_result['passed']:
            raise ValueError(f"Data validation failed: {validation_result['errors']}")
        
        # Create figure
        fig = self.create_figure(spec)
        ax = fig.add_subplot(111)
        
        # Generate waterfall plot
        self._generate_waterfall(ax, data, spec)
        
        # Post-process figure
        fig = self.post_process_figure(fig, spec)
        
        # Generate metadata
        metadata = self.generate_metadata(spec)
        metadata.update({
            'n_subjects': len(data),
            'treatment_groups': data[spec.treatment_var].value_counts().to_dict() if spec.treatment_var else {},
            'response_range': {
                'min': data[spec.y_var].min() if spec.y_var else None,
                'max': data[spec.y_var].max() if spec.y_var else None
            }
        })
        
        return PlotResult(
            figure=fig,
            metadata=metadata,
            validation_results=validation_result
        )
    
    def _generate_waterfall(self, ax: plt.Axes, data: pd.DataFrame, spec: PlotSpecification):
        """Generate waterfall plot."""
        
        # Get plot parameters
        params = spec.get_plot_params()
        colors = spec.get_color_palette()
        
        # Prepare data
        plot_data = data.copy()
        
        # Sort data if requested
        sort_by = params.get('sort_by', 'response')
        if sort_by == 'response' and spec.y_var:
            plot_data = plot_data.sort_values(spec.y_var)
        elif sort_by == 'treatment' and spec.treatment_var:
            plot_data = plot_data.sort_values([spec.treatment_var, spec.y_var])
        
        # Reset index for plotting
        plot_data = plot_data.reset_index(drop=True)
        
        # Get response values
        if spec.y_var:
            responses = plot_data[spec.y_var]
        else:
            raise ValueError("y_var is required for waterfall plots")
        
        # Create x-axis positions
        x_positions = range(len(responses))
        
        # Determine bar colors based on response
        bar_colors = self._get_response_colors(responses, params, colors)
        
        # Create waterfall bars
        bars = ax.bar(x_positions, responses, color=bar_colors, 
                     edgecolor='black', linewidth=0.5, alpha=0.8)
        
        # Add reference lines if requested
        if params.get('show_reference_line', True):
            ref_values = params.get('reference_values', [-30, 20])
            
            # Progressive disease line (typically +20%)
            if len(ref_values) > 1:
                ax.axhline(ref_values[1], color='red', linestyle='--', 
                          alpha=0.7, label=f'Progressive Disease (+{ref_values[1]}%)')
            
            # Partial response line (typically -30%)
            if len(ref_values) > 0:
                ax.axhline(ref_values[0], color='blue', linestyle='--', 
                          alpha=0.7, label=f'Partial Response ({ref_values[0]}%)')
            
            # Stable disease (0% change)
            ax.axhline(0, color='black', linestyle='-', alpha=0.5, linewidth=1)
        
        # Customize plot
        ax.set_xlabel('Individual Patients (sorted by response)')
        ax.set_ylabel('Best % Change from Baseline')
        ax.set_title('')  # Title will be added by post-processing
        
        # Set x-axis limits
        ax.set_xlim(-0.5, len(responses) - 0.5)
        
        # Add treatment group indicators if available
        if spec.treatment_var and params.get('show_treatment_groups', True):
            self._add_treatment_indicators(ax, plot_data, spec)
        
        # Add response statistics if requested
        if params.get('show_statistics', True):
            self._add_response_statistics(ax, responses, params)
        
        # Add legend if reference lines are shown
        if params.get('show_reference_line', True):
            ax.legend(loc='upper right')
    
    def _get_response_colors(self, responses: pd.Series, params: Dict, colors: List[str]) -> List[str]:
        """Determine bar colors based on response values."""
        
        if not params.get('response_colors', True):
            # Use single color
            return [colors[0]] * len(responses)
        
        # Get reference values
        ref_values = params.get('reference_values', [-30, 20])
        
        bar_colors = []
        for response in responses:
            if pd.isna(response):
                bar_colors.append('gray')
            elif len(ref_values) > 1 and response >= ref_values[1]:
                # Progressive disease (red)
                bar_colors.append('#d62728')
            elif len(ref_values) > 0 and response <= ref_values[0]:
                # Partial response (blue)
                bar_colors.append('#1f77b4')
            else:
                # Stable disease (green)
                bar_colors.append('#2ca02c')
        
        return bar_colors
    
    def _add_treatment_indicators(self, ax: plt.Axes, data: pd.DataFrame, spec: PlotSpecification):
        """Add treatment group indicators to the plot."""
        
        treatments = data[spec.treatment_var].unique()
        colors = spec.get_color_palette()
        
        # Add colored bars at the bottom to indicate treatment groups
        y_min = ax.get_ylim()[0]
        bar_height = (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.02
        
        for i, (idx, row) in enumerate(data.iterrows()):
            treatment = row[spec.treatment_var]
            trt_idx = list(treatments).index(treatment)
            color = colors[trt_idx % len(colors)]
            
            ax.bar(i, bar_height, bottom=y_min - bar_height, 
                  color=color, alpha=0.7, width=1.0)
        
        # Add treatment legend
        legend_elements = []
        for i, treatment in enumerate(treatments):
            color = colors[i % len(colors)]
            legend_elements.append(plt.Rectangle((0, 0), 1, 1, facecolor=color, 
                                               alpha=0.7, label=treatment))
        
        # Add second legend for treatments
        ax2 = ax.twinx()
        ax2.set_yticks([])
        ax2.legend(handles=legend_elements, loc='upper left', title='Treatment')
    
    def _add_response_statistics(self, ax: plt.Axes, responses: pd.Series, params: Dict):
        """Add response statistics to the plot."""
        
        # Calculate response rates
        ref_values = params.get('reference_values', [-30, 20])
        
        stats_text = []
        
        if len(ref_values) > 0:
            # Partial response rate
            pr_rate = (responses <= ref_values[0]).sum() / len(responses) * 100
            stats_text.append(f'Partial Response: {pr_rate:.1f}%')
        
        if len(ref_values) > 1:
            # Progressive disease rate
            pd_rate = (responses >= ref_values[1]).sum() / len(responses) * 100
            stats_text.append(f'Progressive Disease: {pd_rate:.1f}%')
        
        # Stable disease rate
        if len(ref_values) >= 2:
            sd_rate = ((responses > ref_values[0]) & (responses < ref_values[1])).sum() / len(responses) * 100
            stats_text.append(f'Stable Disease: {sd_rate:.1f}%')
        
        # Add median response
        median_response = responses.median()
        stats_text.append(f'Median Response: {median_response:.1f}%')
        
        # Display statistics
        stats_str = '\n'.join(stats_text)
        ax.text(0.02, 0.98, stats_str, transform=ax.transAxes, 
               verticalalignment='top', fontsize=10,
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    def get_required_variables(self, spec: PlotSpecification) -> List[str]:
        """Get required variables for waterfall plot."""
        required = []
        
        if spec.y_var:
            required.append(spec.y_var)
        else:
            raise ValueError("y_var is required for waterfall plots")
        
        # treatment_var is optional but recommended
        if spec.treatment_var:
            required.append(spec.treatment_var)
        
        return required
    
    def _register_templates(self):
        """Register waterfall plot templates."""
        
        def tumor_response_template(data: pd.DataFrame, response_var: str, 
                                  treatment_var: str = None, **kwargs):
            """Template for tumor response waterfall plots."""
            # This would contain the core waterfall plotting logic
            pass
        
        def biomarker_template(data: pd.DataFrame, biomarker_var: str, 
                             treatment_var: str = None, **kwargs):
            """Template for biomarker change waterfall plots."""
            # This would contain biomarker-specific plotting logic
            pass
        
        self.register_template('tumor_response', tumor_response_template)
        self.register_template('biomarker_change', biomarker_template) 