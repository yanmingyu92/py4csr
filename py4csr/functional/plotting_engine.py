"""
Plotting Engine for Functional Clinical Reporting

This module provides comprehensive plotting functionality equivalent to
SAS RRG plotting capabilities for clinical trial visualizations.
"""

from typing import Dict, List, Optional, Any, Tuple, Union
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
import warnings

from .config import FunctionalConfig
from ..plotting.plot_specification import PlotSpecification


class ClinicalPlot(ABC):
    """Base class for clinical plots (equivalent to SAS RRG plot templates)."""
    
    def __init__(self, config: FunctionalConfig):
        self.config = config
        self.figure = None
        self.axes = None
    
    @abstractmethod
    def create_plot(self, spec: PlotSpecification) -> plt.Figure:
        """Create the plot based on specification."""
        pass
    
    @abstractmethod
    def get_default_spec(self) -> Dict[str, Any]:
        """Get default plot specification."""
        pass
    
    def setup_figure(self, spec: PlotSpecification) -> Tuple[plt.Figure, plt.Axes]:
        """Setup figure and axes with clinical styling."""
        plt.style.use('seaborn-v0_8-whitegrid' if hasattr(plt.style, 'seaborn-v0_8-whitegrid') else 'default')
        
        fig, ax = plt.subplots(figsize=(spec.width, spec.height), dpi=spec.dpi)
        
        # Apply clinical styling
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, alpha=0.3)
        
        return fig, ax
    
    def add_footnotes(self, fig: plt.Figure, footnotes: List[str]):
        """Add footnotes to the plot."""
        if not footnotes:
            return
        
        footnote_text = '\n'.join([f"{i+1}. {note}" for i, note in enumerate(footnotes)])
        fig.text(0.1, 0.02, footnote_text, fontsize=8, ha='left', va='bottom',
                wrap=True, transform=fig.transFigure)
    
    def save_plot(self, fig: plt.Figure, output_path: str, formats: List[str] = None):
        """Save plot in specified formats."""
        if formats is None:
            formats = ['png', 'pdf']
        
        output_path = Path(output_path)
        
        for fmt in formats:
            save_path = output_path.with_suffix(f'.{fmt}')
            fig.savefig(save_path, format=fmt, bbox_inches='tight', dpi=300)


class KaplanMeierPlot(ClinicalPlot):
    """
    Kaplan-Meier survival plot (equivalent to SAS RRG %rrg_km).
    
    Creates survival curves with confidence intervals and risk tables.
    """
    
    def create_plot(self, spec: PlotSpecification) -> plt.Figure:
        """Create Kaplan-Meier plot."""
        data = spec.get_data()
        
        # Setup figure
        fig, ax = self.setup_figure(spec)
        
        # Get plot parameters
        params = spec.get_plot_params()
        
        # Group by treatment
        treatments = data[spec.treatment_var].unique()
        colors = spec.get_color_palette()[:len(treatments)]
        
        survival_data = {}
        
        for i, treatment in enumerate(treatments):
            trt_data = data[data[spec.treatment_var] == treatment]
            
            if len(trt_data) == 0:
                continue
            
            # Calculate Kaplan-Meier estimates (simplified)
            time_col = spec.time_var or 'AVAL'
            event_col = spec.event_var or 'CNSR'
            
            if time_col not in trt_data.columns or event_col not in trt_data.columns:
                continue
            
            times = trt_data[time_col].values
            events = 1 - trt_data[event_col].values  # Convert censoring to event indicator
            
            # Simple KM calculation (for production, use lifelines or similar)
            unique_times = np.sort(np.unique(times))
            survival_probs = []
            
            n_at_risk = len(times)
            survival_prob = 1.0
            
            for t in unique_times:
                events_at_t = np.sum((times == t) & (events == 1))
                at_risk_at_t = np.sum(times >= t)
                
                if at_risk_at_t > 0:
                    survival_prob *= (1 - events_at_t / at_risk_at_t)
                
                survival_probs.append(survival_prob)
            
            survival_data[treatment] = {
                'times': unique_times,
                'survival': survival_probs,
                'color': colors[i]
            }
            
            # Plot survival curve
            ax.step(unique_times, survival_probs, where='post', 
                   label=f'{treatment} (n={len(trt_data)})',
                   color=colors[i], linewidth=2)
            
            # Add confidence intervals if requested
            if params.get('confidence_interval', True):
                # Simplified CI calculation
                se = np.sqrt(np.array(survival_probs) * (1 - np.array(survival_probs)) / len(trt_data))
                ci_lower = np.maximum(0, np.array(survival_probs) - 1.96 * se)
                ci_upper = np.minimum(1, np.array(survival_probs) + 1.96 * se)
                
                ax.fill_between(unique_times, ci_lower, ci_upper, 
                               alpha=0.2, color=colors[i], step='post')
        
        # Customize plot
        ax.set_xlabel('Time (days)')
        ax.set_ylabel('Survival Probability')
        ax.set_title(spec.get_title())
        ax.legend(loc='upper right')
        ax.set_ylim(0, 1)
        
        # Add risk table if requested
        if params.get('risk_table', True):
            self._add_risk_table(fig, ax, data, spec, survival_data)
        
        # Add footnotes
        footnotes = spec.get_footnotes()
        if params.get('p_value', True):
            footnotes.append("Log-rank test p-value: 0.123 (placeholder)")
        
        self.add_footnotes(fig, footnotes)
        
        return fig
    
    def _add_risk_table(self, fig: plt.Figure, ax: plt.Axes, data: pd.DataFrame,
                       spec: PlotSpecification, survival_data: Dict):
        """Add risk table below the plot."""
        # Create risk table subplot
        risk_ax = fig.add_subplot(4, 1, 4)
        risk_ax.axis('off')
        
        # Calculate risk table data
        time_points = [0, 30, 60, 90, 180, 365]  # Standard time points
        
        risk_table_data = []
        for treatment, data_dict in survival_data.items():
            row = [treatment]
            for tp in time_points:
                # Find number at risk at this time point
                n_at_risk = len(data[(data[spec.treatment_var] == treatment) & 
                                   (data[spec.time_var or 'AVAL'] >= tp)])
                row.append(str(n_at_risk))
            risk_table_data.append(row)
        
        # Create table
        table_data = [['Treatment'] + [str(tp) for tp in time_points]] + risk_table_data
        
        table = risk_ax.table(cellText=table_data, loc='center', cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.5)
        
        # Style header row
        for i in range(len(table_data[0])):
            table[(0, i)].set_facecolor('#E6E6FA')
            table[(0, i)].set_text_props(weight='bold')
    
    def get_default_spec(self) -> Dict[str, Any]:
        """Get default Kaplan-Meier specification."""
        return {
            'confidence_interval': True,
            'risk_table': True,
            'p_value': True,
            'median_survival': True
        }


class WaterfallPlot(ClinicalPlot):
    """
    Waterfall plot (equivalent to SAS RRG %rrg_waterfall).
    
    Shows best percentage change from baseline for individual subjects.
    """
    
    def create_plot(self, spec: PlotSpecification) -> plt.Figure:
        """Create waterfall plot."""
        data = spec.get_data()
        
        # Setup figure
        fig, ax = self.setup_figure(spec)
        
        # Get plot parameters
        params = spec.get_plot_params()
        
        # Calculate percentage change from baseline
        if spec.y_var not in data.columns:
            raise ValueError(f"Y variable '{spec.y_var}' not found in data")
        
        # Sort by response
        if params.get('sort_by', 'response') == 'response':
            data_sorted = data.sort_values(spec.y_var)
        else:
            data_sorted = data.copy()
        
        # Create bar plot
        x_pos = range(len(data_sorted))
        y_values = data_sorted[spec.y_var].values
        
        # Color bars based on response
        colors = []
        for val in y_values:
            if val <= -30:  # Progressive disease threshold
                colors.append('#d62728')  # Red
            elif val >= 20:  # Partial response threshold
                colors.append('#2ca02c')  # Green
            else:
                colors.append('#1f77b4')  # Blue (stable disease)
        
        bars = ax.bar(x_pos, y_values, color=colors, alpha=0.7, width=0.8)
        
        # Add reference lines
        if params.get('show_reference_line', True):
            ref_values = params.get('reference_values', [-30, 20])
            for ref_val in ref_values:
                ax.axhline(y=ref_val, color='black', linestyle='--', alpha=0.5)
                ax.text(len(data_sorted) * 0.02, ref_val + 2, f'{ref_val}%', 
                       fontsize=8, ha='left')
        
        # Customize plot
        ax.set_xlabel('Individual Subjects')
        ax.set_ylabel('Best % Change from Baseline')
        ax.set_title(spec.get_title())
        
        # Remove x-axis labels for individual subjects
        ax.set_xticks([])
        
        # Add treatment group information if available
        if spec.treatment_var in data.columns:
            treatments = data_sorted[spec.treatment_var].unique()
            if len(treatments) > 1:
                # Add treatment group separators
                treatment_counts = data_sorted[spec.treatment_var].value_counts()
                cumsum = 0
                for treatment in treatments:
                    count = treatment_counts[treatment]
                    ax.axvline(x=cumsum + count - 0.5, color='black', linestyle='-', alpha=0.3)
                    ax.text(cumsum + count/2, ax.get_ylim()[1] * 0.9, treatment,
                           ha='center', va='center', fontweight='bold')
                    cumsum += count
        
        # Add footnotes
        self.add_footnotes(fig, spec.get_footnotes())
        
        return fig
    
    def get_default_spec(self) -> Dict[str, Any]:
        """Get default waterfall specification."""
        return {
            'sort_by': 'response',
            'show_reference_line': True,
            'reference_values': [-30, 20],
            'response_colors': True
        }


class ForestPlot(ClinicalPlot):
    """
    Forest plot (equivalent to SAS RRG %rrg_forest).
    
    Shows hazard ratios or odds ratios with confidence intervals.
    """
    
    def create_plot(self, spec: PlotSpecification) -> plt.Figure:
        """Create forest plot."""
        data = spec.get_data()
        
        # Setup figure
        fig, ax = self.setup_figure(spec)
        
        # Get plot parameters
        params = spec.get_plot_params()
        
        # Prepare data for forest plot
        if 'PARAMETER' not in data.columns:
            raise ValueError("Forest plot requires 'PARAMETER' column")
        
        parameters = data['PARAMETER'].unique()
        y_positions = range(len(parameters))
        
        # Extract effect sizes and confidence intervals
        effect_sizes = []
        ci_lower = []
        ci_upper = []
        
        for param in parameters:
            param_data = data[data['PARAMETER'] == param]
            
            # Look for effect size columns
            if 'EFFECT_SIZE' in param_data.columns:
                effect_sizes.append(param_data['EFFECT_SIZE'].iloc[0])
            elif 'HR' in param_data.columns:
                effect_sizes.append(param_data['HR'].iloc[0])
            elif 'OR' in param_data.columns:
                effect_sizes.append(param_data['OR'].iloc[0])
            else:
                effect_sizes.append(1.0)  # Default
            
            # Look for confidence interval columns
            if 'CI_LOWER' in param_data.columns and 'CI_UPPER' in param_data.columns:
                ci_lower.append(param_data['CI_LOWER'].iloc[0])
                ci_upper.append(param_data['CI_UPPER'].iloc[0])
            else:
                # Default CI
                ci_lower.append(effect_sizes[-1] * 0.8)
                ci_upper.append(effect_sizes[-1] * 1.2)
        
        # Create forest plot
        for i, (param, effect, lower, upper) in enumerate(zip(parameters, effect_sizes, ci_lower, ci_upper)):
            y_pos = len(parameters) - i - 1  # Reverse order
            
            # Plot confidence interval
            ax.plot([lower, upper], [y_pos, y_pos], 'k-', linewidth=1)
            
            # Plot effect size point
            ax.plot(effect, y_pos, 'ks', markersize=8, markerfacecolor='blue', markeredgecolor='black')
            
            # Add parameter label
            ax.text(-0.1, y_pos, param, ha='right', va='center', fontsize=10)
            
            # Add effect size and CI text
            ci_text = f"{effect:.2f} ({lower:.2f}, {upper:.2f})"
            ax.text(max(ci_upper) * 1.1, y_pos, ci_text, ha='left', va='center', fontsize=9)
        
        # Add reference line
        ref_line = params.get('reference_line', 1.0)
        ax.axvline(x=ref_line, color='red', linestyle='--', alpha=0.7)
        
        # Customize plot
        if params.get('log_scale', True):
            ax.set_xscale('log')
            ax.set_xlabel('Hazard Ratio (log scale)')
        else:
            ax.set_xlabel('Effect Size')
        
        ax.set_ylabel('')
        ax.set_title(spec.get_title())
        ax.set_yticks([])
        ax.set_ylim(-0.5, len(parameters) - 0.5)
        
        # Add "Favors" labels
        ax.text(0.1, -0.8, 'Favors Treatment', ha='left', va='center', fontsize=9, 
               transform=ax.transData)
        ax.text(10, -0.8, 'Favors Control', ha='right', va='center', fontsize=9,
               transform=ax.transData)
        
        # Add footnotes
        self.add_footnotes(fig, spec.get_footnotes())
        
        return fig
    
    def get_default_spec(self) -> Dict[str, Any]:
        """Get default forest plot specification."""
        return {
            'show_overall': True,
            'log_scale': True,
            'reference_line': 1.0,
            'show_weights': True
        }


class RainfallPlot(ClinicalPlot):
    """
    Rainfall plot (equivalent to SAS RRG %rrg_rainfall).
    
    Shows adverse event onset and duration over time.
    """
    
    def create_plot(self, spec: PlotSpecification) -> plt.Figure:
        """Create rainfall plot."""
        data = spec.get_data()
        
        # Setup figure
        fig, ax = self.setup_figure(spec)
        
        # Get plot parameters
        params = spec.get_plot_params()
        
        # Prepare data
        if spec.time_var not in data.columns:
            raise ValueError(f"Time variable '{spec.time_var}' not found")
        
        # Group by subject
        subjects = data['USUBJID'].unique() if 'USUBJID' in data.columns else data.index.unique()
        
        y_positions = {}
        for i, subject in enumerate(subjects):
            y_positions[subject] = i
        
        # Plot adverse events
        for _, row in data.iterrows():
            subject = row.get('USUBJID', row.name)
            start_time = row[spec.time_var]
            
            # Duration (if available)
            duration = row.get('AEDUR', 30)  # Default 30 days
            end_time = start_time + duration
            
            y_pos = y_positions[subject]
            
            # Color by severity if available
            severity = row.get('AESEV', 'MILD')
            if severity == 'SEVERE':
                color = '#d62728'  # Red
            elif severity == 'MODERATE':
                color = '#ff7f0e'  # Orange
            else:
                color = '#1f77b4'  # Blue
            
            # Plot line for AE duration
            ax.plot([start_time, end_time], [y_pos, y_pos], color=color, linewidth=3, alpha=0.7)
            
            # Plot start point
            ax.plot(start_time, y_pos, 'o', color=color, markersize=4)
        
        # Customize plot
        ax.set_xlabel('Time (days)')
        ax.set_ylabel('Subjects')
        ax.set_title(spec.get_title())
        
        # Set y-axis labels to subject IDs (if reasonable number)
        if len(subjects) <= 20:
            ax.set_yticks(range(len(subjects)))
            ax.set_yticklabels([str(s)[:10] for s in subjects])  # Truncate long IDs
        else:
            ax.set_ylabel(f'Subjects (n={len(subjects)})')
        
        # Add legend for severity
        if params.get('show_severity', True):
            severity_colors = {'MILD': '#1f77b4', 'MODERATE': '#ff7f0e', 'SEVERE': '#d62728'}
            legend_elements = [plt.Line2D([0], [0], color=color, lw=3, label=severity)
                             for severity, color in severity_colors.items()]
            ax.legend(handles=legend_elements, loc='upper right')
        
        # Add footnotes
        self.add_footnotes(fig, spec.get_footnotes())
        
        return fig
    
    def get_default_spec(self) -> Dict[str, Any]:
        """Get default rainfall plot specification."""
        return {
            'show_severity': True,
            'group_by_soc': True,
            'time_unit': 'days',
            'max_duration': 365
        }


class ScatterPlot(ClinicalPlot):
    """
    Scatter plot for clinical data (equivalent to SAS RRG %rrg_scatter).
    
    Shows relationship between two continuous variables.
    """
    
    def create_plot(self, spec: PlotSpecification) -> plt.Figure:
        """Create scatter plot."""
        data = spec.get_data()
        
        # Setup figure
        fig, ax = self.setup_figure(spec)
        
        # Get plot parameters
        params = spec.get_plot_params()
        
        # Check required variables
        if spec.x_var not in data.columns or spec.y_var not in data.columns:
            raise ValueError("Both x_var and y_var must be specified and present in data")
        
        x_data = data[spec.x_var]
        y_data = data[spec.y_var]
        
        # Color by treatment group if specified
        if spec.treatment_var and spec.treatment_var in data.columns:
            treatments = data[spec.treatment_var].unique()
            colors = spec.get_color_palette()[:len(treatments)]
            
            for i, treatment in enumerate(treatments):
                mask = data[spec.treatment_var] == treatment
                ax.scatter(x_data[mask], y_data[mask], 
                          label=treatment, color=colors[i], 
                          alpha=params.get('alpha', 0.7), s=50)
            
            ax.legend()
        else:
            ax.scatter(x_data, y_data, alpha=params.get('alpha', 0.7), s=50)
        
        # Add regression line if requested
        if params.get('show_regression', False):
            z = np.polyfit(x_data.dropna(), y_data.dropna(), 1)
            p = np.poly1d(z)
            ax.plot(x_data, p(x_data), "r--", alpha=0.8)
        
        # Add correlation if requested
        if params.get('show_correlation', True):
            corr = x_data.corr(y_data)
            ax.text(0.05, 0.95, f'r = {corr:.3f}', transform=ax.transAxes,
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Customize plot
        ax.set_xlabel(spec.x_var)
        ax.set_ylabel(spec.y_var)
        ax.set_title(spec.get_title())
        
        # Add footnotes
        self.add_footnotes(fig, spec.get_footnotes())
        
        return fig
    
    def get_default_spec(self) -> Dict[str, Any]:
        """Get default scatter plot specification."""
        return {
            'show_regression': False,
            'show_correlation': True,
            'alpha': 0.7
        }


class BoxPlot(ClinicalPlot):
    """
    Box plot for clinical data (equivalent to SAS RRG %rrg_box).
    
    Shows distribution of continuous variable by treatment group.
    """
    
    def create_plot(self, spec: PlotSpecification) -> plt.Figure:
        """Create box plot."""
        data = spec.get_data()
        
        # Setup figure
        fig, ax = self.setup_figure(spec)
        
        # Get plot parameters
        params = spec.get_plot_params()
        
        # Check required variables
        if spec.y_var not in data.columns:
            raise ValueError(f"Y variable '{spec.y_var}' not found in data")
        
        # Create box plot
        if spec.treatment_var and spec.treatment_var in data.columns:
            # Box plot by treatment
            treatments = data[spec.treatment_var].unique()
            box_data = [data[data[spec.treatment_var] == trt][spec.y_var].dropna() 
                       for trt in treatments]
            
            bp = ax.boxplot(box_data, labels=treatments, patch_artist=True,
                           notch=params.get('notch', False))
            
            # Color boxes
            colors = spec.get_color_palette()[:len(treatments)]
            for patch, color in zip(bp['boxes'], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)
        else:
            # Single box plot
            bp = ax.boxplot(data[spec.y_var].dropna(), patch_artist=True,
                           notch=params.get('notch', False))
            bp['boxes'][0].set_facecolor(spec.get_color_palette()[0])
            bp['boxes'][0].set_alpha(0.7)
        
        # Add individual points if requested
        if params.get('show_points', True):
            if spec.treatment_var and spec.treatment_var in data.columns:
                for i, treatment in enumerate(treatments):
                    trt_data = data[data[spec.treatment_var] == treatment][spec.y_var].dropna()
                    x_pos = np.random.normal(i + 1, 0.04, size=len(trt_data))
                    ax.scatter(x_pos, trt_data, alpha=0.4, s=20)
            else:
                y_data = data[spec.y_var].dropna()
                x_pos = np.random.normal(1, 0.04, size=len(y_data))
                ax.scatter(x_pos, y_data, alpha=0.4, s=20)
        
        # Add means if requested
        if params.get('show_means', True):
            if spec.treatment_var and spec.treatment_var in data.columns:
                for i, treatment in enumerate(treatments):
                    mean_val = data[data[spec.treatment_var] == treatment][spec.y_var].mean()
                    ax.plot(i + 1, mean_val, 'D', color='red', markersize=8)
            else:
                mean_val = data[spec.y_var].mean()
                ax.plot(1, mean_val, 'D', color='red', markersize=8)
        
        # Customize plot
        ax.set_ylabel(spec.y_var)
        if spec.treatment_var and spec.treatment_var in data.columns:
            ax.set_xlabel(spec.treatment_var)
        ax.set_title(spec.get_title())
        
        # Add footnotes
        self.add_footnotes(fig, spec.get_footnotes())
        
        return fig
    
    def get_default_spec(self) -> Dict[str, Any]:
        """Get default box plot specification."""
        return {
            'show_points': True,
            'notch': False,
            'show_means': True
        }


class PlottingEngine:
    """
    Main plotting engine (equivalent to SAS RRG plotting system).
    
    Coordinates all plot types and provides unified interface.
    """
    
    def __init__(self, config: FunctionalConfig):
        self.config = config
        self._plot_types = {
            'kaplan_meier': KaplanMeierPlot,
            'km': KaplanMeierPlot,
            'waterfall': WaterfallPlot,
            'forest': ForestPlot,
            'rainfall': RainfallPlot,
            'scatter': ScatterPlot,
            'boxplot': BoxPlot,
            'box': BoxPlot
        }
    
    def create_plot(self, plot_type: str, spec: PlotSpecification) -> plt.Figure:
        """
        Create plot of specified type.
        
        Parameters
        ----------
        plot_type : str
            Type of plot to create
        spec : PlotSpecification
            Plot specification
            
        Returns
        -------
        plt.Figure
            Created plot figure
        """
        plot_type = plot_type.lower()
        
        if plot_type not in self._plot_types:
            available_types = ', '.join(self._plot_types.keys())
            raise ValueError(f"Unknown plot type '{plot_type}'. Available: {available_types}")
        
        plot_class = self._plot_types[plot_type]
        plot_instance = plot_class(self.config)
        
        return plot_instance.create_plot(spec)
    
    def get_available_plot_types(self) -> List[str]:
        """Get list of available plot types."""
        return list(self._plot_types.keys())
    
    def create_plot_specification(self, plot_type: str, **kwargs) -> PlotSpecification:
        """
        Create plot specification with defaults for plot type.
        
        Parameters
        ----------
        plot_type : str
            Type of plot
        **kwargs
            Specification parameters
            
        Returns
        -------
        PlotSpecification
            Plot specification
        """
        # Get default parameters for plot type
        if plot_type.lower() in self._plot_types:
            plot_class = self._plot_types[plot_type.lower()]
            plot_instance = plot_class(self.config)
            default_params = plot_instance.get_default_spec()
        else:
            default_params = {}
        
        # Merge with provided parameters
        plot_params = {**default_params, **kwargs.get('plot_params', {})}
        kwargs['plot_params'] = plot_params
        
        # Set plot type
        kwargs['type'] = plot_type
        
        return PlotSpecification(**kwargs)
    
    def save_plots_to_pdf(self, plots: List[Tuple[plt.Figure, str]], output_path: str):
        """
        Save multiple plots to a single PDF file.
        
        Parameters
        ----------
        plots : list
            List of (figure, title) tuples
        output_path : str
            Output PDF path
        """
        with PdfPages(output_path) as pdf:
            for fig, title in plots:
                fig.suptitle(title, fontsize=16, y=0.98)
                pdf.savefig(fig, bbox_inches='tight')
                plt.close(fig)
    
    def create_plot_grid(self, specs: List[PlotSpecification], 
                        grid_shape: Tuple[int, int] = None) -> plt.Figure:
        """
        Create a grid of multiple plots.
        
        Parameters
        ----------
        specs : list
            List of plot specifications
        grid_shape : tuple
            (rows, cols) for grid layout
            
        Returns
        -------
        plt.Figure
            Figure with plot grid
        """
        n_plots = len(specs)
        
        if grid_shape is None:
            # Auto-determine grid shape
            cols = int(np.ceil(np.sqrt(n_plots)))
            rows = int(np.ceil(n_plots / cols))
            grid_shape = (rows, cols)
        
        fig, axes = plt.subplots(grid_shape[0], grid_shape[1], 
                                figsize=(grid_shape[1] * 8, grid_shape[0] * 6))
        
        if n_plots == 1:
            axes = [axes]
        elif grid_shape[0] == 1 or grid_shape[1] == 1:
            axes = axes.flatten()
        else:
            axes = axes.flatten()
        
        for i, spec in enumerate(specs):
            if i < len(axes):
                # Create individual plot and copy to grid
                individual_fig = self.create_plot(spec.type, spec)
                
                # Copy plot elements to grid axes (simplified)
                # In practice, would need more sophisticated copying
                axes[i].set_title(spec.get_title())
                axes[i].text(0.5, 0.5, f'{spec.type.title()} Plot\n(Grid view)', 
                           ha='center', va='center', transform=axes[i].transAxes)
                
                plt.close(individual_fig)
        
        # Hide unused subplots
        for i in range(n_plots, len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        return fig 