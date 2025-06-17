from typing import Dict, List, Optional, Any, Callable
import pandas as pd
import numpy as np
from functools import reduce
import logging

class DataProcessor:
    """
    Functional data processor following RRG principles.
    
    Implements pure functions for data validation, cleaning, and transformation
    without side effects, supporting method chaining and composition.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
    
    # Pure functions - no side effects
    def validate_data(self, data: pd.DataFrame, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data using pure function approach."""
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'summary': {}
        }
        
        # Check required columns
        if 'required_columns' in rules:
            missing_cols = set(rules['required_columns']) - set(data.columns)
            if missing_cols:
                validation_results['is_valid'] = False
                validation_results['errors'].append(f"Missing columns: {missing_cols}")
        
        # Check data types
        if 'column_types' in rules:
            for col, expected_type in rules['column_types'].items():
                if col in data.columns and not data[col].dtype == expected_type:
                    validation_results['warnings'].append(
                        f"Column {col} type mismatch: expected {expected_type}, got {data[col].dtype}"
                    )
        
        # Check missing values
        missing_summary = data.isnull().sum()
        validation_results['summary']['missing_values'] = missing_summary.to_dict()
        
        return validation_results
    
    def clean_data(self, data: pd.DataFrame, cleaning_rules: Dict[str, Any]) -> pd.DataFrame:
        """Clean data using functional composition."""
        # Create a copy to maintain immutability
        cleaned_data = data.copy()
        
        # Apply cleaning functions in sequence
        cleaning_functions = [
            self._remove_duplicates,
            self._handle_missing_values,
            self._standardize_formats,
            self._apply_filters
        ]
        
        # Functional composition using reduce
        cleaned_data = reduce(
            lambda df, func: func(df, cleaning_rules),
            cleaning_functions,
            cleaned_data
        )
        
        return cleaned_data
    
    def transform_data(self, data: pd.DataFrame, transformations: List[Callable]) -> pd.DataFrame:
        """Apply transformations using functional composition."""
        return reduce(lambda df, transform: transform(df), transformations, data.copy())
    
    # Private helper functions (pure)
    def _remove_duplicates(self, data: pd.DataFrame, rules: Dict[str, Any]) -> pd.DataFrame:
        """Remove duplicates based on rules."""
        if 'duplicate_subset' in rules:
            return data.drop_duplicates(subset=rules['duplicate_subset'])
        return data.drop_duplicates()
    
    def _handle_missing_values(self, data: pd.DataFrame, rules: Dict[str, Any]) -> pd.DataFrame:
        """Handle missing values functionally."""
        result = data.copy()
        
        if 'fill_values' in rules:
            for col, fill_value in rules['fill_values'].items():
                if col in result.columns:
                    result[col] = result[col].fillna(fill_value)
        
        if 'drop_missing' in rules:
            cols_to_check = rules['drop_missing']
            result = result.dropna(subset=cols_to_check)
        
        return result
    
    def _standardize_formats(self, data: pd.DataFrame, rules: Dict[str, Any]) -> pd.DataFrame:
        """Standardize data formats."""
        result = data.copy()
        
        if 'date_columns' in rules:
            for col in rules['date_columns']:
                if col in result.columns:
                    result[col] = pd.to_datetime(result[col], errors='coerce')
        
        if 'numeric_columns' in rules:
            for col in rules['numeric_columns']:
                if col in result.columns:
                    result[col] = pd.to_numeric(result[col], errors='coerce')
        
        return result
    
    def _apply_filters(self, data: pd.DataFrame, rules: Dict[str, Any]) -> pd.DataFrame:
        """Apply filters functionally."""
        result = data.copy()
        
        if 'filters' in rules:
            for filter_expr in rules['filters']:
                try:
                    result = result.query(filter_expr)
                except Exception as e:
                    self.logger.warning(f"Filter '{filter_expr}' failed: {e}")
        
        return result
    
    # Functional composition helpers
    def compose_operations(self, *operations: Callable) -> Callable:
        """Compose multiple operations into a single function."""
        return lambda data: reduce(lambda result, op: op(result), operations, data)
    
    def create_pipeline(self, operations: List[Dict[str, Any]]) -> Callable:
        """Create a data processing pipeline."""
        def pipeline(data: pd.DataFrame) -> pd.DataFrame:
            result = data.copy()
            for operation in operations:
                op_type = operation.get('type')
                op_params = operation.get('params', {})
                
                if op_type == 'validate':
                    validation = self.validate_data(result, op_params)
                    if not validation['is_valid']:
                        raise ValueError(f"Validation failed: {validation['errors']}")
                elif op_type == 'clean':
                    result = self.clean_data(result, op_params)
                elif op_type == 'transform':
                    transformations = op_params.get('functions', [])
                    result = self.transform_data(result, transformations)
            
            return result
        
        return pipeline