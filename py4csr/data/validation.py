"""
Data validation functions for clinical trial datasets.

This module provides validation functions for CDISC ADaM datasets
to ensure data quality and compliance with standards.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Any, Tuple
import warnings


def validate_adsl(data: pd.DataFrame, strict: bool = False) -> Dict[str, Any]:
    """
    Validate ADSL (Subject Level Analysis Dataset) structure and content.
    
    Parameters
    ----------
    data : pd.DataFrame
        ADSL dataset to validate
    strict : bool, default False
        Whether to use strict validation rules
        
    Returns
    -------
    dict
        Validation report with issues and summary
    """
    
    validation_report = {
        'dataset': 'ADSL',
        'n_subjects': len(data),
        'n_variables': len(data.columns),
        'issues': [],
        'warnings': [],
        'passed': True
    }
    
    # Required variables for ADSL
    required_vars = ['USUBJID', 'STUDYID', 'SUBJID']
    recommended_vars = ['TRT01P', 'TRT01A', 'AGE', 'SEX', 'RACE', 'SAFFL', 'EFFFL']
    
    # Check required variables
    missing_required = [var for var in required_vars if var not in data.columns]
    if missing_required:
        validation_report['issues'].append(f"Missing required variables: {missing_required}")
        validation_report['passed'] = False
    
    # Check recommended variables
    missing_recommended = [var for var in recommended_vars if var not in data.columns]
    if missing_recommended:
        validation_report['warnings'].append(f"Missing recommended variables: {missing_recommended}")
    
    # Check for duplicate subjects
    if 'USUBJID' in data.columns:
        duplicates = data['USUBJID'].duplicated().sum()
        if duplicates > 0:
            validation_report['issues'].append(f"Found {duplicates} duplicate subject IDs")
            validation_report['passed'] = False
    
    # Check treatment variables
    if 'TRT01P' in data.columns:
        trt_missing = data['TRT01P'].isnull().sum()
        if trt_missing > 0:
            validation_report['warnings'].append(f"Missing planned treatment for {trt_missing} subjects")
        
        # Check for reasonable number of treatment groups
        n_treatments = data['TRT01P'].nunique()
        if n_treatments > 10:
            validation_report['warnings'].append(f"Unusually high number of treatment groups: {n_treatments}")
    
    # Check age variable
    if 'AGE' in data.columns:
        age_issues = _validate_age_variable(data['AGE'])
        validation_report['warnings'].extend(age_issues)
    
    # Check sex variable
    if 'SEX' in data.columns:
        sex_issues = _validate_sex_variable(data['SEX'])
        validation_report['warnings'].extend(sex_issues)
    
    # Check flag variables
    flag_vars = [col for col in data.columns if col.endswith('FL')]
    for flag_var in flag_vars:
        flag_issues = _validate_flag_variable(data[flag_var], flag_var)
        validation_report['warnings'].extend(flag_issues)
    
    return validation_report


def validate_adae(data: pd.DataFrame, strict: bool = False) -> Dict[str, Any]:
    """
    Validate ADAE (Adverse Events Analysis Dataset) structure and content.
    
    Parameters
    ----------
    data : pd.DataFrame
        ADAE dataset to validate
    strict : bool, default False
        Whether to use strict validation rules
        
    Returns
    -------
    dict
        Validation report with issues and summary
    """
    
    validation_report = {
        'dataset': 'ADAE',
        'n_records': len(data),
        'n_subjects': data['USUBJID'].nunique() if 'USUBJID' in data.columns else 0,
        'n_variables': len(data.columns),
        'issues': [],
        'warnings': [],
        'passed': True
    }
    
    # Required variables for ADAE
    required_vars = ['USUBJID', 'AEDECOD', 'AESTDT']
    recommended_vars = ['TRTA', 'AESEV', 'AEREL', 'AEOUT', 'AEBODSYS']
    
    # Check required variables
    missing_required = [var for var in required_vars if var not in data.columns]
    if missing_required:
        validation_report['issues'].append(f"Missing required variables: {missing_required}")
        validation_report['passed'] = False
    
    # Check recommended variables
    missing_recommended = [var for var in recommended_vars if var not in recommended_vars if var not in data.columns]
    if missing_recommended:
        validation_report['warnings'].append(f"Missing recommended variables: {missing_recommended}")
    
    # Check for missing AE terms
    if 'AEDECOD' in data.columns:
        missing_terms = data['AEDECOD'].isnull().sum()
        if missing_terms > 0:
            validation_report['issues'].append(f"Missing AE terms for {missing_terms} records")
            validation_report['passed'] = False
    
    # Check severity coding
    if 'AESEV' in data.columns:
        sev_issues = _validate_severity_variable(data['AESEV'])
        validation_report['warnings'].extend(sev_issues)
    
    # Check relationship coding
    if 'AEREL' in data.columns:
        rel_issues = _validate_relationship_variable(data['AEREL'])
        validation_report['warnings'].extend(rel_issues)
    
    return validation_report


def validate_adlb(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate ADLB (Laboratory Analysis Dataset) structure and content.
    
    Parameters
    ----------
    data : pd.DataFrame
        ADLB dataset to validate
        
    Returns
    -------
    dict
        Validation results with status and details
    """
    validation_result = {
        'dataset': 'ADLB',
        'valid': True,
        'errors': [],
        'warnings': [],
        'record_count': len(data)
    }
    
    # Required ADLB variables
    required_vars = [
        'USUBJID', 'PARAMCD', 'PARAM', 'AVAL', 'AVALU',
        'VISIT', 'VISITNUM', 'ADT', 'ATM', 'ATPT'
    ]
    
    # Check required variables
    missing_vars = [var for var in required_vars if var not in data.columns]
    if missing_vars:
        validation_result['errors'].append(f"Missing required variables: {missing_vars}")
        validation_result['valid'] = False
    
    if not data.empty:
        # Check USUBJID format
        if 'USUBJID' in data.columns:
            invalid_subjects = data[data['USUBJID'].isna() | (data['USUBJID'] == '')]
            if len(invalid_subjects) > 0:
                validation_result['errors'].append(f"Found {len(invalid_subjects)} records with invalid USUBJID")
        
        # Check PARAMCD values
        if 'PARAMCD' in data.columns:
            valid_paramcds = ['ALT', 'AST', 'BILI', 'BUN', 'CREAT', 'GLUC', 'HBA1C', 'HDL', 'LDL', 'TRIG']
            invalid_params = data[~data['PARAMCD'].isin(valid_paramcds) & data['PARAMCD'].notna()]
            if len(invalid_params) > 0:
                validation_result['warnings'].append(f"Found {len(invalid_params)} records with non-standard PARAMCD values")
        
        # Check AVAL (analysis value) is numeric
        if 'AVAL' in data.columns:
            non_numeric_aval = data[data['AVAL'].notna() & ~pd.to_numeric(data['AVAL'], errors='coerce').notna()]
            if len(non_numeric_aval) > 0:
                validation_result['errors'].append(f"Found {len(non_numeric_aval)} records with non-numeric AVAL")
                validation_result['valid'] = False
    
    return validation_result


def _validate_age_variable(age_series: pd.Series) -> List[str]:
    """Validate age variable."""
    issues = []
    
    # Check for reasonable age range
    if age_series.min() < 0:
        issues.append("Negative age values found")
    
    if age_series.max() > 120:
        issues.append("Age values > 120 found")
    
    # Check for missing ages
    missing_age = age_series.isnull().sum()
    if missing_age > 0:
        issues.append(f"Missing age for {missing_age} subjects")
    
    return issues


def _validate_sex_variable(sex_series: pd.Series) -> List[str]:
    """Validate sex variable."""
    issues = []
    
    valid_sex_values = {'M', 'F', 'Male', 'Female', 'MALE', 'FEMALE'}
    invalid_sex = sex_series[~sex_series.isin(valid_sex_values) & sex_series.notna()]
    
    if len(invalid_sex) > 0:
        issues.append(f"Invalid sex values found: {invalid_sex.unique()}")
    
    missing_sex = sex_series.isnull().sum()
    if missing_sex > 0:
        issues.append(f"Missing sex for {missing_sex} subjects")
    
    return issues


def _validate_flag_variable(flag_series: pd.Series, var_name: str) -> List[str]:
    """Validate flag variables (should be Y/N)."""
    issues = []
    
    valid_flag_values = {'Y', 'N', 'y', 'n'}
    invalid_flags = flag_series[~flag_series.isin(valid_flag_values) & flag_series.notna()]
    
    if len(invalid_flags) > 0:
        issues.append(f"Invalid {var_name} values found: {invalid_flags.unique()}")
    
    return issues


def _validate_severity_variable(sev_series: pd.Series) -> List[str]:
    """Validate AE severity variable."""
    issues = []
    
    valid_severity = {'MILD', 'MODERATE', 'SEVERE', 'Mild', 'Moderate', 'Severe', '1', '2', '3'}
    invalid_sev = sev_series[~sev_series.isin(valid_severity) & sev_series.notna()]
    
    if len(invalid_sev) > 0:
        issues.append(f"Invalid severity values found: {invalid_sev.unique()}")
    
    return issues


def _validate_relationship_variable(rel_series: pd.Series) -> List[str]:
    """Validate AE relationship variable."""
    issues = []
    
    valid_relationship = {'RELATED', 'NOT RELATED', 'POSSIBLY RELATED', 'PROBABLY RELATED',
                         'Related', 'Not Related', 'Possibly Related', 'Probably Related'}
    invalid_rel = rel_series[~rel_series.isin(valid_relationship) & rel_series.notna()]
    
    if len(invalid_rel) > 0:
        issues.append(f"Invalid relationship values found: {invalid_rel.unique()}")
    
    return issues


def _validate_analysis_values(aval_series: pd.Series) -> List[str]:
    """Validate analysis values."""
    issues = []
    
    # Check for infinite values
    if np.isinf(aval_series).any():
        issues.append("Infinite values found in analysis values")
    
    # Check for extremely large values
    if aval_series.max() > 1e10:
        issues.append("Extremely large analysis values found")
    
    return issues


def run_full_validation(datasets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """
    Run validation on multiple datasets.
    
    Parameters
    ----------
    datasets : dict
        Dictionary with dataset names as keys and DataFrames as values
        
    Returns
    -------
    dict
        Complete validation report
    """
    
    full_report = {
        'validation_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
        'datasets_validated': list(datasets.keys()),
        'overall_passed': True,
        'dataset_reports': {}
    }
    
    validation_functions = {
        'adsl': validate_adsl,
        'adae': validate_adae, 
        'adlb': validate_adlb
    }
    
    for dataset_name, dataset in datasets.items():
        dataset_lower = dataset_name.lower()
        
        if dataset_lower in validation_functions:
            report = validation_functions[dataset_lower](dataset)
        else:
            # Generic validation for unknown datasets
            report = _generic_validation(dataset, dataset_name)
        
        full_report['dataset_reports'][dataset_name] = report
        
        if not report['passed']:
            full_report['overall_passed'] = False
    
    return full_report


def _generic_validation(data: pd.DataFrame, dataset_name: str) -> Dict[str, Any]:
    """Generic validation for unknown datasets."""
    
    return {
        'dataset': dataset_name,
        'n_records': len(data),
        'n_variables': len(data.columns),
        'issues': [],
        'warnings': ['Generic validation applied - dataset type not recognized'],
        'passed': True
    } 