from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from ..core.data_processor import DataProcessor

class AdvancedUtilities:
    """
    Advanced utility functions following RRG design principles.
    
    Provides sophisticated data manipulation, formatting, and
    analysis utilities for clinical reporting.
    """
    
    @staticmethod
    def advanced_string_manipulation(data: pd.DataFrame, 
                                   operations: List[Dict]) -> pd.DataFrame:
        """
        Advanced string manipulation operations.
        
        Equivalent to RRG's string processing macros.
        """
        result_data = data.copy()
        
        for op in operations:
            column = op.get('column')
            operation = op.get('operation')
            
            if column not in result_data.columns:
                continue
            
            if operation == 'standardize_case':
                case_type = op.get('case', 'upper')
                if case_type == 'upper':
                    result_data[column] = result_data[column].str.upper()
                elif case_type == 'lower':
                    result_data[column] = result_data[column].str.lower()
                elif case_type == 'title':
                    result_data[column] = result_data[column].str.title()
            
            elif operation == 'clean_whitespace':
                result_data[column] = result_data[column].str.strip()
                result_data[column] = result_data[column].str.replace(r'\s+', ' ', regex=True)
            
            elif operation == 'extract_pattern':
                pattern = op.get('pattern')
                new_column = op.get('new_column', f"{column}_extracted")
                if pattern:
                    result_data[new_column] = result_data[column].str.extract(pattern)
            
            elif operation == 'concatenate':
                other_columns = op.get('other_columns', [])
                separator = op.get('separator', ' ')
                new_column = op.get('new_column', f"{column}_concat")
                cols_to_concat = [column] + other_columns
                result_data[new_column] = result_data[cols_to_concat].apply(
                    lambda x: separator.join(x.astype(str)), axis=1
                )
        
        return result_data
    
    @staticmethod
    def advanced_date_processing(data: pd.DataFrame, 
                               date_operations: List[Dict]) -> pd.DataFrame:
        """
        Advanced date processing operations.
        
        Equivalent to RRG's date manipulation macros.
        """
        result_data = data.copy()
        
        for op in date_operations:
            column = op.get('column')
            operation = op.get('operation')
            
            if column not in result_data.columns:
                continue
            
            # Ensure column is datetime
            if not pd.api.types.is_datetime64_any_dtype(result_data[column]):
                result_data[column] = pd.to_datetime(result_data[column], errors='coerce')
            
            if operation == 'extract_components':
                result_data[f"{column}_year"] = result_data[column].dt.year
                result_data[f"{column}_month"] = result_data[column].dt.month
                result_data[f"{column}_day"] = result_data[column].dt.day
                result_data[f"{column}_weekday"] = result_data[column].dt.day_name()
            
            elif operation == 'calculate_age':
                reference_date = op.get('reference_date', datetime.now())
                if isinstance(reference_date, str):
                    reference_date = pd.to_datetime(reference_date)
                
                age_column = op.get('age_column', f"{column}_age")
                result_data[age_column] = (
                    (reference_date - result_data[column]).dt.days / 365.25
                ).round(1)
            
            elif operation == 'calculate_duration':
                end_column = op.get('end_column')
                duration_column = op.get('duration_column', f"{column}_duration")
                unit = op.get('unit', 'days')
                
                if end_column and end_column in result_data.columns:
                    if not pd.api.types.is_datetime64_any_dtype(result_data[end_column]):
                        result_data[end_column] = pd.to_datetime(result_data[end_column], errors='coerce')
                    
                    duration = result_data[end_column] - result_data[column]
                    
                    if unit == 'days':
                        result_data[duration_column] = duration.dt.days
                    elif unit == 'weeks':
                        result_data[duration_column] = (duration.dt.days / 7).round(1)
                    elif unit == 'months':
                        result_data[duration_column] = (duration.dt.days / 30.44).round(1)
                    elif unit == 'years':
                        result_data[duration_column] = (duration.dt.days / 365.25).round(1)
        
        return result_data
    
    @staticmethod
    def advanced_numeric_formatting(data: pd.DataFrame, 
                                  formatting_rules: Dict[str, Dict]) -> pd.DataFrame:
        """
        Advanced numeric formatting for clinical tables.
        
        Equivalent to RRG's numeric formatting macros.
        """
        result_data = data.copy()
        
        for column, rules in formatting_rules.items():
            if column not in result_data.columns:
                continue
            
            decimal_places = rules.get('decimal_places', 2)
            format_type = rules.get('format_type', 'standard')
            
            if format_type == 'standard':
                result_data[column] = result_data[column].round(decimal_places)
            
            elif format_type == 'percentage':
                result_data[column] = (result_data[column] * 100).round(decimal_places)
                result_data[column] = result_data[column].astype(str) + '%'
            
            elif format_type == 'scientific':
                result_data[column] = result_data[column].apply(
                    lambda x: f"{x:.{decimal_places}e}" if pd.notnull(x) else ''
                )
            
            elif format_type == 'clinical_range':
                # Format as "mean ± std" or "median (Q1, Q3)"
                if 'summary_type' in rules:
                    summary_type = rules['summary_type']
                    if summary_type == 'mean_std':
                        mean_val = result_data[column].mean()
                        std_val = result_data[column].std()
                        formatted_val = f"{mean_val:.{decimal_places}f} ± {std_val:.{decimal_places}f}"
                        result_data[f"{column}_formatted"] = formatted_val
                    
                    elif summary_type == 'median_iqr':
                        median_val = result_data[column].median()
                        q1 = result_data[column].quantile(0.25)
                        q3 = result_data[column].quantile(0.75)
                        formatted_val = f"{median_val:.{decimal_places}f} ({q1:.{decimal_places}f}, {q3:.{decimal_places}f})"
                        result_data[f"{column}_formatted"] = formatted_val
        
        return result_data

# Functional interface functions
def manipulate_strings(data: pd.DataFrame, operations: List[Dict]) -> pd.DataFrame:
    """Functional interface for string manipulation."""
    return AdvancedUtilities.advanced_string_manipulation(data, operations)

def process_dates(data: pd.DataFrame, operations: List[Dict]) -> pd.DataFrame:
    """Functional interface for date processing."""
    return AdvancedUtilities.advanced_date_processing(data, operations)

def format_numbers(data: pd.DataFrame, rules: Dict[str, Dict]) -> pd.DataFrame:
    """Functional interface for numeric formatting."""
    return AdvancedUtilities.advanced_numeric_formatting(data, rules)