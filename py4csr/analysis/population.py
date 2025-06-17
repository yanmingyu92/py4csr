"""
Population analysis functions for clinical trial data.

This module provides functions for analyzing subject disposition
and population flow in clinical trials.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any


def create_disposition_table(data, treatment_var='TRT01P', disposition_vars=['SAFFL', 'EFFFL', 'DTHFL']):
    """
    Create subject disposition table.
    
    Parameters
    ----------
    data : pandas.DataFrame
        Subject-level dataset (e.g., ADSL)
    treatment_var : str, default 'TRT01P'
        Treatment variable name
    disposition_vars : list, default ['SAFFL', 'EFFFL', 'DTHFL']
        List of disposition flag variables
        
    Returns
    -------
    pandas.DataFrame
        Subject disposition table
    """
    
    treatments = sorted(data[treatment_var].unique())
    
    # Create disposition summary
    disposition_data = []
    
    # Total randomized
    randomized_row = {'Category': 'Total Randomized'}
    for trt in treatments:
        n_total = len(data[data[treatment_var] == trt])
        randomized_row[trt] = f'{n_total}'
    disposition_data.append(randomized_row)
    
    # Disposition categories
    disposition_labels = {
        'SAFFL': 'Safety Population',
        'EFFFL': 'Efficacy Population', 
        'DTHFL': 'Deaths'
    }
    
    for var in disposition_vars:
        if var in data.columns:
            category_row = {'Category': disposition_labels.get(var, var)}
            for trt in treatments:
                trt_data = data[data[treatment_var] == trt]
                n_yes = len(trt_data[trt_data[var] == 'Y'])
                n_total = len(trt_data)
                pct = (n_yes / n_total * 100) if n_total > 0 else 0
                category_row[trt] = f'{n_yes} ({pct:.1f}%)'
            disposition_data.append(category_row)
    
    # Completion status
    if 'DCSREAS' in data.columns:
        completion_row = {'Category': 'Completed Study'}
        for trt in treatments:
            trt_data = data[data[treatment_var] == trt]
            n_completed = len(trt_data[trt_data['DCSREAS'] == 'COMPLETED'])
            n_total = len(trt_data)
            pct = (n_completed / n_total * 100) if n_total > 0 else 0
            completion_row[trt] = f'{n_completed} ({pct:.1f}%)'
        disposition_data.append(completion_row)
    
    return pd.DataFrame(disposition_data)


def create_population_summary(data, treatment_var='TRT01P', population_flags=['SAFFL', 'EFFFL']):
    """
    Create analysis population summary table.
    
    Parameters
    ----------
    data : pandas.DataFrame
        Subject-level dataset (e.g., ADSL)
    treatment_var : str, default 'TRT01P'
        Treatment variable name
    population_flags : list, default ['SAFFL', 'EFFFL']
        List of analysis population flag variables
        
    Returns
    -------
    pandas.DataFrame
        Analysis population summary table
    """
    
    treatments = sorted(data[treatment_var].unique())
    
    # Create population summary
    population_data = []
    
    # Population labels
    population_labels = {
        'SAFFL': 'Safety Analysis Population',
        'EFFFL': 'Efficacy Analysis Population',
        'ITTFL': 'Intent-to-Treat Population',
        'PPFL': 'Per-Protocol Population'
    }
    
    for flag in population_flags:
        if flag in data.columns:
            pop_row = {'Population': population_labels.get(flag, flag)}
            for trt in treatments:
                trt_data = data[data[treatment_var] == trt]
                n_pop = len(trt_data[trt_data[flag] == 'Y'])
                pop_row[trt] = f'{n_pop}'
            population_data.append(pop_row)
    
    return pd.DataFrame(population_data)


def _format_population_name(flag_name: str) -> str:
    """Format population flag name for display."""
    
    name_mapping = {
        'SAFFL': 'Safety Population',
        'EFFFL': 'Efficacy Population', 
        'ITTFL': 'Intent-to-Treat Population',
        'PPFL': 'Per-Protocol Population',
        'COMPLFL': 'Completer Population'
    }
    
    return name_mapping.get(flag_name, flag_name.replace('FL', '').replace('_', ' ').title())


def analyze_discontinuations(data: pd.DataFrame,
                           treatment_var: str,
                           discontinuation_var: str = 'DCSREAS') -> pd.DataFrame:
    """
    Analyze reasons for study discontinuation.
    
    Parameters
    ----------
    data : pd.DataFrame
        Subject-level dataset
    treatment_var : str
        Treatment variable name
    discontinuation_var : str, default 'DCSREAS'
        Discontinuation reason variable name
        
    Returns
    -------
    pd.DataFrame
        Discontinuation analysis table
    """
    
    if discontinuation_var not in data.columns:
        return pd.DataFrame({'Error': ['Discontinuation variable not found']})
    
    # Filter to discontinued subjects
    discontinued = data[data[discontinuation_var].notna()]
    
    if len(discontinued) == 0:
        return pd.DataFrame({'Message': ['No discontinuations found']})
    
    # Count by reason and treatment
    disc_counts = discontinued.groupby([discontinuation_var, treatment_var]).size().reset_index(name='count')
    
    # Get total subjects per treatment
    total_counts = data.groupby(treatment_var).size().reset_index(name='total')
    
    # Merge and calculate percentages
    disc_summary = disc_counts.merge(total_counts, on=treatment_var)
    disc_summary['percentage'] = (disc_summary['count'] / disc_summary['total'] * 100).round(1)
    disc_summary['formatted'] = disc_summary['count'].astype(str) + ' (' + disc_summary['percentage'].astype(str) + '%)'
    
    # Pivot table
    discontinuation_table = disc_summary.pivot(
        index=discontinuation_var, 
        columns=treatment_var, 
        values='formatted'
    ).fillna('0 (0.0%)').reset_index()
    
    return discontinuation_table 