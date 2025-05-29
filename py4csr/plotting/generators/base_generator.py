"""
Base plot generator for py4csr functional plotting system.

This module defines the abstract base class for all plot generators,
providing the template pattern for clinical plot generation.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.figure
from datetime import datetime

from ..plot_specification import PlotSpecification
from ..plot_result import PlotResult


class BasePlotGenerator(ABC):
    """
    Abstract base class for plot generators.
    
    This class defines the interface and common functionality for all
    plot generators in the functional plotting system.
    """
    
    def __init__(self):
        """Initialize the generator."""
        self.template_registry = {}
        self.validation_rules = {}
        
    @abstractmethod
    def generate(self, spec: PlotSpecification) -> PlotResult:
        """
        Generate plot based on specification.
        
        Parameters
        ----------
        spec : PlotSpecification
            Plot specification with all parameters
            
        Returns
        -------
        PlotResult
            Generated plot result
        """
        pass
    
    def register_template(self, name: str, template: Callable):
        """
        Register a template function.
        
        Parameters
        ----------
        name : str
            Template name
        template : callable
            Template function
        """
        self.template_registry[name] = template
    
    def apply_template(self, template_name: str, data: pd.DataFrame, **kwargs) -> matplotlib.figure.Figure:
        """
        Apply a registered template to data.
        
        Parameters
        ----------
        template_name : str
            Name of template to apply
        data : pd.DataFrame
            Input data
        **kwargs
            Additional template parameters
            
        Returns
        -------
        matplotlib.figure.Figure
            Generated plot figure
        """
        if template_name not in self.template_registry:
            raise ValueError(f"Template '{template_name}' not found")
        
        template_func = self.template_registry[template_name]
        return template_func(data, **kwargs)
    
    def validate_data(self, data: pd.DataFrame, spec: PlotSpecification) -> Dict[str, Any]:
        """
        Validate input data for plot generation.
        
        Parameters
        ----------
        data : pd.DataFrame
            Input data to validate
        spec : PlotSpecification
            Plot specification
            
        Returns
        -------
        dict
            Validation results
        """
        validation_result = {
            'passed': True,
            'errors': [],
            'warnings': []
        }
        
        # Check if data is empty
        if data.empty:
            validation_result['passed'] = False
            validation_result['errors'].append("Dataset is empty")
            return validation_result
        
        # Check required variables
        required_vars = self.get_required_variables(spec)
        missing_vars = [var for var in required_vars if var not in data.columns]
        if missing_vars:
            validation_result['passed'] = False
            validation_result['errors'].append(f"Missing required variables: {missing_vars}")
        
        # Check for sufficient data
        if len(data) < 2:
            validation_result['warnings'].append("Very small dataset (n < 2)")
        
        return validation_result
    
    def get_required_variables(self, spec: PlotSpecification) -> List[str]:
        """
        Get list of required variables for this plot type.
        
        Parameters
        ----------
        spec : PlotSpecification
            Plot specification
            
        Returns
        -------
        list
            Required variable names
        """
        # Base requirements
        required = []
        
        # Add variables based on plot specification
        if spec.x_var:
            required.append(spec.x_var)
        if spec.y_var:
            required.append(spec.y_var)
        if spec.group_var:
            required.append(spec.group_var)
        if spec.time_var:
            required.append(spec.time_var)
        if spec.event_var:
            required.append(spec.event_var)
        if spec.treatment_var:
            required.append(spec.treatment_var)
        
        return list(set(required))  # Remove duplicates
    
    def create_figure(self, spec: PlotSpecification) -> matplotlib.figure.Figure:
        """
        Create matplotlib figure with specified dimensions and style.
        
        Parameters
        ----------
        spec : PlotSpecification
            Plot specification
            
        Returns
        -------
        matplotlib.figure.Figure
            Created figure
        """
        # Set style
        if spec.style == 'clinical':
            plt.style.use('seaborn-v0_8-whitegrid')
        elif spec.style == 'publication':
            plt.style.use('seaborn-v0_8-white')
        else:
            plt.style.use('default')
        
        # Create figure
        fig, ax = plt.subplots(figsize=(spec.width, spec.height), dpi=spec.dpi)
        
        return fig
    
    def apply_clinical_styling(self, fig: matplotlib.figure.Figure, spec: PlotSpecification):
        """
        Apply clinical study report styling to the figure.
        
        Parameters
        ----------
        fig : matplotlib.figure.Figure
            Figure to style
        spec : PlotSpecification
            Plot specification
        """
        # Get axes
        axes = fig.get_axes()
        if not axes:
            return
        
        ax = axes[0]
        
        # Set title and subtitle
        title = spec.get_title()
        subtitle = spec.get_subtitle()
        
        if title:
            fig.suptitle(title, fontsize=14, fontweight='bold', y=0.95)
        
        if subtitle:
            ax.set_title(subtitle, fontsize=12, pad=20)
        
        # Apply grid styling
        ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        ax.set_axisbelow(True)
        
        # Set spine styling
        for spine in ax.spines.values():
            spine.set_linewidth(0.8)
            spine.set_color('black')
        
        # Set tick parameters
        ax.tick_params(axis='both', which='major', labelsize=10)
        ax.tick_params(axis='both', which='minor', labelsize=8)
        
        # Add footnotes if specified
        footnotes = spec.get_footnotes()
        if footnotes:
            footnote_text = '\n'.join([f"• {footnote}" for footnote in footnotes])
            fig.text(0.1, 0.02, footnote_text, fontsize=8, 
                    verticalalignment='bottom', wrap=True)
        
        # Adjust layout
        plt.tight_layout()
        if footnotes:
            plt.subplots_adjust(bottom=0.15)
    
    def generate_metadata(self, spec: PlotSpecification, 
                         generation_time: datetime = None) -> Dict[str, Any]:
        """
        Generate metadata for the plot result.
        
        Parameters
        ----------
        spec : PlotSpecification
            Plot specification
        generation_time : datetime, optional
            Time of generation
            
        Returns
        -------
        dict
            Plot metadata
        """
        if generation_time is None:
            generation_time = datetime.now()
        
        return {
            'plot_type': spec.type,
            'title': spec.get_title(),
            'subtitle': spec.get_subtitle(),
            'population': spec.population,
            'treatment_variable': spec.treatment_var,
            'x_variable': spec.x_var,
            'y_variable': spec.y_var,
            'group_variable': spec.group_var,
            'time_variable': spec.time_var,
            'event_variable': spec.event_var,
            'width': spec.width,
            'height': spec.height,
            'dpi': spec.dpi,
            'style': spec.style,
            'generation_time': generation_time,
            'generator_class': self.__class__.__name__,
            'plot_params': spec.get_plot_params()
        }
    
    def post_process_figure(self, fig: matplotlib.figure.Figure, 
                           spec: PlotSpecification) -> matplotlib.figure.Figure:
        """
        Post-process the generated figure.
        
        Parameters
        ----------
        fig : matplotlib.figure.Figure
            Generated figure
        spec : PlotSpecification
            Plot specification
            
        Returns
        -------
        matplotlib.figure.Figure
            Post-processed figure
        """
        # Apply clinical styling
        self.apply_clinical_styling(fig, spec)
        
        # Set background color
        fig.patch.set_facecolor('white')
        
        return fig 