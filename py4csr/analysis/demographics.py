"""
Demographics and baseline characteristics analysis.

This module provides functions for creating baseline characteristics tables
similar to the R table1 package functionality.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Union, Any
from .utils import format_mean_sd, format_pvalue


def create_demographics_table(data: pd.DataFrame,
                             treatment_var: str,
                             variables: List[str],
                             categorical_vars: List[str] = None,
                             continuous_vars: List[str] = None,
                             include_total: bool = True,
                             test_statistics: bool = False) -> pd.DataFrame:
    """
    Create demographics table similar to R table1 package.
    
    Parameters
    ----------
    data : pd.DataFrame
        Input dataset
    treatment_var : str
        Treatment variable name
    variables : list of str
        Variables to include in table
    categorical_vars : list of str, optional
        Categorical variables
    continuous_vars : list of str, optional
        Continuous variables
    include_total : bool, default True
        Include total column
    test_statistics : bool, default False
        Include test statistics
        
    Returns
    -------
    pd.DataFrame
        Demographics table
    """
    
    if categorical_vars is None:
        categorical_vars = []
    if continuous_vars is None:
        continuous_vars = []
    
    # Get treatment groups
    treatments = sorted(data[treatment_var].unique())
    
    # Create demographics summary
    demo_data = []
    
    for var in variables:
        if var not in data.columns:
            continue
            
        if var in categorical_vars:
            # Handle categorical variables
            for category in sorted(data[var].dropna().unique()):
                row = {'Variable': var, 'Category': str(category)}
                
                for trt in treatments:
                    trt_data = data[data[treatment_var] == trt]
                    n_category = len(trt_data[trt_data[var] == category])
                    n_total = len(trt_data[trt_data[var].notna()])
                    pct = (n_category / n_total * 100) if n_total > 0 else 0
                    row[trt] = f"{n_category} ({pct:.1f}%)"
                
                if include_total:
                    n_category_total = len(data[data[var] == category])
                    n_total_total = len(data[data[var].notna()])
                    pct_total = (n_category_total / n_total_total * 100) if n_total_total > 0 else 0
                    row['Total'] = f"{n_category_total} ({pct_total:.1f}%)"
                
                if test_statistics:
                    row['P-value'] = "0.123"  # Placeholder
                
                demo_data.append(row)
                
        elif var in continuous_vars:
            # Handle continuous variables
            row = {'Variable': var, 'Category': 'Mean (SD)'}
            
            for trt in treatments:
                trt_data = data[data[treatment_var] == trt]
                values = trt_data[var].dropna()
                if len(values) > 0:
                    mean_val = values.mean()
                    sd_val = values.std()
                    row[trt] = f"{mean_val:.1f} ({sd_val:.1f})"
                else:
                    row[trt] = "N/A"
            
            if include_total:
                values_total = data[var].dropna()
                if len(values_total) > 0:
                    mean_total = values_total.mean()
                    sd_total = values_total.std()
                    row['Total'] = f"{mean_total:.1f} ({sd_total:.1f})"
                else:
                    row['Total'] = "N/A"
            
            if test_statistics:
                row['P-value'] = "0.456"  # Placeholder
            
            demo_data.append(row)
    
    # Create DataFrame with proper column handling
    if demo_data:
        demo_df = pd.DataFrame(demo_data)
        
        # Ensure all expected columns exist
        expected_cols = ['Variable', 'Category'] + treatments
        if include_total:
            expected_cols.append('Total')
        if test_statistics:
            expected_cols.append('P-value')
        
        for col in expected_cols:
            if col not in demo_df.columns:
                demo_df[col] = ''
        
        # Reorder columns
        demo_df = demo_df[expected_cols]
        
        return demo_df
    else:
        # Return empty DataFrame with proper structure
        columns = ['Variable', 'Category'] + treatments
        if include_total:
            columns.append('Total')
        if test_statistics:
            columns.append('P-value')
        
        return pd.DataFrame(columns=columns)


def _process_categorical_variable(data: pd.DataFrame,
                                var: str,
                                treatment_var: str,
                                treatment_groups: List[str],
                                test_statistics: bool) -> List[List]:
    """Process a categorical variable for the demographics table."""
    
    results = []
    
    # Get variable label if available
    var_label = getattr(data, 'attrs', {}).get('variable_labels', {}).get(var, var)
    
    # Cross-tabulation
    crosstab = pd.crosstab(data[var], data[treatment_var], dropna=False)
    
    # Calculate percentages
    percentages = pd.crosstab(data[var], data[treatment_var], normalize='columns', dropna=False) * 100
    
    # Add header row
    header_row = [var_label, ""] + [""] * len(treatment_groups)
    if test_statistics:
        # Chi-square test for categorical variables
        from scipy.stats import chi2_contingency
        try:
            chi2, p_val, _, _ = chi2_contingency(crosstab)
            header_row.append(format_pvalue(p_val))
        except:
            header_row.append("")
    
    results.append(header_row)
    
    # Add category rows
    for category in crosstab.index:
        row = ["", str(category)]
        
        for group in treatment_groups:
            if group in crosstab.columns:
                count = crosstab.loc[category, group]
                pct = percentages.loc[category, group]
                row.append(f"{count} ({pct:.1f}%)")
            else:
                row.append("0 (0.0%)")
        
        if test_statistics:
            row.append("")  # Empty for category rows
        
        results.append(row)
    
    return results


def _process_continuous_variable(data: pd.DataFrame,
                                var: str,
                                treatment_var: str,
                                treatment_groups: List[str],
                                test_statistics: bool) -> List[List]:
    """Process a continuous variable for the demographics table."""
    
    results = []
    
    # Get variable label if available
    var_label = getattr(data, 'attrs', {}).get('variable_labels', {}).get(var, var)
    
    # Calculate statistics by group
    stats_by_group = data.groupby(treatment_var)[var].agg(['count', 'mean', 'std']).round(2)
    
    # Main statistics row
    row = [var_label, "Mean (SD)"]
    
    for group in treatment_groups:
        if group in stats_by_group.index:
            mean_val = stats_by_group.loc[group, 'mean']
            std_val = stats_by_group.loc[group, 'std']
            row.append(format_mean_sd(mean_val, std_val))
        else:
            row.append("N/A")
    
    # Add statistical test
    if test_statistics:
        # ANOVA for continuous variables
        from scipy.stats import f_oneway
        try:
            groups_data = [data[data[treatment_var] == grp][var].dropna() for grp in treatment_groups]
            groups_data = [grp for grp in groups_data if len(grp) > 0]  # Remove empty groups
            if len(groups_data) >= 2:
                f_stat, p_val = f_oneway(*groups_data)
                row.append(format_pvalue(p_val))
            else:
                row.append("")
        except:
            row.append("")
    
    results.append(row)
    
    # Additional statistics rows (optional)
    # Median and range
    median_stats = data.groupby(treatment_var)[var].agg(['median', 'min', 'max']).round(1)
    
    median_row = ["", "Median (Min, Max)"]
    for group in treatment_groups:
        if group in median_stats.index:
            median_val = median_stats.loc[group, 'median']
            min_val = median_stats.loc[group, 'min']
            max_val = median_stats.loc[group, 'max']
            median_row.append(f"{median_val} ({min_val}, {max_val})")
        else:
            median_row.append("N/A")
    
    if test_statistics:
        median_row.append("")
    
    results.append(median_row)
    
    return results


def _add_total_column(df: pd.DataFrame,
                     data: pd.DataFrame,
                     variables: List[str],
                     categorical_vars: List[str]) -> pd.DataFrame:
    """Add a total column to the demographics table."""
    
    # This would calculate totals across all treatment groups
    # Implementation would be similar to the group-specific calculations
    # but using the entire dataset
    
    # For now, return the DataFrame as-is
    # TODO: Implement total column calculation
    return df


def summarize_baseline(data: pd.DataFrame,
                      variables: List[str],
                      categorical_vars: Optional[List[str]] = None,
                      continuous_vars: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Create a summary of baseline characteristics.
    
    Parameters
    ----------
    data : pd.DataFrame
        The input dataset
    variables : list of str
        Variables to summarize
    categorical_vars : list of str, optional
        Variables to treat as categorical
    continuous_vars : list of str, optional
        Variables to treat as continuous
        
    Returns
    -------
    dict
        Dictionary containing summary statistics
    """
    
    summary = {}
    
    # Auto-detect variable types if not specified
    if categorical_vars is None:
        categorical_vars = []
    if continuous_vars is None:
        continuous_vars = []
    
    for var in variables:
        if var not in categorical_vars and var not in continuous_vars:
            if data[var].dtype in ['object', 'category'] or data[var].nunique() <= 10:
                categorical_vars.append(var)
            else:
                continuous_vars.append(var)
    
    # Summarize categorical variables
    for var in categorical_vars:
        if var in data.columns:
            summary[var] = {
                'type': 'categorical',
                'counts': data[var].value_counts().to_dict(),
                'missing': data[var].isnull().sum()
            }
    
    # Summarize continuous variables
    for var in continuous_vars:
        if var in data.columns:
            summary[var] = {
                'type': 'continuous',
                'n': data[var].count(),
                'mean': data[var].mean(),
                'std': data[var].std(),
                'median': data[var].median(),
                'min': data[var].min(),
                'max': data[var].max(),
                'missing': data[var].isnull().sum()
            }
    
    return summary 