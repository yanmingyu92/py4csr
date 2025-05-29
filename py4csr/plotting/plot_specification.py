"""
Plot specification for py4csr functional plotting system.

This module defines the PlotSpecification class that holds all parameters
needed to generate clinical plots.
"""

from typing import Dict, List, Optional, Any, Union
import pandas as pd
from dataclasses import dataclass, field


@dataclass
class PlotSpecification:
    """
    Specification for plot generation.
    
    This class holds all parameters needed to generate a specific plot,
    including data filters, styling options, and plot-specific parameters.
    """
    
    # Core identification
    type: str
    title: str = ""
    subtitle: str = ""
    
    # Data specification
    datasets: Dict[str, pd.DataFrame] = field(default_factory=dict)
    population: str = "safety"
    population_filters: Dict[str, str] = field(default_factory=dict)
    additional_filters: List[str] = field(default_factory=list)
    
    # Variables
    x_var: Optional[str] = None
    y_var: Optional[str] = None
    group_var: Optional[str] = None
    time_var: Optional[str] = None
    event_var: Optional[str] = None
    treatment_var: str = "TRT01P"
    
    # Plot styling
    width: float = 10.0
    height: float = 8.0
    dpi: int = 300
    style: str = "clinical"
    color_palette: Optional[List[str]] = None
    
    # Plot-specific parameters
    plot_params: Dict[str, Any] = field(default_factory=dict)
    
    # Output options
    footnotes: List[str] = field(default_factory=list)
    source: str = ""
    output_formats: List[str] = field(default_factory=lambda: ["png", "pdf"])
    
    # Configuration
    config: Optional[Any] = None
    
    def get_data(self, dataset_name: str = None) -> pd.DataFrame:
        """
        Get filtered data for plot generation.
        
        Parameters
        ----------
        dataset_name : str, optional
            Name of dataset to retrieve. If None, returns primary dataset.
            
        Returns
        -------
        pd.DataFrame
            Filtered dataset
        """
        if dataset_name is None:
            # Return first available dataset
            if not self.datasets:
                raise ValueError("No datasets available")
            dataset_name = list(self.datasets.keys())[0]
        
        if dataset_name not in self.datasets:
            raise ValueError(f"Dataset '{dataset_name}' not found")
        
        data = self.datasets[dataset_name].copy()
        
        # Apply population filter
        if self.population in self.population_filters:
            pop_filter = self.population_filters[self.population]
            data = data.query(pop_filter)
        
        # Apply additional filters
        for filter_expr in self.additional_filters:
            data = data.query(filter_expr)
        
        return data
    
    def get_title(self) -> str:
        """Get plot title."""
        if self.title:
            return self.title
        return self.get_default_title()
    
    def get_subtitle(self) -> str:
        """Get plot subtitle."""
        if self.subtitle:
            return self.subtitle
        return self.get_default_subtitle()
    
    def get_default_title(self) -> str:
        """Get default title based on plot type."""
        titles = {
            'kaplan_meier': 'Kaplan-Meier Survival Curve',
            'waterfall': 'Waterfall Plot of Best Overall Response',
            'forest': 'Forest Plot of Treatment Effects',
            'rainfall': 'Rainfall Plot of Adverse Events',
            'scatter': 'Scatter Plot',
            'boxplot': 'Box Plot by Treatment Group'
        }
        return titles.get(self.type, f'{self.type.title()} Plot')
    
    def get_default_subtitle(self) -> str:
        """Get default subtitle based on population."""
        population_labels = {
            'safety': 'Safety Analysis Population',
            'efficacy': 'Efficacy Analysis Population',
            'itt': 'Intent-to-Treat Population',
            'pp': 'Per-Protocol Population'
        }
        return population_labels.get(self.population, f'{self.population.title()} Population')
    
    def get_footnotes(self) -> List[str]:
        """Get plot footnotes."""
        footnotes = self.footnotes.copy()
        
        # Add default footnotes based on plot type
        default_footnotes = self.get_default_footnotes()
        footnotes.extend(default_footnotes)
        
        return footnotes
    
    def get_default_footnotes(self) -> List[str]:
        """Get default footnotes based on plot type."""
        footnotes = {
            'kaplan_meier': [
                'Kaplan-Meier estimates with 95% confidence intervals',
                'Log-rank test p-value shown'
            ],
            'waterfall': [
                'Best percentage change from baseline',
                'Bars represent individual subjects'
            ],
            'forest': [
                'Hazard ratios with 95% confidence intervals',
                'Favors treatment if HR < 1'
            ],
            'rainfall': [
                'Each line represents one subject',
                'AE onset time and duration shown'
            ]
        }
        return footnotes.get(self.type, [])
    
    def get_color_palette(self) -> List[str]:
        """Get color palette for the plot."""
        if self.color_palette:
            return self.color_palette
        
        # Default clinical color palettes
        palettes = {
            'clinical': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'],
            'colorblind': ['#0173b2', '#de8f05', '#029e73', '#cc78bc', '#ca9161', '#fbafe4'],
            'grayscale': ['#000000', '#404040', '#808080', '#c0c0c0', '#e0e0e0', '#f0f0f0']
        }
        
        return palettes.get(self.style, palettes['clinical'])
    
    def get_plot_params(self) -> Dict[str, Any]:
        """Get plot-specific parameters with defaults."""
        params = self.plot_params.copy()
        
        # Add default parameters based on plot type
        defaults = self.get_default_plot_params()
        for key, value in defaults.items():
            if key not in params:
                params[key] = value
        
        return params
    
    def get_default_plot_params(self) -> Dict[str, Any]:
        """Get default plot parameters based on plot type."""
        defaults = {
            'kaplan_meier': {
                'confidence_interval': True,
                'risk_table': True,
                'p_value': True,
                'median_survival': True
            },
            'waterfall': {
                'sort_by': 'response',
                'show_reference_line': True,
                'reference_values': [-30, 20],
                'response_colors': True
            },
            'forest': {
                'show_overall': True,
                'log_scale': True,
                'reference_line': 1.0,
                'show_weights': True
            },
            'rainfall': {
                'show_severity': True,
                'group_by_soc': True,
                'time_unit': 'days',
                'max_duration': 365
            },
            'scatter': {
                'show_regression': False,
                'show_correlation': True,
                'alpha': 0.7
            },
            'boxplot': {
                'show_points': True,
                'notch': False,
                'show_means': True
            }
        }
        return defaults.get(self.type, {}) 