"""
Plotting module for py4csr functional reporting system.

This module provides plot generation capabilities for clinical study reports,
including survival plots, efficacy plots, and safety visualizations.
"""

from .plot_builder import PlotBuilder
from .plot_specification import PlotSpecification
from .plot_result import PlotResult
from .generators import (
    BasePlotGenerator,
    PlotGeneratorFactory,
    KaplanMeierGenerator,
    WaterfallGenerator,
    ForestGenerator,
    RainfallGenerator,
    ScatterGenerator,
    BoxplotGenerator
)

__all__ = [
    "PlotBuilder",
    "PlotSpecification", 
    "PlotResult",
    "BasePlotGenerator",
    "PlotGeneratorFactory",
    "KaplanMeierGenerator",
    "WaterfallGenerator",
    "ForestGenerator",
    "RainfallGenerator",
    "ScatterGenerator",
    "BoxplotGenerator"
] 