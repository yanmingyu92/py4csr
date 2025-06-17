"""
Data preprocessing functions for clinical trial datasets.

This module provides functions for preprocessing and formatting
clinical data for analysis and reporting.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Union


def apply_formats(data: pd.DataFrame, 
                 format_dict: Dict[str, str]) -> pd.DataFrame:
    """
    Apply formatting to DataFrame columns.
    
    Parameters
    ----------
    data : pd.DataFrame
        Input dataset
    format_dict : dict
        Dictionary mapping column names to format strings
        
    Returns
    -------
    pd.DataFrame
        Formatted dataset
    """
    formatted_data = data.copy()
    
    for col, fmt in format_dict.items():
        if col in formatted_data.columns:
            if fmt == 'date':
                formatted_data[col] = pd.to_datetime(formatted_data[col])
            elif fmt == 'numeric':
                formatted_data[col] = pd.to_numeric(formatted_data[col], errors='coerce')
            elif fmt == 'categorical':
                formatted_data[col] = formatted_data[col].astype('category')
    
    return formatted_data


def handle_missing_data(data: pd.DataFrame,
                       strategy: str = 'listwise',
                       fill_values: Dict[str, Any] = None) -> pd.DataFrame:
    """
    Handle missing data in clinical datasets.
    
    Parameters
    ----------
    data : pd.DataFrame
        Input dataset with missing values
    strategy : str, default 'listwise'
        Missing data strategy: 'listwise', 'pairwise', 'impute', 'forward_fill'
    fill_values : dict, optional
        Dictionary of column -> fill value for imputation
        
    Returns
    -------
    pd.DataFrame
        Dataset with missing data handled
    """
    result_data = data.copy()
    
    if strategy == 'listwise':
        # Remove rows with any missing values
        n_before = len(result_data)
        result_data = result_data.dropna()
        n_after = len(result_data)
        if n_before != n_after:
            print(f"Listwise deletion: removed {n_before - n_after} rows with missing data")
    
    elif strategy == 'pairwise':
        # Keep all data, handle missing values analysis-by-analysis
        print("Pairwise deletion: keeping all data, missing values handled per analysis")
        pass
    
    elif strategy == 'impute':
        if fill_values:
            # Use specified fill values
            for col, fill_val in fill_values.items():
                if col in result_data.columns:
                    result_data[col] = result_data[col].fillna(fill_val)
        else:
            # Use default imputation strategies
            for col in result_data.columns:
                if result_data[col].dtype in ['int64', 'float64']:
                    # Numeric: fill with median
                    result_data[col] = result_data[col].fillna(result_data[col].median())
                else:
                    # Categorical: fill with mode
                    mode_val = result_data[col].mode()
                    if len(mode_val) > 0:
                        result_data[col] = result_data[col].fillna(mode_val[0])
    
    elif strategy == 'forward_fill':
        # Forward fill missing values
        result_data = result_data.fillna(method='ffill')
    
    else:
        raise ValueError(f"Unknown missing data strategy: {strategy}")
    
    return result_data


def derive_variables(data: pd.DataFrame,
                    derivations: Dict[str, str]) -> pd.DataFrame:
    """
    Derive new variables based on existing ones.
    
    Parameters
    ----------
    data : pd.DataFrame
        Input dataset
    derivations : dict
        Dictionary mapping new variable names to derivation expressions
        
    Returns
    -------
    pd.DataFrame
        Dataset with derived variables
    """
    derived_data = data.copy()
    
    for new_var, expression in derivations.items():
        try:
            derived_data[new_var] = derived_data.eval(expression)
        except Exception as e:
            print(f"Warning: Could not derive {new_var}: {e}")
    
    return derived_data


def clean_data(data: pd.DataFrame, 
               remove_duplicates: bool = True,
               standardize_columns: bool = True) -> pd.DataFrame:
    """
    Clean clinical data with standard preprocessing steps.
    
    Parameters
    ----------
    data : pd.DataFrame
        Input clinical dataset
    remove_duplicates : bool, default True
        Whether to remove duplicate rows
    standardize_columns : bool, default True
        Whether to standardize column names
        
    Returns
    -------
    pd.DataFrame
        Cleaned dataset
    """
    cleaned_data = data.copy()
    
    # Remove duplicates
    if remove_duplicates:
        n_before = len(cleaned_data)
        cleaned_data = cleaned_data.drop_duplicates()
        n_after = len(cleaned_data)
        if n_before != n_after:
            print(f"Removed {n_before - n_after} duplicate rows")
    
    # Standardize column names
    if standardize_columns:
        cleaned_data.columns = cleaned_data.columns.str.upper().str.strip()
    
    # Convert string representations of missing to actual NaN
    string_na_values = ['', ' ', 'NA', 'N/A', 'NULL', 'null', '.', 'Missing']
    for col in cleaned_data.select_dtypes(include=['object']).columns:
        cleaned_data[col] = cleaned_data[col].replace(string_na_values, np.nan)
    
    return cleaned_data 