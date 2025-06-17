"""
Enhanced Efficacy Analysis Functions for Clinical Trial Data
Extends existing efficacy capabilities with advanced statistical methods
"""

import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.formula.api import ols, mixedlm
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from typing import Dict, List, Optional, Tuple, Union
import warnings

def repeated_measures_analysis(data: pd.DataFrame,
                              subject_col: str,
                              treatment_col: str,
                              time_col: str,
                              response_col: str,
                              baseline_col: Optional[str] = None,
                              covariates: Optional[List[str]] = None) -> Dict:
    """
    Repeated measures analysis using mixed effects models
    
    Parameters:
    -----------
    data : pd.DataFrame
        Longitudinal data
    subject_col : str
        Subject identifier
    treatment_col : str
        Treatment group
    time_col : str
        Time/visit variable
    response_col : str
        Response variable
    baseline_col : str, optional
        Baseline value column
    covariates : List[str], optional
        Additional covariates
        
    Returns:
    --------
    Dict containing repeated measures analysis results
    """
    
    # Build formula for mixed effects model
    formula_parts = [response_col, '~', treatment_col, '+', time_col, '+', f'{treatment_col}*{time_col}']
    
    if baseline_col:
        formula_parts.extend(['+', baseline_col])
    
    if covariates:
        formula_parts.extend(['+'] + ['+'.join(covariates)])
    
    formula = ' '.join(formula_parts)
    
    # Fit mixed effects model
    try:
        model = mixedlm(formula, data, groups=data[subject_col]).fit()
        
        results = {
            'analysis_type': 'Repeated Measures Mixed Effects Analysis',
            'model_summary': model.summary(),
            'fixed_effects': model.fe_params,
            'random_effects': model.random_effects,
            'aic': model.aic,
            'bic': model.bic,
            'log_likelihood': model.llf,
            'formula': formula
        }
        
        # Extract treatment effects
        treatment_effects = {}
        for param in model.fe_params.index:
            if treatment_col in param:
                treatment_effects[param] = {
                    'estimate': model.fe_params[param],
                    'std_error': model.bse[param],
                    'p_value': model.pvalues[param],
                    'ci_lower': model.conf_int().loc[param, 0],
                    'ci_upper': model.conf_int().loc[param, 1]
                }
        
        results['treatment_effects'] = treatment_effects
        
    except Exception as e:
        results = {
            'analysis_type': 'Repeated Measures Mixed Effects Analysis',
            'error': str(e),
            'formula': formula
        }
    
    return results

def change_from_baseline_analysis(data: pd.DataFrame,
                                 subject_col: str,
                                 treatment_col: str,
                                 baseline_col: str,
                                 post_baseline_col: str,
                                 visit_col: Optional[str] = None,
                                 covariates: Optional[List[str]] = None) -> Dict:
    """
    Change from baseline analysis with ANCOVA
    
    Parameters:
    -----------
    data : pd.DataFrame
        Analysis data
    subject_col : str
        Subject identifier
    treatment_col : str
        Treatment group
    baseline_col : str
        Baseline value
    post_baseline_col : str
        Post-baseline value
    visit_col : str, optional
        Visit identifier for multiple timepoints
    covariates : List[str], optional
        Additional covariates
        
    Returns:
    --------
    Dict containing change from baseline analysis
    """
    
    # Calculate change from baseline
    data = data.copy()
    data['change_from_baseline'] = data[post_baseline_col] - data[baseline_col]
    
    results = {
        'analysis_type': 'Change from Baseline Analysis'
    }
    
    if visit_col:
        # Analysis by visit
        visit_results = {}
        for visit in data[visit_col].unique():
            visit_data = data[data[visit_col] == visit].copy()
            
            if len(visit_data) > 0:
                visit_analysis = _perform_ancova_analysis(
                    visit_data, 'change_from_baseline', treatment_col, 
                    baseline_col, covariates
                )
                visit_results[visit] = visit_analysis
        
        results['visit_results'] = visit_results
    else:
        # Overall analysis
        overall_analysis = _perform_ancova_analysis(
            data, 'change_from_baseline', treatment_col, 
            baseline_col, covariates
        )
        results['overall_analysis'] = overall_analysis
    
    return results

def _perform_ancova_analysis(data: pd.DataFrame,
                            response_col: str,
                            treatment_col: str,
                            baseline_col: str,
                            covariates: Optional[List[str]] = None) -> Dict:
    """
    Helper function to perform ANCOVA analysis
    """
    
    # Build formula
    formula_parts = [response_col, '~', treatment_col, '+', baseline_col]
    
    if covariates:
        formula_parts.extend(['+'] + ['+'.join(covariates)])
    
    formula = ' '.join(formula_parts)
    
    try:
        # Fit ANCOVA model
        model = ols(formula, data=data).fit()
        anova_table = anova_lm(model, typ=2)
        
        # Extract treatment effects
        treatment_params = {param: {'estimate': model.params[param],
                                   'std_error': model.bse[param],
                                   'p_value': model.pvalues[param],
                                   'ci_lower': model.conf_int().loc[param, 0],
                                   'ci_upper': model.conf_int().loc[param, 1]}
                           for param in model.params.index if treatment_col in param}
        
        # Calculate least squares means
        treatment_groups = data[treatment_col].unique()
        ls_means = {}
        
        for group in treatment_groups:
            group_data = data[data[treatment_col] == group]
            if len(group_data) > 0:
                # Predict using mean baseline and covariates
                pred_data = pd.DataFrame({
                    treatment_col: [group],
                    baseline_col: [data[baseline_col].mean()]
                })
                
                if covariates:
                    for cov in covariates:
                        if cov in data.columns:
                            pred_data[cov] = [data[cov].mean()]
                
                try:
                    ls_mean = model.predict(pred_data)[0]
                    ls_means[group] = ls_mean
                except:
                    ls_means[group] = group_data[response_col].mean()
        
        analysis_result = {
            'model_summary': model.summary(),
            'anova_table': anova_table,
            'treatment_effects': treatment_params,
            'ls_means': ls_means,
            'r_squared': model.rsquared,
            'adj_r_squared': model.rsquared_adj,
            'formula': formula
        }
        
    except Exception as e:
        analysis_result = {
            'error': str(e),
            'formula': formula
        }
    
    return analysis_result

def responder_analysis(data: pd.DataFrame,
                      subject_col: str,
                      treatment_col: str,
                      response_col: str,
                      threshold: float,
                      direction: str = 'greater') -> Dict:
    """
    Responder analysis (binary endpoint based on threshold)
    
    Parameters:
    -----------
    data : pd.DataFrame
        Analysis data
    subject_col : str
        Subject identifier
    treatment_col : str
        Treatment group
    response_col : str
        Continuous response variable
    threshold : float
        Response threshold
    direction : str
        'greater' or 'less' than threshold
        
    Returns:
    --------
    Dict containing responder analysis results
    """
    
    # Create responder variable
    data = data.copy()
    if direction == 'greater':
        data['responder'] = (data[response_col] >= threshold).astype(int)
    else:
        data['responder'] = (data[response_col] <= threshold).astype(int)
    
    # Calculate response rates by treatment
    response_rates = {}
    for treatment in data[treatment_col].unique():
        trt_data = data[data[treatment_col] == treatment]
        
        n_total = len(trt_data)
        n_responders = trt_data['responder'].sum()
        response_rate = n_responders / n_total if n_total > 0 else 0
        
        # Calculate confidence interval for proportion
        from scipy.stats import binom
        ci_lower, ci_upper = binom.interval(0.95, n_total, response_rate) / n_total
        
        response_rates[treatment] = {
            'n_total': n_total,
            'n_responders': n_responders,
            'response_rate': response_rate,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper
        }
    
    # Perform chi-square test if multiple treatments
    treatments = list(data[treatment_col].unique())
    if len(treatments) >= 2:
        contingency_table = pd.crosstab(data[treatment_col], data['responder'])
        chi2_stat, p_value, dof, expected = stats.chi2_contingency(contingency_table)
        
        statistical_test = {
            'test_type': 'Chi-square test',
            'chi2_statistic': chi2_stat,
            'p_value': p_value,
            'degrees_of_freedom': dof,
            'contingency_table': contingency_table
        }
    else:
        statistical_test = None
    
    results = {
        'analysis_type': 'Responder Analysis',
        'threshold': threshold,
        'direction': direction,
        'response_rates': response_rates,
        'statistical_test': statistical_test
    }
    
    return results