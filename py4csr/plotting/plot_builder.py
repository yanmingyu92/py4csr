"""
Plot builder for py4csr functional plotting system.

This module provides the PlotBuilder class that enables functional composition
for generating clinical plots, following the same pattern as ReportBuilder.
"""

from typing import Dict, List, Optional, Any, Union
import pandas as pd
from pathlib import Path
from datetime import datetime

from .plot_specification import PlotSpecification
from .plot_result import PlotResult, PlotCollection
from .generators.factory import PlotGeneratorFactory


class PlotBuilder:
    """
    Functional plot builder for clinical visualizations.
    
    This class provides a fluent interface for generating clinical plots
    using method chaining, similar to the SAS RRG approach.
    """
    
    def __init__(self, config: Optional[Any] = None):
        """
        Initialize plot builder.
        
        Parameters
        ----------
        config : ReportConfig, optional
            Configuration object for plot styling and defaults
        """
        self.config = config
        self.datasets = {}
        self.population_filters = {}
        self.treatment_config = {}
        self.plots = PlotCollection()
        self.study_info = {}
        
    def init_study(self, uri: str, title: str = "", **kwargs) -> 'PlotBuilder':
        """
        Initialize study information.
        
        Parameters
        ----------
        uri : str
            Study identifier
        title : str, optional
            Study title
        **kwargs
            Additional study metadata
            
        Returns
        -------
        PlotBuilder
            Self for method chaining
        """
        self.study_info = {
            'uri': uri,
            'title': title,
            'creation_time': datetime.now(),
            **kwargs
        }
        return self
    
    def add_dataset(self, data: pd.DataFrame, name: str, type: str = "analysis") -> 'PlotBuilder':
        """
        Add dataset for plotting.
        
        Parameters
        ----------
        data : pd.DataFrame
            Dataset to add
        name : str
            Dataset name
        type : str, optional
            Dataset type
            
        Returns
        -------
        PlotBuilder
            Self for method chaining
        """
        self.datasets[name] = {
            'data': data.copy(),
            'type': type,
            'added_time': datetime.now()
        }
        return self
    
    def define_populations(self, **populations) -> 'PlotBuilder':
        """
        Define analysis populations.
        
        Parameters
        ----------
        **populations
            Population definitions as keyword arguments
            
        Returns
        -------
        PlotBuilder
            Self for method chaining
        """
        self.population_filters.update(populations)
        return self
    
    def define_treatments(self, var: str, decode: str = None, **kwargs) -> 'PlotBuilder':
        """
        Define treatment variable configuration.
        
        Parameters
        ----------
        var : str
            Treatment variable name
        decode : str, optional
            Treatment decode variable
        **kwargs
            Additional treatment configuration
            
        Returns
        -------
        PlotBuilder
            Self for method chaining
        """
        self.treatment_config = {
            'var': var,
            'decode': decode or var,
            **kwargs
        }
        return self
    
    def add_kaplan_meier_plot(self, 
                             title: str = "",
                             subtitle: str = "",
                             time_var: str = None,
                             event_var: str = None,
                             population: str = "safety",
                             **kwargs) -> 'PlotBuilder':
        """
        Add Kaplan-Meier survival plot.
        
        Parameters
        ----------
        title : str, optional
            Plot title
        subtitle : str, optional
            Plot subtitle
        time_var : str, optional
            Time-to-event variable
        event_var : str, optional
            Event indicator variable
        population : str, optional
            Analysis population
        **kwargs
            Additional plot parameters
            
        Returns
        -------
        PlotBuilder
            Self for method chaining
        """
        spec = PlotSpecification(
            type='kaplan_meier',
            title=title,
            subtitle=subtitle,
            datasets=self._get_datasets(),
            population=population,
            population_filters=self.population_filters,
            time_var=time_var,
            event_var=event_var,
            treatment_var=self.treatment_config.get('var', 'TRT01P'),
            plot_params=kwargs,
            config=self.config
        )
        
        # Generate plot
        generator = PlotGeneratorFactory.create('kaplan_meier')
        result = generator.generate(spec)
        
        # Add to collection
        plot_name = f"kaplan_meier_{len(self.plots.plots) + 1}"
        self.plots.add_plot(plot_name, result)
        
        return self
    
    def add_waterfall_plot(self,
                          title: str = "",
                          subtitle: str = "",
                          y_var: str = None,
                          population: str = "efficacy",
                          **kwargs) -> 'PlotBuilder':
        """
        Add waterfall plot.
        
        Parameters
        ----------
        title : str, optional
            Plot title
        subtitle : str, optional
            Plot subtitle
        y_var : str, optional
            Response variable
        population : str, optional
            Analysis population
        **kwargs
            Additional plot parameters
            
        Returns
        -------
        PlotBuilder
            Self for method chaining
        """
        spec = PlotSpecification(
            type='waterfall',
            title=title,
            subtitle=subtitle,
            datasets=self._get_datasets(),
            population=population,
            population_filters=self.population_filters,
            y_var=y_var,
            treatment_var=self.treatment_config.get('var', 'TRT01P'),
            plot_params=kwargs,
            config=self.config
        )
        
        # Generate plot
        generator = PlotGeneratorFactory.create('waterfall')
        result = generator.generate(spec)
        
        # Add to collection
        plot_name = f"waterfall_{len(self.plots.plots) + 1}"
        self.plots.add_plot(plot_name, result)
        
        return self
    
    def add_forest_plot(self,
                       title: str = "",
                       subtitle: str = "",
                       population: str = "efficacy",
                       **kwargs) -> 'PlotBuilder':
        """
        Add forest plot.
        
        Parameters
        ----------
        title : str, optional
            Plot title
        subtitle : str, optional
            Plot subtitle
        population : str, optional
            Analysis population
        **kwargs
            Additional plot parameters
            
        Returns
        -------
        PlotBuilder
            Self for method chaining
        """
        spec = PlotSpecification(
            type='forest',
            title=title,
            subtitle=subtitle,
            datasets=self._get_datasets(),
            population=population,
            population_filters=self.population_filters,
            treatment_var=self.treatment_config.get('var', 'TRT01P'),
            plot_params=kwargs,
            config=self.config
        )
        
        # Generate plot
        generator = PlotGeneratorFactory.create('forest')
        result = generator.generate(spec)
        
        # Add to collection
        plot_name = f"forest_{len(self.plots.plots) + 1}"
        self.plots.add_plot(plot_name, result)
        
        return self
    
    def add_rainfall_plot(self,
                         title: str = "",
                         subtitle: str = "",
                         time_var: str = None,
                         population: str = "safety",
                         **kwargs) -> 'PlotBuilder':
        """
        Add rainfall plot.
        
        Parameters
        ----------
        title : str, optional
            Plot title
        subtitle : str, optional
            Plot subtitle
        time_var : str, optional
            Time variable for AE onset
        population : str, optional
            Analysis population
        **kwargs
            Additional plot parameters
            
        Returns
        -------
        PlotBuilder
            Self for method chaining
        """
        spec = PlotSpecification(
            type='rainfall',
            title=title,
            subtitle=subtitle,
            datasets=self._get_datasets(),
            population=population,
            population_filters=self.population_filters,
            time_var=time_var,
            treatment_var=self.treatment_config.get('var', 'TRT01P'),
            plot_params=kwargs,
            config=self.config
        )
        
        # Generate plot
        generator = PlotGeneratorFactory.create('rainfall')
        result = generator.generate(spec)
        
        # Add to collection
        plot_name = f"rainfall_{len(self.plots.plots) + 1}"
        self.plots.add_plot(plot_name, result)
        
        return self
    
    def add_scatter_plot(self,
                        title: str = "",
                        subtitle: str = "",
                        x_var: str = None,
                        y_var: str = None,
                        population: str = "safety",
                        **kwargs) -> 'PlotBuilder':
        """
        Add scatter plot.
        
        Parameters
        ----------
        title : str, optional
            Plot title
        subtitle : str, optional
            Plot subtitle
        x_var : str, optional
            X-axis variable
        y_var : str, optional
            Y-axis variable
        population : str, optional
            Analysis population
        **kwargs
            Additional plot parameters
            
        Returns
        -------
        PlotBuilder
            Self for method chaining
        """
        spec = PlotSpecification(
            type='scatter',
            title=title,
            subtitle=subtitle,
            datasets=self._get_datasets(),
            population=population,
            population_filters=self.population_filters,
            x_var=x_var,
            y_var=y_var,
            treatment_var=self.treatment_config.get('var', 'TRT01P'),
            plot_params=kwargs,
            config=self.config
        )
        
        # Generate plot
        generator = PlotGeneratorFactory.create('scatter')
        result = generator.generate(spec)
        
        # Add to collection
        plot_name = f"scatter_{len(self.plots.plots) + 1}"
        self.plots.add_plot(plot_name, result)
        
        return self
    
    def add_boxplot(self,
                   title: str = "",
                   subtitle: str = "",
                   y_var: str = None,
                   group_var: str = None,
                   population: str = "safety",
                   **kwargs) -> 'PlotBuilder':
        """
        Add box plot.
        
        Parameters
        ----------
        title : str, optional
            Plot title
        subtitle : str, optional
            Plot subtitle
        y_var : str, optional
            Y-axis variable
        group_var : str, optional
            Grouping variable
        population : str, optional
            Analysis population
        **kwargs
            Additional plot parameters
            
        Returns
        -------
        PlotBuilder
            Self for method chaining
        """
        if group_var is None:
            group_var = self.treatment_config.get('var', 'TRT01P')
        
        spec = PlotSpecification(
            type='boxplot',
            title=title,
            subtitle=subtitle,
            datasets=self._get_datasets(),
            population=population,
            population_filters=self.population_filters,
            y_var=y_var,
            group_var=group_var,
            treatment_var=self.treatment_config.get('var', 'TRT01P'),
            plot_params=kwargs,
            config=self.config
        )
        
        # Generate plot
        generator = PlotGeneratorFactory.create('boxplot')
        result = generator.generate(spec)
        
        # Add to collection
        plot_name = f"boxplot_{len(self.plots.plots) + 1}"
        self.plots.add_plot(plot_name, result)
        
        return self
    
    def save_all(self, output_dir: Union[str, Path], 
                formats: Optional[List[str]] = None) -> 'PlotBuilder':
        """
        Save all plots to directory.
        
        Parameters
        ----------
        output_dir : str or Path
            Output directory
        formats : list, optional
            Output formats (default: ['png', 'pdf'])
            
        Returns
        -------
        PlotBuilder
            Self for method chaining
        """
        if formats is None:
            formats = ['png', 'pdf']
        
        self.plots.save_all(output_dir, formats)
        return self
    
    def finalize(self) -> PlotCollection:
        """
        Finalize plot generation and return collection.
        
        Returns
        -------
        PlotCollection
            Collection of generated plots
        """
        # Update metadata
        self.plots.metadata.update({
            'study_info': self.study_info,
            'finalization_time': datetime.now()
        })
        
        return self.plots
    
    def _get_datasets(self) -> Dict[str, pd.DataFrame]:
        """Get datasets as dictionary of DataFrames."""
        return {name: info['data'] for name, info in self.datasets.items()}
    
    def print_summary(self):
        """Print summary of generated plots."""
        print(f"Plot Builder Summary:")
        print(f"Study: {self.study_info.get('uri', 'Unknown')}")
        print(f"Total Plots: {len(self.plots.plots)}")
        
        for name, plot_result in self.plots.plots.items():
            plot_type = plot_result.metadata.get('plot_type', 'Unknown')
            print(f"  {name}: {plot_type}")
    
    def get_plot_summary(self) -> Dict[str, Any]:
        """Get summary of all plots."""
        return self.plots.get_summary() 