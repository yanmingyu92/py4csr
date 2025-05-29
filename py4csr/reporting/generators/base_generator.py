"""
Base table generator for py4csr functional reporting system.

This module defines the abstract base class for all table generators,
providing the template pattern for statistical table generation.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
import pandas as pd
from datetime import datetime

from ..table_specification import TableSpecification
from ..table_result import TableResult
from ..rtf_table import RTFTable


class BaseTableGenerator(ABC):
    """
    Abstract base class for table generators.
    
    This class defines the interface and common functionality for all
    table generators in the functional reporting system.
    """
    
    def __init__(self):
        """Initialize the generator."""
        self.template_registry = {}
        self.validation_rules = {}
        
    @abstractmethod
    def generate(self, spec: TableSpecification) -> TableResult:
        """
        Generate table based on specification.
        
        Parameters
        ----------
        spec : TableSpecification
            Table specification with all parameters
            
        Returns
        -------
        TableResult
            Generated table result
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
    
    def apply_template(self, template_name: str, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
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
        pd.DataFrame
            Processed data
        """
        if template_name not in self.template_registry:
            raise ValueError(f"Template '{template_name}' not found")
        
        template_func = self.template_registry[template_name]
        return template_func(data, **kwargs)
    
    def validate_data(self, data: pd.DataFrame, spec: TableSpecification) -> Dict[str, Any]:
        """
        Validate input data for table generation.
        
        Parameters
        ----------
        data : pd.DataFrame
            Input data to validate
        spec : TableSpecification
            Table specification
            
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
        
        # Check treatment variable
        trt_var = spec.get_treatment_variable()
        if trt_var not in data.columns:
            validation_result['passed'] = False
            validation_result['errors'].append(f"Treatment variable '{trt_var}' not found")
        
        # Check for sufficient data
        if len(data) < 1:
            validation_result['warnings'].append("Very small dataset (n < 1)")
        
        return validation_result
    
    def get_required_variables(self, spec: TableSpecification) -> List[str]:
        """
        Get list of required variables for this table type.
        
        Parameters
        ----------
        spec : TableSpecification
            Table specification
            
        Returns
        -------
        list
            Required variable names
        """
        # Base requirements
        required = [spec.get_treatment_variable()]
        
        # Add table-specific requirements
        if spec.variables:
            required.extend(spec.variables)
        else:
            required.extend(spec.get_default_variables())
        
        return list(set(required))  # Remove duplicates
    
    def create_rtf_table(self, data: pd.DataFrame, spec: TableSpecification) -> RTFTable:
        """
        Create RTF table from processed data.
        
        Parameters
        ----------
        data : pd.DataFrame
            Processed table data
        spec : TableSpecification
            Table specification
            
        Returns
        -------
        RTFTable
            RTF table object
        """
        rtf_table = RTFTable()
        
        # Set page settings from config
        page_settings = spec.config.page_settings
        rtf_table.rtf_page(
            orientation=page_settings.orientation,
            margins=page_settings.margins,
            font_size=page_settings.font_size,
            font_family=page_settings.font_family
        )
        
        # Add title and subtitle
        rtf_table.rtf_title(spec.get_title(), spec.get_subtitle())
        
        # Add column headers
        if not data.empty:
            rtf_table.rtf_colheader(list(data.columns))
            rtf_table.rtf_body(data)
        
        # Add footnotes
        footnotes = spec.get_footnotes()
        if footnotes:
            rtf_table.rtf_footnote(footnotes)
        
        # Add source if specified
        if hasattr(spec, 'source') and spec.source:
            rtf_table.rtf_source(spec.source)
        
        return rtf_table
    
    def format_statistics(self, value: Any, stat_name: str, config) -> str:
        """
        Format a statistical value according to configuration.
        
        Parameters
        ----------
        value : any
            Value to format
        stat_name : str
            Name of the statistic
        config : ReportConfig
            Report configuration
            
        Returns
        -------
        str
            Formatted value
        """
        if pd.isna(value):
            return ""
        
        stat_config = config.get_statistic(stat_name)
        if stat_config:
            return stat_config.format_value(value)
        
        # Default formatting
        if isinstance(value, (int, float)):
            return f"{value:.1f}"
        return str(value)
    
    def generate_metadata(self, spec: TableSpecification, 
                         generation_time: datetime = None) -> Dict[str, Any]:
        """
        Generate metadata for the table result.
        
        Parameters
        ----------
        spec : TableSpecification
            Table specification
        generation_time : datetime, optional
            Time of generation
            
        Returns
        -------
        dict
            Table metadata
        """
        if generation_time is None:
            generation_time = datetime.now()
        
        return {
            'table_type': spec.type,
            'title': spec.get_title(),
            'subtitle': spec.get_subtitle(),
            'population': spec.population,
            'treatment_variable': spec.get_treatment_variable(),
            'variables': spec.variables or spec.get_default_variables(),
            'statistics': spec.statistics or spec.get_default_statistics(),
            'generation_time': generation_time,
            'generator_class': self.__class__.__name__,
            'config_type': type(spec.config).__name__
        }
    
    def post_process_data(self, data: pd.DataFrame, spec: TableSpecification) -> pd.DataFrame:
        """
        Post-process the generated data.
        
        Parameters
        ----------
        data : pd.DataFrame
            Generated data
        spec : TableSpecification
            Table specification
            
        Returns
        -------
        pd.DataFrame
            Post-processed data
        """
        # Sort by treatment if specified
        trt_var = spec.get_treatment_variable()
        if trt_var in data.columns:
            # Get treatment order from config or data
            if hasattr(spec.config, 'treatments') and 'levels' in spec.config.treatments:
                treatment_order = spec.config.treatments['levels']
                data[trt_var] = pd.Categorical(data[trt_var], categories=treatment_order, ordered=True)
                data = data.sort_values(trt_var)
        
        # Apply any custom sorting
        if spec.sort_by and spec.sort_by in data.columns:
            data = data.sort_values(spec.sort_by)
        
        return data 