"""
py4csr.functional: Functional Programming Interface for Clinical Reporting

This module provides a functional programming approach to clinical trial data analysis
and reporting. It implements the same core patterns used in enterprise clinical reporting
systems while maintaining Python's ease of use and flexibility.

The system follows these key principles:
- Immutable data transformations
- Pure functions for statistical calculations
- Composable operations through method chaining
- Lazy evaluation for performance
- Type safety and validation

Key Components:
- ReportSession: Main orchestrator for functional composition
- FunctionalConfig: Configuration management system
- TableBuilder: Functional table construction engine
- StatisticalTemplates: Reusable statistical calculations
- OutputGenerators: Multi-format output generation

Example Usage:
    >>> from py4csr.functional import ReportSession
    >>> # Functional composition for clinical reports
    >>> session = (ReportSession()
    ...     .init_study("ABC-001", title="Phase III Study")
    ...     .load_datasets(data_path="data/")
    ...     .define_populations(safety="SAFFL=='Y'")
    ...     .add_demographics_table()
    ...     .generate_all()
    ...     .finalize())
"""

from .session import ReportSession
from .config import FunctionalConfig, StatisticDefinition, FormatDefinition, TableTemplate
from .table_builder import TableBuilder
from .statistical_templates import StatisticalTemplates
from .output_generators import RTFGenerator, HTMLGenerator, PDFGenerator

__all__ = [
    # Main classes
    'ReportSession',
    'FunctionalConfig', 
    'TableBuilder',
    'StatisticalTemplates',
    
    # Configuration
    'StatisticDefinition',
    'FormatDefinition', 
    'TableTemplate',
    
    # Output generators
    'RTFGenerator',
    'HTMLGenerator', 
    'PDFGenerator'
] 