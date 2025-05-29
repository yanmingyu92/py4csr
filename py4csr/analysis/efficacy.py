"""
Efficacy analysis functions for clinical trial data.

This module provides functions for performing efficacy analyses
including ANCOVA and survival analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import warnings


def ancova_analysis(data: pd.DataFrame,
                   endpoint: str,
                   treatment: str,
                   baseline: Optional[str] = None,
                   covariates: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Perform ANCOVA analysis for efficacy endpoint.
    
    Parameters
    ----------
    data : pd.DataFrame
        Input dataset
    endpoint : str
        Endpoint variable name
    treatment : str
        Treatment variable name
    baseline : str, optional
        Baseline value variable name
    covariates : list of str, optional
        Additional covariates
        
    Returns
    -------
    dict
        ANCOVA results
    """
    try:
        import statsmodels.api as sm
        from statsmodels.formula.api import ols
    except ImportError:
        raise ImportError("statsmodels is required for ANCOVA analysis")
    
    # Prepare formula
    formula_parts = [endpoint, "~", treatment]
    
    if baseline:
        formula_parts.extend(["+", baseline])
    
    if covariates:
        for cov in covariates:
            formula_parts.extend(["+", cov])
    
    formula = " ".join(formula_parts)
    
    # Fit model
    try:
        model = ols(formula, data=data).fit()
        
        results = {
            'formula': formula,
            'n_obs': model.nobs,
            'r_squared': model.rsquared,
            'f_statistic': model.fvalue,
            'f_pvalue': model.f_pvalue,
            'coefficients': model.params.to_dict(),
            'pvalues': model.pvalues.to_dict(),
            'conf_int': model.conf_int().to_dict(),
            'residuals': model.resid,
            'fitted_values': model.fittedvalues
        }
        
        return results
        
    except Exception as e:
        return {'error': str(e)}


def create_efficacy_table(ancova_results):
    """
    Create efficacy table from ANCOVA results.
    
    Parameters
    ----------
    ancova_results : dict
        Dictionary containing ANCOVA analysis results
        
    Returns
    -------
    pandas.DataFrame
        Formatted efficacy table
    """
    import pandas as pd
    
    # Extract results
    model_summary = ancova_results.get('model_summary', {})
    ls_means = ancova_results.get('ls_means', {})
    comparisons = ancova_results.get('comparisons', {})
    
    efficacy_data = []
    
    # LS Means
    if ls_means:
        for treatment, results in ls_means.items():
            efficacy_data.append({
                'Parameter': f'LS Mean - {treatment}',
                'Estimate': f"{results.get('estimate', 0):.2f}",
                'CI_Lower': f"{results.get('ci_lower', 0):.2f}",
                'CI_Upper': f"{results.get('ci_upper', 0):.2f}",
                'P_value': f"{results.get('p_value', 1):.4f}"
            })
    
    # Treatment comparisons
    if comparisons:
        for comparison, results in comparisons.items():
            efficacy_data.append({
                'Parameter': f'Difference - {comparison}',
                'Estimate': f"{results.get('estimate', 0):.2f}",
                'CI_Lower': f"{results.get('ci_lower', 0):.2f}",
                'CI_Upper': f"{results.get('ci_upper', 0):.2f}",
                'P_value': f"{results.get('p_value', 1):.4f}"
            })
    
    # Overall model test
    if model_summary:
        efficacy_data.append({
            'Parameter': 'Overall Treatment Effect',
            'Estimate': '-',
            'CI_Lower': '-',
            'CI_Upper': '-',
            'P_value': f"{model_summary.get('overall_p', 1):.4f}"
        })
    
    return pd.DataFrame(efficacy_data)


def survival_analysis(data: pd.DataFrame,
                     time_var: str,
                     event_var: str,
                     treatment_var: str) -> Dict[str, Any]:
    """
    Perform survival analysis (Kaplan-Meier).
    
    Parameters
    ----------
    data : pd.DataFrame
        Input dataset
    time_var : str
        Time to event variable
    event_var : str
        Event indicator variable
    treatment_var : str
        Treatment group variable
        
    Returns
    -------
    dict
        Survival analysis results
    """
    try:
        from lifelines import KaplanMeierFitter
        from lifelines.statistics import logrank_test
    except ImportError:
        raise ImportError("lifelines is required for survival analysis")
    
    results = {}
    
    # Fit Kaplan-Meier for each treatment group
    treatment_groups = data[treatment_var].unique()
    
    for group in treatment_groups:
        group_data = data[data[treatment_var] == group]
        
        kmf = KaplanMeierFitter()
        kmf.fit(group_data[time_var], group_data[event_var], label=group)
        
        results[group] = {
            'survival_function': kmf.survival_function_,
            'median_survival': kmf.median_survival_time_,
            'confidence_interval': kmf.confidence_interval_
        }
    
    # Log-rank test if two groups
    if len(treatment_groups) == 2:
        group1_data = data[data[treatment_var] == treatment_groups[0]]
        group2_data = data[data[treatment_var] == treatment_groups[1]]
        
        logrank_result = logrank_test(
            group1_data[time_var], group2_data[time_var],
            group1_data[event_var], group2_data[event_var]
        )
        
        results['logrank_test'] = {
            'test_statistic': logrank_result.test_statistic,
            'p_value': logrank_result.p_value
        }
    
    return results 