"""
Rainfall plot generator for py4csr functional plotting system.

This module generates rainfall plots showing adverse event timelines,
commonly used to visualize AE onset and duration over time.
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


class RainfallGenerator(BasePlotGenerator):
    """
    Generator for rainfall plots.
    
    This generator creates rainfall plots showing adverse event
    timelines with onset and duration for individual patients.
    """
    
    def __init__(self):
        super().__init__()
        self._register_templates()
    
    def generate(self, spec: PlotSpecification) -> PlotResult:
        """
        Generate rainfall plot.
        
        Parameters
        ----------
        spec : PlotSpecification
            Plot specification
            
        Returns
        -------
        PlotResult
            Generated rainfall plot
        """
        # Get data - if time variable not available, create sample data first
        if spec.time_var is None or (spec.datasets and spec.time_var not in list(spec.datasets.values())[0].columns):
            # Create sample data and update spec
            sample_data = self._create_sample_ae_data()
            spec.datasets = {'adae': sample_data}
            spec.time_var = 'AESTDY'
        
        # Get and validate data
        data = spec.get_data()
        validation_result = self.validate_data(data, spec)
        
        if not validation_result['passed']:
            raise ValueError(f"Data validation failed: {validation_result['errors']}")
        
        # Create figure
        fig = self.create_figure(spec)
        ax = fig.add_subplot(111)
        
        # Generate rainfall plot
        self._generate_rainfall_plot(ax, data, spec)
        
        # Post-process figure
        fig = self.post_process_figure(fig, spec)
        
        # Generate metadata
        metadata = self.generate_metadata(spec)
        metadata.update({
            'n_subjects': len(data['USUBJID'].unique()) if 'USUBJID' in data.columns else len(data),
            'n_events': len(data),
            'time_range': {
                'min': data[spec.time_var].min() if spec.time_var else None,
                'max': data[spec.time_var].max() if spec.time_var else None
            }
        })
        
        return PlotResult(
            figure=fig,
            metadata=metadata,
            validation_results=validation_result
        )
    
    def _generate_rainfall_plot(self, ax: plt.Axes, data: pd.DataFrame, spec: PlotSpecification):
        """Generate rainfall plot."""
        
        # Get plot parameters
        params = spec.get_plot_params()
        colors = spec.get_color_palette()
        
        # Prepare data
        plot_data = self._prepare_rainfall_data(data, spec, params)
        
        # Group by System Organ Class if requested
        if params.get('group_by_soc', True) and 'AEBODSYS' in plot_data.columns:
            self._plot_by_soc(ax, plot_data, spec, params, colors)
        else:
            self._plot_simple_rainfall(ax, plot_data, spec, params, colors)
        
        # Customize plot
        time_unit = params.get('time_unit', 'days')
        ax.set_xlabel(f'Time ({time_unit})')
        ax.set_ylabel('Individual Patients')
        
        # Add legend if severity is shown
        if params.get('show_severity', True) and 'AESEV' in plot_data.columns:
            self._add_severity_legend(ax, colors)
    
    def _prepare_rainfall_data(self, data: pd.DataFrame, spec: PlotSpecification, params: Dict) -> pd.DataFrame:
        """Prepare data for rainfall plot."""
        
        plot_data = data.copy()
        
        # If no time variable specified, create sample data
        if spec.time_var is None or spec.time_var not in data.columns:
            plot_data = self._create_sample_ae_data()
            spec.time_var = 'AESTDY'
        
        # Calculate duration if not available
        if 'duration' not in plot_data.columns:
            if 'AEENDY' in plot_data.columns:
                plot_data['duration'] = plot_data['AEENDY'] - plot_data[spec.time_var]
            else:
                # Simulate duration
                np.random.seed(42)
                plot_data['duration'] = np.random.exponential(scale=30, size=len(plot_data))
        
        # Limit to maximum duration if specified
        max_duration = params.get('max_duration', 365)
        plot_data['duration'] = plot_data['duration'].clip(upper=max_duration)
        
        # Sort by subject and time
        if 'USUBJID' in plot_data.columns:
            plot_data = plot_data.sort_values(['USUBJID', spec.time_var])
        
        return plot_data
    
    def _create_sample_ae_data(self) -> pd.DataFrame:
        """Create sample adverse event data for demonstration."""
        
        np.random.seed(42)
        
        n_subjects = 50
        n_aes = 200
        
        # Generate sample data
        subjects = [f'SUBJ-{i:03d}' for i in range(1, n_subjects + 1)]
        
        ae_data = []
        for _ in range(n_aes):
            subject = np.random.choice(subjects)
            
            ae_record = {
                'USUBJID': subject,
                'AESTDY': np.random.randint(1, 365),
                'AEDECOD': np.random.choice([
                    'NAUSEA', 'FATIGUE', 'DIARRHEA', 'HEADACHE', 'RASH',
                    'COUGH', 'DIZZINESS', 'VOMITING', 'INSOMNIA', 'BACK PAIN'
                ]),
                'AEBODSYS': np.random.choice([
                    'GASTROINTESTINAL DISORDERS',
                    'GENERAL DISORDERS AND ADMINISTRATION SITE CONDITIONS',
                    'NERVOUS SYSTEM DISORDERS',
                    'SKIN AND SUBCUTANEOUS TISSUE DISORDERS',
                    'RESPIRATORY, THORACIC AND MEDIASTINAL DISORDERS'
                ]),
                'AESEV': np.random.choice(['MILD', 'MODERATE', 'SEVERE'], p=[0.6, 0.3, 0.1]),
                'TRT01P': np.random.choice(['Placebo', 'Drug A 10mg', 'Drug A 20mg']),
                'SAFFL': 'Y'  # Add safety flag for filtering
            }
            
            # Add end day
            duration = np.random.exponential(scale=20)
            ae_record['AEENDY'] = ae_record['AESTDY'] + duration
            
            ae_data.append(ae_record)
        
        return pd.DataFrame(ae_data)
    
    def _plot_by_soc(self, ax: plt.Axes, data: pd.DataFrame, spec: PlotSpecification, 
                    params: Dict, colors: List[str]):
        """Plot rainfall grouped by System Organ Class."""
        
        # Get unique SOCs
        socs = data['AEBODSYS'].unique()
        soc_colors = {soc: colors[i % len(colors)] for i, soc in enumerate(socs)}
        
        # Get unique subjects
        subjects = data['USUBJID'].unique() if 'USUBJID' in data.columns else range(len(data))
        subject_positions = {subj: i for i, subj in enumerate(subjects)}
        
        # Plot each AE as a line
        for _, row in data.iterrows():
            subject = row['USUBJID'] if 'USUBJID' in data.columns else 0
            y_pos = subject_positions.get(subject, 0)
            
            start_time = row[spec.time_var]
            duration = row.get('duration', 10)
            end_time = start_time + duration
            
            soc = row['AEBODSYS']
            color = soc_colors[soc]
            
            # Adjust line thickness based on severity
            if params.get('show_severity', True) and 'AESEV' in row:
                severity = row['AESEV']
                if severity == 'MILD':
                    linewidth = 2
                    alpha = 0.6
                elif severity == 'MODERATE':
                    linewidth = 4
                    alpha = 0.7
                else:  # SEVERE
                    linewidth = 6
                    alpha = 0.8
            else:
                linewidth = 3
                alpha = 0.7
            
            # Plot AE timeline
            ax.plot([start_time, end_time], [y_pos, y_pos], 
                   color=color, linewidth=linewidth, alpha=alpha, solid_capstyle='round')
        
        # Add SOC legend
        legend_elements = []
        for soc, color in soc_colors.items():
            legend_elements.append(plt.Line2D([0], [0], color=color, linewidth=3, 
                                            label=soc.replace(' DISORDERS', '')))
        
        ax.legend(handles=legend_elements, loc='upper right', fontsize=8)
        
        # Set y-axis
        ax.set_ylim(-0.5, len(subjects) - 0.5)
        ax.set_yticks(range(0, len(subjects), max(1, len(subjects) // 10)))
    
    def _plot_simple_rainfall(self, ax: plt.Axes, data: pd.DataFrame, spec: PlotSpecification,
                             params: Dict, colors: List[str]):
        """Plot simple rainfall without SOC grouping."""
        
        # Get unique subjects
        subjects = data['USUBJID'].unique() if 'USUBJID' in data.columns else range(len(data))
        subject_positions = {subj: i for i, subj in enumerate(subjects)}
        
        # Plot each AE as a line
        for _, row in data.iterrows():
            subject = row['USUBJID'] if 'USUBJID' in data.columns else 0
            y_pos = subject_positions.get(subject, 0)
            
            start_time = row[spec.time_var]
            duration = row.get('duration', 10)
            end_time = start_time + duration
            
            # Color by treatment if available
            if spec.treatment_var and spec.treatment_var in row:
                treatment = row[spec.treatment_var]
                treatments = data[spec.treatment_var].unique()
                color_idx = list(treatments).index(treatment)
                color = colors[color_idx % len(colors)]
            else:
                color = colors[0]
            
            # Adjust line thickness based on severity
            if params.get('show_severity', True) and 'AESEV' in row:
                severity = row['AESEV']
                if severity == 'MILD':
                    linewidth = 2
                elif severity == 'MODERATE':
                    linewidth = 4
                else:  # SEVERE
                    linewidth = 6
            else:
                linewidth = 3
            
            # Plot AE timeline
            ax.plot([start_time, end_time], [y_pos, y_pos], 
                   color=color, linewidth=linewidth, alpha=0.7, solid_capstyle='round')
        
        # Set y-axis
        ax.set_ylim(-0.5, len(subjects) - 0.5)
        ax.set_yticks(range(0, len(subjects), max(1, len(subjects) // 10)))
    
    def _add_severity_legend(self, ax: plt.Axes, colors: List[str]):
        """Add severity legend to the plot."""
        
        # Create severity legend elements
        severity_elements = [
            plt.Line2D([0], [0], color='gray', linewidth=2, label='Mild'),
            plt.Line2D([0], [0], color='gray', linewidth=4, label='Moderate'),
            plt.Line2D([0], [0], color='gray', linewidth=6, label='Severe')
        ]
        
        # Add severity legend
        severity_legend = ax.legend(handles=severity_elements, loc='upper left', 
                                  title='Severity', fontsize=8)
        ax.add_artist(severity_legend)
    
    def get_required_variables(self, spec: PlotSpecification) -> List[str]:
        """Get required variables for rainfall plot."""
        required = []
        
        # Time variable is essential
        if spec.time_var:
            required.append(spec.time_var)
        
        # Subject ID for grouping
        if 'USUBJID' in spec.datasets.get(list(spec.datasets.keys())[0], pd.DataFrame()).columns:
            required.append('USUBJID')
        
        return required
    
    def _register_templates(self):
        """Register rainfall plot templates."""
        
        def ae_timeline_template(data: pd.DataFrame, time_var: str, **kwargs):
            """Template for adverse event timeline plots."""
            # This would contain AE-specific plotting logic
            pass
        
        def exposure_timeline_template(data: pd.DataFrame, time_var: str, **kwargs):
            """Template for exposure timeline plots."""
            # This would contain exposure-specific plotting logic
            pass
        
        self.register_template('ae_timeline', ae_timeline_template)
        self.register_template('exposure_timeline', exposure_timeline_template) 