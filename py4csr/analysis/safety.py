"""
Safety analysis functions for clinical trial data.

This module provides functions for performing safety analyses
including adverse events and laboratory data summaries.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any


def create_ae_summary(data: pd.DataFrame,
                     treatment_var: str,
                     term_var: str,
                     severity_var: Optional[str] = None) -> pd.DataFrame:
    """
    Create adverse events summary table.
    
    Parameters
    ----------
    data : pd.DataFrame
        Adverse events dataset (ADAE)
    treatment_var : str
        Treatment variable name
    term_var : str
        AE term variable name
    severity_var : str, optional
        Severity variable name
        
    Returns
    -------
    pd.DataFrame
        AE summary table
    """
    
    # Count AEs by treatment and term
    ae_counts = data.groupby([term_var, treatment_var]).size().reset_index(name='count')
    
    # Get total subjects per treatment
    subject_counts = data.groupby(treatment_var)['USUBJID'].nunique().reset_index(name='total_subjects')
    
    # Merge and calculate percentages
    ae_summary = ae_counts.merge(subject_counts, on=treatment_var)
    ae_summary['percentage'] = (ae_summary['count'] / ae_summary['total_subjects'] * 100).round(1)
    ae_summary['formatted'] = ae_summary['count'].astype(str) + ' (' + ae_summary['percentage'].astype(str) + '%)'
    
    # Pivot to wide format
    summary_table = ae_summary.pivot(index=term_var, columns=treatment_var, values='formatted').fillna('0 (0.0%)')
    summary_table.reset_index(inplace=True)
    
    return summary_table


def create_ae_specific_table(data, treatment_var='TRT01A', term_var='AEDECOD', system_var='AEBODSYS'):
    """
    Create adverse events table by System Organ Class and Preferred Term.
    
    Parameters
    ----------
    data : pandas.DataFrame
        Adverse events dataset (e.g., ADAE)
    treatment_var : str, default 'TRT01A'
        Treatment variable name
    term_var : str, default 'AEDECOD'
        Preferred term variable name  
    system_var : str, default 'AEBODSYS'
        System organ class variable name
        
    Returns
    -------
    pandas.DataFrame
        AE specific table with SOC and PT breakdown
    """
    
    # Get unique treatments
    treatments = sorted(data[treatment_var].unique())
    
    # Create summary by SOC and PT
    ae_summary = []
    
    # Group by SOC and PT
    for soc in sorted(data[system_var].unique()):
        soc_data = data[data[system_var] == soc]
        
        # Add SOC header row
        soc_row = {'SOC': soc, 'PT': ''}
        for trt in treatments:
            trt_data = soc_data[soc_data[treatment_var] == trt]
            n_subjects = trt_data['USUBJID'].nunique()
            soc_row[f'{trt}_n'] = n_subjects
            soc_row[f'{trt}_pct'] = f'({n_subjects/len(data[data[treatment_var]==trt]["USUBJID"].unique())*100:.1f})'
        ae_summary.append(soc_row)
        
        # Add PT rows within SOC
        for pt in sorted(soc_data[term_var].unique()):
            pt_data = soc_data[soc_data[term_var] == pt]
            pt_row = {'SOC': '', 'PT': f'  {pt}'}
            
            for trt in treatments:
                trt_data = pt_data[pt_data[treatment_var] == trt]
                n_subjects = trt_data['USUBJID'].nunique()
                pt_row[f'{trt}_n'] = n_subjects
                pt_row[f'{trt}_pct'] = f'({n_subjects/len(data[data[treatment_var]==trt]["USUBJID"].unique())*100:.1f})'
            ae_summary.append(pt_row)
    
    return pd.DataFrame(ae_summary)


def create_lab_summary(data: pd.DataFrame,
                      treatment_var: str,
                      parameter_var: str = 'PARAMCD',
                      value_var: str = 'AVAL',
                      visit_var: str = 'AVISIT') -> pd.DataFrame:
    """
    Create laboratory data summary table.
    
    Parameters
    ----------
    data : pd.DataFrame
        Laboratory dataset (ADLB)
    treatment_var : str
        Treatment variable name
    parameter_var : str, default 'PARAMCD'
        Parameter code variable name
    value_var : str, default 'AVAL'
        Analysis value variable name
    visit_var : str, default 'AVISIT'
        Visit variable name
        
    Returns
    -------
    pd.DataFrame
        Laboratory summary table
    """
    
    # Calculate summary statistics by parameter, visit, and treatment
    lab_stats = data.groupby([parameter_var, visit_var, treatment_var])[value_var].agg([
        'count', 'mean', 'std', 'median', 'min', 'max'
    ]).round(2).reset_index()
    
    # Format mean (SD)
    lab_stats['mean_sd'] = lab_stats['mean'].astype(str) + ' (' + lab_stats['std'].astype(str) + ')'
    
    # Format median (min, max)
    lab_stats['median_range'] = (lab_stats['median'].astype(str) + ' (' + 
                                lab_stats['min'].astype(str) + ', ' + 
                                lab_stats['max'].astype(str) + ')')
    
    # Select key columns
    summary_cols = [parameter_var, visit_var, treatment_var, 'count', 'mean_sd', 'median_range']
    lab_summary = lab_stats[summary_cols]
    
    return lab_summary 