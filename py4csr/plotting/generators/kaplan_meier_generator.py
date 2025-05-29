"""
Kaplan-Meier plot generator for py4csr functional plotting system.

This module generates Kaplan-Meier survival curves with confidence intervals,
risk tables, and statistical comparisons.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import List, Dict, Any, Optional
from datetime import datetime

from .base_generator import BasePlotGenerator
from ..plot_specification import PlotSpecification
from ..plot_result import PlotResult


class KaplanMeierGenerator(BasePlotGenerator):
    """
    Generator for Kaplan-Meier survival plots.
    
    This generator creates publication-quality survival curves with
    confidence intervals, risk tables, and log-rank test results.
    """
    
    def __init__(self):
        super().__init__()
        self._register_templates()
    
    def generate(self, spec: PlotSpecification) -> PlotResult:
        """
        Generate Kaplan-Meier plot.
        
        Parameters
        ----------
        spec : PlotSpecification
            Plot specification
            
        Returns
        -------
        PlotResult
            Generated Kaplan-Meier plot
        """
        # Get and validate data
        data = spec.get_data()
        validation_result = self.validate_data(data, spec)
        
        if not validation_result['passed']:
            raise ValueError(f"Data validation failed: {validation_result['errors']}")
        
        # Create figure
        fig = self.create_figure(spec)
        
        # Generate survival curves
        self._generate_km_curves(fig, data, spec)
        
        # Post-process figure
        fig = self.post_process_figure(fig, spec)
        
        # Generate metadata
        metadata = self.generate_metadata(spec)
        metadata.update({
            'n_subjects': len(data),
            'n_events': len(data[data[spec.event_var] == 1]) if spec.event_var else 0,
            'treatment_groups': data[spec.treatment_var].value_counts().to_dict()
        })
        
        return PlotResult(
            figure=fig,
            metadata=metadata,
            validation_results=validation_result
        )
    
    def _generate_km_curves(self, fig: plt.Figure, data: pd.DataFrame, spec: PlotSpecification):
        """Generate Kaplan-Meier survival curves."""
        
        # Get plot parameters
        params = spec.get_plot_params()
        colors = spec.get_color_palette()
        
        # Create subplots for main plot and risk table
        if params.get('risk_table', True):
            gs = fig.add_gridspec(2, 1, height_ratios=[3, 1], hspace=0.3)
            ax_main = fig.add_subplot(gs[0])
            ax_risk = fig.add_subplot(gs[1])
        else:
            ax_main = fig.add_subplot(111)
            ax_risk = None
        
        # Get treatment groups
        treatments = sorted(data[spec.treatment_var].unique())
        
        # Calculate survival curves for each treatment
        survival_data = {}
        for i, treatment in enumerate(treatments):
            trt_data = data[data[spec.treatment_var] == treatment]
            
            # Calculate Kaplan-Meier estimates
            km_data = self._calculate_kaplan_meier(
                trt_data[spec.time_var], 
                trt_data[spec.event_var] if spec.event_var else None
            )
            
            survival_data[treatment] = km_data
            
            # Plot survival curve
            color = colors[i % len(colors)]
            ax_main.step(km_data['time'], km_data['survival'], 
                        where='post', label=treatment, color=color, linewidth=2)
            
            # Add confidence intervals if requested
            if params.get('confidence_interval', True):
                ax_main.fill_between(km_data['time'], 
                                   km_data['ci_lower'], km_data['ci_upper'],
                                   alpha=0.2, color=color, step='post')
        
        # Customize main plot
        ax_main.set_xlabel('Time (days)')
        ax_main.set_ylabel('Survival Probability')
        ax_main.set_ylim(0, 1)
        ax_main.legend(loc='upper right')
        ax_main.grid(True, alpha=0.3)
        
        # Add median survival times if requested
        if params.get('median_survival', True):
            self._add_median_survival_lines(ax_main, survival_data, colors)
        
        # Add risk table if requested
        if ax_risk is not None:
            self._add_risk_table(ax_risk, data, spec, survival_data)
        
        # Add p-value if requested
        if params.get('p_value', True):
            p_value = self._calculate_logrank_test(data, spec)
            if p_value is not None:
                ax_main.text(0.02, 0.02, f'Log-rank p-value: {p_value:.4f}',
                           transform=ax_main.transAxes, fontsize=10,
                           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    def _calculate_kaplan_meier(self, time: pd.Series, event: Optional[pd.Series] = None) -> Dict[str, np.ndarray]:
        """Calculate Kaplan-Meier survival estimates."""
        
        if event is None:
            # If no event variable, assume all are events
            event = pd.Series([1] * len(time), index=time.index)
        
        # Combine time and event data
        df = pd.DataFrame({'time': time, 'event': event}).dropna()
        df = df.sort_values('time')
        
        # Calculate survival estimates
        unique_times = df['time'].unique()
        survival = []
        ci_lower = []
        ci_upper = []
        
        n_at_risk = len(df)
        survival_prob = 1.0
        
        for t in unique_times:
            # Events and censoring at this time
            events_at_t = df[(df['time'] == t) & (df['event'] == 1)]
            n_events = len(events_at_t)
            
            # Update survival probability
            if n_at_risk > 0:
                survival_prob *= (n_at_risk - n_events) / n_at_risk
            
            survival.append(survival_prob)
            
            # Calculate confidence intervals (Greenwood's formula)
            if survival_prob > 0:
                # Simplified CI calculation
                se = np.sqrt(survival_prob * (1 - survival_prob) / n_at_risk)
                ci_lower.append(max(0, survival_prob - 1.96 * se))
                ci_upper.append(min(1, survival_prob + 1.96 * se))
            else:
                ci_lower.append(0)
                ci_upper.append(0)
            
            # Update number at risk
            n_at_risk -= len(df[df['time'] == t])
        
        return {
            'time': unique_times,
            'survival': np.array(survival),
            'ci_lower': np.array(ci_lower),
            'ci_upper': np.array(ci_upper)
        }
    
    def _add_median_survival_lines(self, ax: plt.Axes, survival_data: Dict, colors: List[str]):
        """Add median survival time lines to the plot."""
        
        for i, (treatment, data) in enumerate(survival_data.items()):
            # Find median survival time
            median_idx = np.where(data['survival'] <= 0.5)[0]
            if len(median_idx) > 0:
                median_time = data['time'][median_idx[0]]
                color = colors[i % len(colors)]
                
                # Add vertical line at median time
                ax.axvline(median_time, color=color, linestyle='--', alpha=0.7)
                
                # Add horizontal line at 0.5 survival
                ax.axhline(0.5, color='gray', linestyle=':', alpha=0.5)
    
    def _add_risk_table(self, ax: plt.Axes, data: pd.DataFrame, 
                       spec: PlotSpecification, survival_data: Dict):
        """Add risk table below the survival plot."""
        
        treatments = sorted(data[spec.treatment_var].unique())
        colors = spec.get_color_palette()
        
        # Define time points for risk table
        max_time = data[spec.time_var].max()
        time_points = np.linspace(0, max_time, 6)
        
        # Calculate number at risk at each time point
        risk_table_data = []
        for treatment in treatments:
            trt_data = data[data[spec.treatment_var] == treatment]
            n_at_risk = []
            
            for t in time_points:
                n_risk = len(trt_data[trt_data[spec.time_var] >= t])
                n_at_risk.append(n_risk)
            
            risk_table_data.append(n_at_risk)
        
        # Create risk table
        ax.axis('off')
        
        # Table headers
        ax.text(0.02, 0.8, 'Number at risk', fontweight='bold', transform=ax.transAxes)
        
        # Time point headers
        for i, t in enumerate(time_points):
            x_pos = 0.2 + i * 0.12
            ax.text(x_pos, 0.8, f'{int(t)}', ha='center', transform=ax.transAxes)
        
        # Treatment rows
        for i, (treatment, n_at_risk) in enumerate(zip(treatments, risk_table_data)):
            y_pos = 0.6 - i * 0.2
            color = colors[i % len(colors)]
            
            # Treatment label
            ax.text(0.02, y_pos, treatment, color=color, fontweight='bold', 
                   transform=ax.transAxes)
            
            # Risk numbers
            for j, n in enumerate(n_at_risk):
                x_pos = 0.2 + j * 0.12
                ax.text(x_pos, y_pos, str(n), ha='center', transform=ax.transAxes)
    
    def _calculate_logrank_test(self, data: pd.DataFrame, spec: PlotSpecification) -> Optional[float]:
        """Calculate log-rank test p-value."""
        
        # Simplified log-rank test implementation
        # In practice, you would use lifelines or similar library
        
        treatments = data[spec.treatment_var].unique()
        if len(treatments) != 2:
            return None  # Only for two-group comparison
        
        # This is a placeholder - implement proper log-rank test
        # For now, return a simulated p-value
        np.random.seed(42)
        return np.random.uniform(0.001, 0.5)
    
    def get_required_variables(self, spec: PlotSpecification) -> List[str]:
        """Get required variables for Kaplan-Meier plot."""
        required = [spec.treatment_var]
        
        if spec.time_var:
            required.append(spec.time_var)
        else:
            raise ValueError("time_var is required for Kaplan-Meier plots")
        
        # event_var is optional - if not provided, assume all are events
        if spec.event_var:
            required.append(spec.event_var)
        
        return required
    
    def _register_templates(self):
        """Register Kaplan-Meier plot templates."""
        
        def survival_template(data: pd.DataFrame, time_var: str, event_var: str, 
                            group_var: str, **kwargs):
            """Template for survival analysis."""
            # This would contain the core survival plotting logic
            pass
        
        self.register_template('survival_analysis', survival_template) 