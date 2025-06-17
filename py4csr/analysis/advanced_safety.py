"""
Advanced Safety Analysis Functions for Clinical Trial Data
Implements comprehensive safety analysis capabilities following RRG design principles
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import poisson
from typing import Dict, List, Optional, Tuple, Union
import warnings

def adverse_event_analysis(data: pd.DataFrame,
                          subject_col: str,
                          treatment_col: str,
                          ae_term_col: str,
                          severity_col: Optional[str] = None,
                          soc_col: Optional[str] = None,
                          exposure_col: Optional[str] = None) -> Dict:
    """
    Comprehensive adverse event analysis (enhanced RRG AE equivalent)
    
    Parameters:
    -----------
    data : pd.DataFrame
        Adverse events dataset
    subject_col : str
        Subject identifier column
    treatment_col : str
        Treatment group column
    ae_term_col : str
        Adverse event term column
    severity_col : str, optional
        Severity/grade column
    soc_col : str, optional
        System organ class column
    exposure_col : str, optional
        Exposure time column for rate calculations
        
    Returns:
    --------
    Dict containing comprehensive AE analysis
    """
    
    results = {
        'analysis_type': 'Comprehensive Adverse Event Analysis'
    }
    
    # Overall AE summary by treatment
    treatment_summary = {}
    for treatment in data[treatment_col].unique():
        trt_data = data[data[treatment_col] == treatment]
        
        n_subjects_with_ae = trt_data[subject_col].nunique()
        total_aes = len(trt_data)
        
        summary = {
            'subjects_with_ae': n_subjects_with_ae,
            'total_ae_events': total_aes,
            'ae_rate_per_subject': total_aes / n_subjects_with_ae if n_subjects_with_ae > 0 else 0
        }
        
        if exposure_col and exposure_col in trt_data.columns:
            total_exposure = trt_data.groupby(subject_col)[exposure_col].first().sum()
            summary['total_exposure'] = total_exposure
            summary['ae_rate_per_exposure'] = total_aes / total_exposure if total_exposure > 0 else 0
        
        treatment_summary[treatment] = summary
    
    results['treatment_summary'] = treatment_summary
    
    # AE frequency by preferred term
    ae_by_term = data.groupby([treatment_col, ae_term_col]).agg({
        subject_col: 'nunique',
        ae_term_col: 'count'
    }).rename(columns={subject_col: 'subjects', ae_term_col: 'events'})
    
    results['ae_by_term'] = ae_by_term
    
    # Severity analysis if available
    if severity_col and severity_col in data.columns:
        severity_analysis = data.groupby([treatment_col, severity_col]).agg({
            subject_col: 'nunique',
            severity_col: 'count'
        }).rename(columns={subject_col: 'subjects', severity_col: 'events'})
        
        results['severity_analysis'] = severity_analysis
    
    # System organ class analysis if available
    if soc_col and soc_col in data.columns:
        soc_analysis = data.groupby([treatment_col, soc_col]).agg({
            subject_col: 'nunique',
            soc_col: 'count'
        }).rename(columns={subject_col: 'subjects', soc_col: 'events'})
        
        results['soc_analysis'] = soc_analysis
    
    return results

def laboratory_shift_analysis(data: pd.DataFrame,
                             subject_col: str,
                             treatment_col: str,
                             parameter_col: str,
                             baseline_col: str,
                             post_baseline_col: str,
                             visit_col: Optional[str] = None) -> Dict:
    """
    Laboratory shift table analysis (RRG lab shift equivalent)
    
    Parameters:
    -----------
    data : pd.DataFrame
        Laboratory data
    subject_col : str
        Subject identifier
    treatment_col : str
        Treatment group
    parameter_col : str
        Laboratory parameter
    baseline_col : str
        Baseline category (Normal/Abnormal)
    post_baseline_col : str
        Post-baseline category
    visit_col : str, optional
        Visit identifier
        
    Returns:
    --------
    Dict containing shift analysis results
    """
    
    results = {
        'analysis_type': 'Laboratory Shift Analysis'
    }
    
    # Create shift combinations
    data['shift_category'] = data[baseline_col].astype(str) + ' → ' + data[post_baseline_col].astype(str)
    
    if visit_col:
        # Analysis by visit
        shift_by_visit = {}
        for visit in data[visit_col].unique():
            visit_data = data[data[visit_col] == visit]
            
            shift_table = pd.crosstab(
                [visit_data[treatment_col], visit_data[baseline_col]], 
                visit_data[post_baseline_col],
                margins=True
            )
            
            shift_by_visit[visit] = shift_table
        
        results['shift_by_visit'] = shift_by_visit
    else:
        # Overall shift analysis
        shift_table = pd.crosstab(
            [data[treatment_col], data[baseline_col]], 
            data[post_baseline_col],
            margins=True
        )
        
        results['overall_shift'] = shift_table
    
    # Calculate shift percentages
    shift_summary = data.groupby([treatment_col, 'shift_category']).agg({
        subject_col: 'nunique'
    }).rename(columns={subject_col: 'n_subjects'})
    
    # Add percentages
    total_by_treatment = data.groupby(treatment_col)[subject_col].nunique()
    shift_summary['percentage'] = shift_summary.apply(
        lambda row: (row['n_subjects'] / total_by_treatment[row.name[0]]) * 100
        if row.name[0] in total_by_treatment else 0, axis=1
    )
    
    results['shift_summary'] = shift_summary
    
    return results

def exposure_analysis(data: pd.DataFrame,
                     subject_col: str,
                     treatment_col: str,
                     exposure_col: str,
                     exposure_unit: str = 'days') -> Dict:
    """
    Treatment exposure analysis
    
    Parameters:
    -----------
    data : pd.DataFrame
        Exposure data
    subject_col : str
        Subject identifier
    treatment_col : str
        Treatment group
    exposure_col : str
        Exposure duration column
    exposure_unit : str
        Unit of exposure measurement
        
    Returns:
    --------
    Dict containing exposure analysis
    """
    
    results = {
        'analysis_type': 'Treatment Exposure Analysis',
        'exposure_unit': exposure_unit
    }
    
    exposure_summary = {}
    for treatment in data[treatment_col].unique():
        trt_data = data[data[treatment_col] == treatment]
        
        exposure_stats = {
            'n_subjects': len(trt_data),
            'mean_exposure': trt_data[exposure_col].mean(),
            'median_exposure': trt_data[exposure_col].median(),
            'std_exposure': trt_data[exposure_col].std(),
            'min_exposure': trt_data[exposure_col].min(),
            'max_exposure': trt_data[exposure_col].max(),
            'total_exposure': trt_data[exposure_col].sum()
        }
        
        # Exposure categories
        exposure_categories = {
            f'<30 {exposure_unit}': (trt_data[exposure_col] < 30).sum(),
            f'30-89 {exposure_unit}': ((trt_data[exposure_col] >= 30) & (trt_data[exposure_col] < 90)).sum(),
            f'90-179 {exposure_unit}': ((trt_data[exposure_col] >= 90) & (trt_data[exposure_col] < 180)).sum(),
            f'≥180 {exposure_unit}': (trt_data[exposure_col] >= 180).sum()
        }
        
        exposure_stats['exposure_categories'] = exposure_categories
        exposure_summary[treatment] = exposure_stats
    
    results['exposure_summary'] = exposure_summary
    
    return results