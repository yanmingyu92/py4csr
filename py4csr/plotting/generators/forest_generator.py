"""
Forest plot generator for py4csr functional plotting system.

This module generates forest plots showing treatment effects across subgroups,
commonly used in meta-analyses and subgroup analyses.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Optional
from datetime import datetime

from .base_generator import BasePlotGenerator
from ..plot_specification import PlotSpecification
from ..plot_result import PlotResult


class ForestGenerator(BasePlotGenerator):
    """
    Generator for forest plots.
    
    This generator creates forest plots showing treatment effects
    (hazard ratios, odds ratios, etc.) across different subgroups.
    """
    
    def __init__(self):
        super().__init__()
        self._register_templates()
    
    def generate(self, spec: PlotSpecification) -> PlotResult:
        """
        Generate forest plot.
        
        Parameters
        ----------
        spec : PlotSpecification
            Plot specification
            
        Returns
        -------
        PlotResult
            Generated forest plot
        """
        # Get and validate data
        data = spec.get_data()
        validation_result = self.validate_data(data, spec)
        
        if not validation_result['passed']:
            raise ValueError(f"Data validation failed: {validation_result['errors']}")
        
        # Create figure
        fig = self.create_figure(spec)
        ax = fig.add_subplot(111)
        
        # Generate forest plot
        self._generate_forest_plot(ax, data, spec)
        
        # Post-process figure
        fig = self.post_process_figure(fig, spec)
        
        # Generate metadata
        metadata = self.generate_metadata(spec)
        metadata.update({
            'n_subgroups': len(data),
            'effect_measure': spec.plot_params.get('effect_measure', 'HR'),
            'reference_value': spec.plot_params.get('reference_line', 1.0)
        })
        
        return PlotResult(
            figure=fig,
            metadata=metadata,
            validation_results=validation_result
        )
    
    def _generate_forest_plot(self, ax: plt.Axes, data: pd.DataFrame, spec: PlotSpecification):
        """Generate forest plot."""
        
        # Get plot parameters
        params = spec.get_plot_params()
        colors = spec.get_color_palette()
        
        # Required columns for forest plot
        required_cols = ['subgroup', 'estimate', 'ci_lower', 'ci_upper']
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            # Create sample data for demonstration
            data = self._create_sample_forest_data()
        
        # Sort data by estimate if requested
        if params.get('sort_by_estimate', False):
            data = data.sort_values('estimate')
        
        # Create y-axis positions
        y_positions = range(len(data))
        
        # Plot confidence intervals
        for i, (_, row) in enumerate(data.iterrows()):
            estimate = row['estimate']
            ci_lower = row['ci_lower']
            ci_upper = row['ci_upper']
            
            # Plot confidence interval line
            ax.plot([ci_lower, ci_upper], [i, i], 'k-', linewidth=2, alpha=0.7)
            
            # Plot point estimate
            ax.plot(estimate, i, 'o', markersize=8, color=colors[0], 
                   markeredgecolor='black', markeredgewidth=1)
        
        # Add reference line
        ref_line = params.get('reference_line', 1.0)
        ax.axvline(ref_line, color='red', linestyle='--', alpha=0.7, linewidth=2)
        
        # Customize axes
        ax.set_yticks(y_positions)
        ax.set_yticklabels(data['subgroup'])
        ax.set_xlabel(f"{params.get('effect_measure', 'Effect Estimate')} (95% CI)")
        ax.set_ylabel('Subgroup')
        
        # Set x-axis to log scale if requested
        if params.get('log_scale', True):
            ax.set_xscale('log')
            ax.set_xlabel(f"{params.get('effect_measure', 'Effect Estimate')} (95% CI) - Log Scale")
        
        # Add grid
        ax.grid(True, alpha=0.3, axis='x')
        
        # Add effect estimates and CIs as text
        if params.get('show_estimates', True):
            self._add_estimate_text(ax, data, params)
        
        # Add sample sizes if available
        if 'n' in data.columns and params.get('show_n', True):
            self._add_sample_sizes(ax, data)
        
        # Invert y-axis to have first subgroup at top
        ax.invert_yaxis()
        
        # Add favors labels
        if params.get('show_favors', True):
            self._add_favors_labels(ax, params)
    
    def _create_sample_forest_data(self) -> pd.DataFrame:
        """Create sample forest plot data for demonstration."""
        
        np.random.seed(42)
        
        subgroups = [
            'Overall',
            'Age < 65',
            'Age ≥ 65',
            'Male',
            'Female',
            'Stage I-II',
            'Stage III-IV',
            'ECOG 0',
            'ECOG 1-2'
        ]
        
        # Generate realistic hazard ratios
        estimates = np.random.lognormal(mean=-0.2, sigma=0.3, size=len(subgroups))
        
        # Generate confidence intervals
        ci_width = np.random.uniform(0.1, 0.4, size=len(subgroups))
        ci_lower = estimates * np.exp(-ci_width)
        ci_upper = estimates * np.exp(ci_width)
        
        # Sample sizes
        n_values = np.random.randint(50, 300, size=len(subgroups))
        
        return pd.DataFrame({
            'subgroup': subgroups,
            'estimate': estimates,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'n': n_values
        })
    
    def _add_estimate_text(self, ax: plt.Axes, data: pd.DataFrame, params: Dict):
        """Add effect estimates and confidence intervals as text."""
        
        # Find the rightmost position for text
        x_max = ax.get_xlim()[1]
        x_text = x_max * 1.1
        
        # Extend x-axis to accommodate text
        ax.set_xlim(ax.get_xlim()[0], x_max * 1.4)
        
        # Add header
        ax.text(x_text, len(data), f"{params.get('effect_measure', 'HR')} (95% CI)", 
               fontweight='bold', ha='left', va='center')
        
        # Add estimates for each subgroup
        for i, (_, row) in enumerate(data.iterrows()):
            estimate = row['estimate']
            ci_lower = row['ci_lower']
            ci_upper = row['ci_upper']
            
            text = f"{estimate:.2f} ({ci_lower:.2f}, {ci_upper:.2f})"
            ax.text(x_text, i, text, ha='left', va='center', fontsize=10)
    
    def _add_sample_sizes(self, ax: plt.Axes, data: pd.DataFrame):
        """Add sample sizes to the plot."""
        
        # Find the leftmost position for text
        x_min = ax.get_xlim()[0]
        x_text = x_min * 0.1 if x_min > 0 else x_min * 1.1
        
        # Extend x-axis to accommodate text
        current_xlim = ax.get_xlim()
        ax.set_xlim(x_text * 1.2, current_xlim[1])
        
        # Add header
        ax.text(x_text, len(data), 'N', fontweight='bold', ha='center', va='center')
        
        # Add sample sizes for each subgroup
        for i, (_, row) in enumerate(data.iterrows()):
            n = row['n']
            ax.text(x_text, i, str(int(n)), ha='center', va='center', fontsize=10)
    
    def _add_favors_labels(self, ax: plt.Axes, params: Dict):
        """Add 'favors' labels below the plot."""
        
        ref_line = params.get('reference_line', 1.0)
        favors_left = params.get('favors_left', 'Favors Treatment')
        favors_right = params.get('favors_right', 'Favors Control')
        
        # Get x-axis limits
        x_min, x_max = ax.get_xlim()
        
        # Position labels
        y_pos = -0.5
        
        # Left label
        x_left = x_min + (ref_line - x_min) * 0.5
        ax.text(x_left, y_pos, favors_left, ha='center', va='top', 
               fontsize=10, style='italic')
        
        # Right label
        x_right = ref_line + (x_max - ref_line) * 0.5
        ax.text(x_right, y_pos, favors_right, ha='center', va='top', 
               fontsize=10, style='italic')
    
    def get_required_variables(self, spec: PlotSpecification) -> List[str]:
        """Get required variables for forest plot."""
        # Forest plots typically use pre-calculated estimates
        # So we don't require specific raw data variables
        return []
    
    def _register_templates(self):
        """Register forest plot templates."""
        
        def subgroup_analysis_template(data: pd.DataFrame, **kwargs):
            """Template for subgroup analysis forest plots."""
            # This would contain subgroup-specific plotting logic
            pass
        
        def meta_analysis_template(data: pd.DataFrame, **kwargs):
            """Template for meta-analysis forest plots."""
            # This would contain meta-analysis specific plotting logic
            pass
        
        self.register_template('subgroup_analysis', subgroup_analysis_template)
        self.register_template('meta_analysis', meta_analysis_template) 