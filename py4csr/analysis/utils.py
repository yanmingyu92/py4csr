"""
Utility functions for statistical analysis and formatting.

This module provides helper functions for formatting statistical results
and performing common calculations used in clinical study reports.
"""

import numpy as np
from typing import Union, Optional


def format_mean_sd(mean: float, sd: float, 
                  mean_digits: int = 1, sd_digits: int = 2) -> str:
    """
    Format mean and standard deviation for reporting.
    
    Parameters
    ----------
    mean : float
        Mean value
    sd : float
        Standard deviation
    mean_digits : int, default 1
        Number of decimal places for mean
    sd_digits : int, default 2
        Number of decimal places for standard deviation
        
    Returns
    -------
    str
        Formatted string "mean (sd)"
        
    Examples
    --------
    >>> format_mean_sd(12.5, 3.24)
    '12.5 (3.24)'
    """
    if np.isnan(mean) or np.isnan(sd):
        return "N/A"
    
    mean_str = f"{mean:.{mean_digits}f}"
    sd_str = f"{sd:.{sd_digits}f}"
    
    return f"{mean_str} ({sd_str})"


def format_ci(estimate: float, lower: float, upper: float,
              digits: int = 2) -> str:
    """
    Format confidence interval for reporting.
    
    Parameters
    ----------
    estimate : float
        Point estimate
    lower : float
        Lower confidence limit
    upper : float
        Upper confidence limit
    digits : int, default 2
        Number of decimal places
        
    Returns
    -------
    str
        Formatted string "estimate (lower, upper)"
        
    Examples
    --------
    >>> format_ci(2.5, 1.2, 3.8)
    '2.50 (1.20, 3.80)'
    """
    if any(np.isnan([estimate, lower, upper])):
        return "N/A"
    
    est_str = f"{estimate:.{digits}f}"
    lower_str = f"{lower:.{digits}f}"
    upper_str = f"{upper:.{digits}f}"
    
    return f"{est_str} ({lower_str}, {upper_str})"


def format_pvalue(p_value: float, digits: int = 3, 
                 threshold: Optional[float] = None) -> str:
    """
    Format p-value for reporting.
    
    Parameters
    ----------
    p_value : float
        P-value to format
    digits : int, default 3
        Number of decimal places
    threshold : float, optional
        Threshold for showing "<" instead of exact value
        
    Returns
    -------
    str
        Formatted p-value string
        
    Examples
    --------
    >>> format_pvalue(0.0234)
    '0.023'
    >>> format_pvalue(0.0001)
    '<0.001'
    """
    if np.isnan(p_value):
        return "N/A"
    
    if threshold is None:
        threshold = 10 ** (-digits)
    
    if p_value < threshold:
        return f"<{threshold:.{digits}f}"
    else:
        return f"{p_value:.{digits}f}"


def format_number(value: Union[float, int], digits: int = 1,
                 width: Optional[int] = None) -> str:
    """
    Format a number for reporting.
    
    Parameters
    ----------
    value : float or int
        Number to format
    digits : int, default 1
        Number of decimal places
    width : int, optional
        Minimum width for formatting
        
    Returns
    -------
    str
        Formatted number string
    """
    if np.isnan(value):
        return "N/A"
    
    if width is None:
        width = digits + 4
    
    return f"{value:{width}.{digits}f}"


def calculate_locf(data, subject_col: str, visit_col: str, 
                  value_col: str, baseline_visit: str = "Baseline") -> np.ndarray:
    """
    Apply Last Observation Carried Forward (LOCF) imputation.
    
    Parameters
    ----------
    data : pd.DataFrame
        Input dataset
    subject_col : str
        Subject identifier column
    visit_col : str
        Visit column
    value_col : str
        Value column to impute
    baseline_visit : str, default "Baseline"
        Name of baseline visit
        
    Returns
    -------
    np.ndarray
        LOCF imputed values
    """
    import pandas as pd
    
    # Sort by subject and visit
    data_sorted = data.sort_values([subject_col, visit_col])
    
    # Group by subject and forward fill
    locf_values = (data_sorted
                   .groupby(subject_col)[value_col]
                   .fillna(method='ffill')
                   .values)
    
    return locf_values


def calculate_change_from_baseline(data, subject_col: str, visit_col: str,
                                 value_col: str, baseline_visit: str = "Baseline") -> np.ndarray:
    """
    Calculate change from baseline values.
    
    Parameters
    ----------
    data : pd.DataFrame
        Input dataset
    subject_col : str
        Subject identifier column
    visit_col : str
        Visit column
    value_col : str
        Value column
    baseline_visit : str, default "Baseline"
        Name of baseline visit
        
    Returns
    -------
    np.ndarray
        Change from baseline values
    """
    import pandas as pd
    
    # Get baseline values
    baseline_data = data[data[visit_col] == baseline_visit][[subject_col, value_col]]
    baseline_data = baseline_data.rename(columns={value_col: 'baseline'})
    
    # Merge with main data
    merged = data.merge(baseline_data, on=subject_col, how='left')
    
    # Calculate change
    change = merged[value_col] - merged['baseline']
    
    return change.values


def get_summary_stats(values: np.ndarray, include_missing: bool = True) -> dict:
    """
    Calculate summary statistics for a numeric array.
    
    Parameters
    ----------
    values : np.ndarray
        Numeric values
    include_missing : bool, default True
        Whether to include missing value count
        
    Returns
    -------
    dict
        Dictionary of summary statistics
    """
    clean_values = values[~np.isnan(values)]
    
    stats = {
        'n': len(clean_values),
        'mean': np.mean(clean_values) if len(clean_values) > 0 else np.nan,
        'std': np.std(clean_values, ddof=1) if len(clean_values) > 1 else np.nan,
        'median': np.median(clean_values) if len(clean_values) > 0 else np.nan,
        'min': np.min(clean_values) if len(clean_values) > 0 else np.nan,
        'max': np.max(clean_values) if len(clean_values) > 0 else np.nan,
        'q1': np.percentile(clean_values, 25) if len(clean_values) > 0 else np.nan,
        'q3': np.percentile(clean_values, 75) if len(clean_values) > 0 else np.nan,
    }
    
    if include_missing:
        stats['missing'] = len(values) - len(clean_values)
    
    return stats


def get_frequency_stats(values: np.ndarray, sort_by_freq: bool = True) -> dict:
    """
    Calculate frequency statistics for categorical data.
    
    Parameters
    ----------
    values : np.ndarray
        Categorical values
    sort_by_freq : bool, default True
        Whether to sort by frequency
        
    Returns
    -------
    dict
        Dictionary of frequency statistics
    """
    import pandas as pd
    
    # Remove missing values for frequency calculation
    clean_values = values[~pd.isna(values)]
    
    # Count frequencies
    freq_series = pd.Series(clean_values).value_counts(sort=sort_by_freq)
    
    # Calculate percentages
    total = len(clean_values)
    percentages = (freq_series / total * 100) if total > 0 else freq_series * 0
    
    stats = {
        'total': len(values),
        'valid': total,
        'missing': len(values) - total,
        'frequencies': freq_series.to_dict(),
        'percentages': percentages.to_dict()
    }
    
    return stats 