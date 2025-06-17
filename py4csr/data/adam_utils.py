"""
CDISC ADaM Data Manipulation Utilities.

This module provides specialized functions for manipulating CDISC ADaM datasets
commonly used in clinical study reports, following ICH E3 and CTD guidelines.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Tuple, Any
import warnings
from datetime import datetime, timedelta


def derive_treatment_variables(adsl: pd.DataFrame) -> pd.DataFrame:
    """
    Derive standard treatment variables for ADSL dataset.
    
    Parameters
    ----------
    adsl : pd.DataFrame
        ADSL dataset
        
    Returns
    -------
    pd.DataFrame
        ADSL with derived treatment variables
    """
    adsl_derived = adsl.copy()
    
    # Ensure treatment numeric variables exist
    if 'TRT01PN' not in adsl_derived.columns and 'TRT01P' in adsl_derived.columns:
        trt_map = {
            'Placebo': 0,
            'Xanomeline Low Dose': 54,
            'Xanomeline High Dose': 81
        }
        adsl_derived['TRT01PN'] = adsl_derived['TRT01P'].map(trt_map)
    
    # Derive actual treatment from planned if missing
    if 'TRT01A' not in adsl_derived.columns and 'TRT01P' in adsl_derived.columns:
        adsl_derived['TRT01A'] = adsl_derived['TRT01P']
    
    if 'TRT01AN' not in adsl_derived.columns and 'TRT01PN' in adsl_derived.columns:
        adsl_derived['TRT01AN'] = adsl_derived['TRT01PN']
    
    return adsl_derived


def derive_analysis_flags(adsl: pd.DataFrame) -> pd.DataFrame:
    """
    Derive standard analysis population flags.
    
    Parameters
    ----------
    adsl : pd.DataFrame
        ADSL dataset
        
    Returns
    -------
    pd.DataFrame
        ADSL with derived analysis flags
    """
    adsl_derived = adsl.copy()
    
    # Safety flag - typically all randomized subjects
    if 'SAFFL' not in adsl_derived.columns:
        adsl_derived['SAFFL'] = 'Y'
    
    # Efficacy flag - typically excludes major protocol violations
    if 'EFFFL' not in adsl_derived.columns:
        # Simple derivation - could be more complex in real studies
        adsl_derived['EFFFL'] = np.where(
            adsl_derived.get('DTHFL', 'N') == 'Y', 'N', 'Y'
        )
    
    # ITT flag - Intent-to-treat population
    if 'ITTFL' not in adsl_derived.columns:
        adsl_derived['ITTFL'] = 'Y'
    
    return adsl_derived


def derive_disposition_variables(adsl: pd.DataFrame) -> pd.DataFrame:
    """
    Derive disposition-related variables.
    
    Parameters
    ----------
    adsl : pd.DataFrame
        ADSL dataset
        
    Returns
    -------
    pd.DataFrame
        ADSL with derived disposition variables
    """
    adsl_derived = adsl.copy()
    
    # Discontinuation flag
    if 'DISCONFL' not in adsl_derived.columns:
        adsl_derived['DISCONFL'] = np.where(
            adsl_derived.get('DCSREAS', '') == 'COMPLETED', 'N', 'Y'
        )
    
    # Discontinuation reason coded
    if 'DCREASCD' not in adsl_derived.columns and 'DCSREAS' in adsl_derived.columns:
        reason_map = {
            'COMPLETED': 'COMPLETED',
            'ADVERSE EVENT': 'AE',
            'LACK OF EFFICACY': 'LACK_EFF',
            'WITHDREW CONSENT': 'WITHDREW',
            'LOST TO FOLLOW-UP': 'LTFU',
            'PROTOCOL VIOLATION': 'PROTOCOL'
        }
        adsl_derived['DCREASCD'] = adsl_derived['DCSREAS'].map(reason_map).fillna('OTHER')
    
    return adsl_derived


def derive_demographic_categories(adsl: pd.DataFrame) -> pd.DataFrame:
    """
    Derive demographic category variables for analysis.
    
    Parameters
    ----------
    adsl : pd.DataFrame
        ADSL dataset
        
    Returns
    -------
    pd.DataFrame
        ADSL with derived demographic categories
    """
    adsl_derived = adsl.copy()
    
    # Age categories
    if 'AGEGR1' not in adsl_derived.columns and 'AGE' in adsl_derived.columns:
        adsl_derived['AGEGR1'] = pd.cut(
            adsl_derived['AGE'],
            bins=[0, 65, 75, 999],
            labels=['<65', '65-74', '>=75'],
            right=False
        )
    
    # BMI categories if height and weight available
    if all(col in adsl_derived.columns for col in ['HEIGHT', 'WEIGHT']):
        if 'BMI' not in adsl_derived.columns:
            # BMI = weight(kg) / height(m)^2
            height_m = adsl_derived['HEIGHT'] / 100  # Convert cm to m
            adsl_derived['BMI'] = adsl_derived['WEIGHT'] / (height_m ** 2)
        
        if 'BMIGR1' not in adsl_derived.columns:
            adsl_derived['BMIGR1'] = pd.cut(
                adsl_derived['BMI'],
                bins=[0, 18.5, 25, 30, 999],
                labels=['Underweight', 'Normal', 'Overweight', 'Obese'],
                right=False
            )
    
    return adsl_derived


def merge_adam_datasets(adsl: pd.DataFrame, 
                       other_datasets: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Merge ADSL with other ADaM datasets and add treatment information.
    
    Parameters
    ----------
    adsl : pd.DataFrame
        ADSL dataset (subject-level)
    other_datasets : dict
        Dictionary of other ADaM datasets
        
    Returns
    -------
    dict
        Dictionary of merged datasets
    """
    merged_datasets = {}
    
    # Treatment variables to merge
    trt_vars = ['TRT01P', 'TRT01PN', 'TRT01A', 'TRT01AN', 'SAFFL', 'EFFFL', 'ITTFL']
    trt_vars = [var for var in trt_vars if var in adsl.columns]
    
    for name, dataset in other_datasets.items():
        if 'USUBJID' in dataset.columns:
            # Merge with ADSL to get treatment information
            merged = dataset.merge(
                adsl[['USUBJID'] + trt_vars],
                on='USUBJID',
                how='left'
            )
            merged_datasets[name] = merged
        else:
            merged_datasets[name] = dataset
    
    return merged_datasets


def create_analysis_dataset(data: pd.DataFrame,
                          analysis_var: str,
                          by_vars: List[str],
                          population_flag: str = 'SAFFL') -> pd.DataFrame:
    """
    Create analysis dataset for TLF generation.
    
    Parameters
    ----------
    data : pd.DataFrame
        Input dataset
    analysis_var : str
        Variable to analyze
    by_vars : list
        Variables to group by
    population_flag : str
        Population flag to filter by
        
    Returns
    -------
    pd.DataFrame
        Analysis dataset
    """
    # Filter by population
    if population_flag in data.columns:
        analysis_data = data[data[population_flag] == 'Y'].copy()
    else:
        analysis_data = data.copy()
    
    # Create analysis dataset
    if analysis_var in analysis_data.columns:
        result = analysis_data.groupby(by_vars + [analysis_var]).size().reset_index(name='n')
    else:
        result = analysis_data.groupby(by_vars).size().reset_index(name='n')
    
    return result


def format_ae_data(adae: pd.DataFrame, adsl: pd.DataFrame) -> pd.DataFrame:
    """
    Format adverse events data for analysis.
    
    Parameters
    ----------
    adae : pd.DataFrame
        ADAE dataset
    adsl : pd.DataFrame
        ADSL dataset
        
    Returns
    -------
    pd.DataFrame
        Formatted AE dataset
    """
    # Merge with ADSL for treatment information
    ae_data = adae.merge(
        adsl[['USUBJID', 'TRT01A', 'TRT01AN', 'SAFFL']],
        on='USUBJID',
        how='left'
    )
    
    # Filter safety population
    ae_data = ae_data[ae_data['SAFFL'] == 'Y']
    
    # Standardize AE terms
    if 'AEDECOD' in ae_data.columns:
        ae_data['AEDECOD'] = ae_data['AEDECOD'].str.title()
    
    if 'AEBODSYS' in ae_data.columns:
        ae_data['AEBODSYS'] = ae_data['AEBODSYS'].str.title()
    
    # Derive AE flags
    ae_data['DRUG_RELATED'] = ae_data.get('AEREL', '').isin(['POSSIBLE', 'PROBABLE', 'RELATED'])
    ae_data['SERIOUS'] = ae_data.get('AESER', 'N') == 'Y'
    ae_data['FATAL'] = ae_data.get('AEOUT', '') == 'FATAL'
    
    return ae_data


def format_lab_data(adlb: pd.DataFrame, adsl: pd.DataFrame) -> pd.DataFrame:
    """
    Format laboratory data for analysis.
    
    Parameters
    ----------
    adlb : pd.DataFrame
        ADLB dataset
    adsl : pd.DataFrame
        ADSL dataset
        
    Returns
    -------
    pd.DataFrame
        Formatted lab dataset
    """
    # Merge with ADSL for treatment information
    lab_data = adlb.merge(
        adsl[['USUBJID', 'TRT01P', 'TRT01PN', 'EFFFL']],
        on='USUBJID',
        how='left'
    )
    
    # Filter efficacy population
    lab_data = lab_data[lab_data['EFFFL'] == 'Y']
    
    # Ensure numeric analysis values
    if 'AVAL' in lab_data.columns:
        lab_data['AVAL'] = pd.to_numeric(lab_data['AVAL'], errors='coerce')
    
    if 'BASE' in lab_data.columns:
        lab_data['BASE'] = pd.to_numeric(lab_data['BASE'], errors='coerce')
    
    # Calculate change from baseline if not present
    if 'CHG' not in lab_data.columns and all(col in lab_data.columns for col in ['AVAL', 'BASE']):
        lab_data['CHG'] = lab_data['AVAL'] - lab_data['BASE']
    
    # Calculate percent change from baseline
    if 'PCHG' not in lab_data.columns and all(col in lab_data.columns for col in ['AVAL', 'BASE']):
        lab_data['PCHG'] = ((lab_data['AVAL'] - lab_data['BASE']) / lab_data['BASE']) * 100
    
    return lab_data


def create_summary_statistics(data: pd.DataFrame,
                            analysis_var: str,
                            by_var: str = 'TRT01P') -> pd.DataFrame:
    """
    Create summary statistics for continuous variables.
    
    Parameters
    ----------
    data : pd.DataFrame
        Input dataset
    analysis_var : str
        Variable to summarize
    by_var : str
        Grouping variable
        
    Returns
    -------
    pd.DataFrame
        Summary statistics
    """
    if analysis_var not in data.columns:
        raise ValueError(f"Analysis variable '{analysis_var}' not found in data")
    
    # Remove missing values
    clean_data = data.dropna(subset=[analysis_var])
    
    # Calculate statistics
    stats = clean_data.groupby(by_var)[analysis_var].agg([
        'count', 'mean', 'std', 'min', 'max', 'median'
    ]).round(2)
    
    # Calculate quartiles
    q25 = clean_data.groupby(by_var)[analysis_var].quantile(0.25)
    q75 = clean_data.groupby(by_var)[analysis_var].quantile(0.75)
    
    stats['q1'] = q25
    stats['q3'] = q75
    
    # Reset index to make treatment a column
    stats = stats.reset_index()
    
    return stats


def create_frequency_table(data: pd.DataFrame,
                         analysis_var: str,
                         by_var: str = 'TRT01P',
                         include_total: bool = True) -> pd.DataFrame:
    """
    Create frequency table for categorical variables.
    
    Parameters
    ----------
    data : pd.DataFrame
        Input dataset
    analysis_var : str
        Variable to tabulate
    by_var : str
        Grouping variable
    include_total : bool
        Whether to include total column
        
    Returns
    -------
    pd.DataFrame
        Frequency table
    """
    if analysis_var not in data.columns:
        raise ValueError(f"Analysis variable '{analysis_var}' not found in data")
    
    # Create frequency table
    freq_table = pd.crosstab(
        data[analysis_var],
        data[by_var],
        margins=include_total,
        margins_name='Total'
    )
    
    # Calculate percentages
    pct_table = pd.crosstab(
        data[analysis_var],
        data[by_var],
        normalize='columns',
        margins=include_total,
        margins_name='Total'
    ) * 100
    
    # Combine counts and percentages
    result_data = []
    for idx in freq_table.index:
        if idx == 'Total' and not include_total:
            continue
            
        row_data = {'Category': idx}
        for col in freq_table.columns:
            if col == 'Total' and not include_total:
                continue
                
            try:
                n = freq_table.loc[idx, col]
                pct = pct_table.loc[idx, col]
                row_data[f'{col}_n'] = n
                row_data[f'{col}_pct'] = f"{pct:.1f}"
                row_data[f'{col}_npct'] = f"{n} ({pct:.1f}%)"
            except KeyError:
                # Handle missing combinations
                row_data[f'{col}_n'] = 0
                row_data[f'{col}_pct'] = "0.0"
                row_data[f'{col}_npct'] = "0 (0.0%)"
        result_data.append(row_data)
    
    return pd.DataFrame(result_data)


def apply_cdisc_formats(data: pd.DataFrame, dataset_type: str) -> pd.DataFrame:
    """
    Apply standard CDISC formatting to datasets.
    
    Parameters
    ----------
    data : pd.DataFrame
        Input dataset
    dataset_type : str
        Type of dataset ('ADSL', 'ADAE', 'ADLB', etc.)
        
    Returns
    -------
    pd.DataFrame
        Formatted dataset
    """
    formatted_data = data.copy()
    
    # Standard date formatting
    date_vars = [col for col in formatted_data.columns if col.endswith('DT') or col.endswith('DTM')]
    for var in date_vars:
        if var in formatted_data.columns:
            formatted_data[var] = pd.to_datetime(formatted_data[var], errors='coerce')
    
    # Standard numeric formatting
    numeric_vars = [col for col in formatted_data.columns if col in ['AGE', 'AVAL', 'BASE', 'CHG']]
    for var in numeric_vars:
        if var in formatted_data.columns:
            formatted_data[var] = pd.to_numeric(formatted_data[var], errors='coerce')
    
    # Dataset-specific formatting
    if dataset_type.upper() == 'ADSL':
        # Ensure subject ID is string
        if 'USUBJID' in formatted_data.columns:
            formatted_data['USUBJID'] = formatted_data['USUBJID'].astype(str)
        
        # Standardize flag variables
        flag_vars = [col for col in formatted_data.columns if col.endswith('FL')]
        for var in flag_vars:
            formatted_data[var] = formatted_data[var].fillna('N')
    
    elif dataset_type.upper() == 'ADAE':
        # Standardize severity
        if 'AESEV' in formatted_data.columns:
            sev_map = {'1': 'MILD', '2': 'MODERATE', '3': 'SEVERE'}
            formatted_data['AESEV'] = formatted_data['AESEV'].replace(sev_map)
    
    return formatted_data


def validate_adam_structure(data: pd.DataFrame, dataset_type: str) -> Dict[str, Any]:
    """
    Validate ADaM dataset structure according to CDISC standards.
    
    Parameters
    ----------
    data : pd.DataFrame
        Dataset to validate
    dataset_type : str
        Type of dataset ('ADSL', 'ADAE', 'ADLB', etc.)
        
    Returns
    -------
    dict
        Validation results
    """
    validation_result = {
        'dataset_type': dataset_type.upper(),
        'valid': True,
        'errors': [],
        'warnings': [],
        'record_count': len(data),
        'variable_count': len(data.columns)
    }
    
    # Required variables by dataset type
    required_vars = {
        'ADSL': ['USUBJID', 'STUDYID', 'SUBJID'],
        'ADAE': ['USUBJID', 'AEDECOD'],
        'ADLB': ['USUBJID', 'PARAMCD', 'AVAL'],
        'ADCM': ['USUBJID', 'CMDECOD'],
        'ADVS': ['USUBJID', 'PARAMCD', 'AVAL']
    }
    
    dataset_required = required_vars.get(dataset_type.upper(), ['USUBJID'])
    
    # Check required variables
    missing_vars = [var for var in dataset_required if var not in data.columns]
    if missing_vars:
        validation_result['errors'].append(f"Missing required variables: {missing_vars}")
        validation_result['valid'] = False
    
    # Check for duplicate keys
    if dataset_type.upper() == 'ADSL' and 'USUBJID' in data.columns:
        duplicates = data['USUBJID'].duplicated().sum()
        if duplicates > 0:
            validation_result['errors'].append(f"Found {duplicates} duplicate subject IDs")
            validation_result['valid'] = False
    
    # Check data types
    if 'USUBJID' in data.columns and not data['USUBJID'].dtype == 'object':
        validation_result['warnings'].append("USUBJID should be character/string type")
    
    return validation_result 