"""
Plot generator factory for py4csr functional plotting system.

This module provides the factory pattern for creating plot generators,
similar to the table generator factory.
"""

from typing import Dict, Type, Optional
from .base_generator import BasePlotGenerator


class PlotGeneratorFactory:
    """
    Factory for creating plot generators.
    
    This class manages the registry of available plot generators and
    creates instances on demand based on plot type.
    """
    
    _generators: Dict[str, Type[BasePlotGenerator]] = {}
    
    @classmethod
    def register(cls, plot_type: str, generator_class: Type[BasePlotGenerator]) -> None:
        """
        Register a generator class for a plot type.
        
        Parameters
        ----------
        plot_type : str
            Type of plot (e.g., 'kaplan_meier', 'waterfall')
        generator_class : type
            Generator class to register
        """
        cls._generators[plot_type] = generator_class
    
    @classmethod
    def create(cls, plot_type: str) -> BasePlotGenerator:
        """
        Create generator for specified plot type.
        
        Parameters
        ----------
        plot_type : str
            Type of plot to generate
            
        Returns
        -------
        BasePlotGenerator
            Generator instance for the plot type
            
        Raises
        ------
        ValueError
            If plot type is not registered
        """
        if plot_type not in cls._generators:
            # Try to import and register common generators
            cls._register_default_generators()
            
            if plot_type not in cls._generators:
                available_types = list(cls._generators.keys())
                raise ValueError(
                    f"Unknown plot type: '{plot_type}'. "
                    f"Available types: {available_types}"
                )
        
        generator_class = cls._generators[plot_type]
        return generator_class()
    
    @classmethod
    def list_available_types(cls) -> list:
        """
        List all available plot types.
        
        Returns
        -------
        list
            Available plot type names
        """
        cls._register_default_generators()
        return list(cls._generators.keys())
    
    @classmethod
    def is_registered(cls, plot_type: str) -> bool:
        """
        Check if a plot type is registered.
        
        Parameters
        ----------
        plot_type : str
            Plot type to check
            
        Returns
        -------
        bool
            True if registered, False otherwise
        """
        return plot_type in cls._generators
    
    @classmethod
    def _register_default_generators(cls) -> None:
        """Register default generators if not already registered."""
        if cls._generators:
            return  # Already registered
        
        try:
            # Import and register all default generators
            from .kaplan_meier_generator import KaplanMeierGenerator
            from .waterfall_generator import WaterfallGenerator
            from .forest_generator import ForestGenerator
            from .rainfall_generator import RainfallGenerator
            from .scatter_generator import ScatterGenerator
            from .boxplot_generator import BoxplotGenerator
            
            # Register all generators
            cls.register('kaplan_meier', KaplanMeierGenerator)
            cls.register('waterfall', WaterfallGenerator)
            cls.register('forest', ForestGenerator)
            cls.register('rainfall', RainfallGenerator)
            cls.register('scatter', ScatterGenerator)
            cls.register('boxplot', BoxplotGenerator)
            
        except ImportError:
            # Some generators may not be implemented yet
            # Register the ones that are available
            try:
                from .kaplan_meier_generator import KaplanMeierGenerator
                cls.register('kaplan_meier', KaplanMeierGenerator)
            except ImportError:
                pass
            
            try:
                from .waterfall_generator import WaterfallGenerator
                cls.register('waterfall', WaterfallGenerator)
            except ImportError:
                pass
            
            try:
                from .forest_generator import ForestGenerator
                cls.register('forest', ForestGenerator)
            except ImportError:
                pass
            
            try:
                from .rainfall_generator import RainfallGenerator
                cls.register('rainfall', RainfallGenerator)
            except ImportError:
                pass
            
            try:
                from .scatter_generator import ScatterGenerator
                cls.register('scatter', ScatterGenerator)
            except ImportError:
                pass
            
            try:
                from .boxplot_generator import BoxplotGenerator
                cls.register('boxplot', BoxplotGenerator)
            except ImportError:
                pass 