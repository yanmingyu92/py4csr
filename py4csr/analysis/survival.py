"""
Survival Analysis Functions for Clinical Trial Data
Implements advanced survival analysis capabilities following RRG design principles
"""

import pandas as pd
import numpy as np
from scipy import stats
from lifelines import KaplanMeierFitter, CoxPHFitter
from lifelines.statistics import pairwise_logrank_test, logrank_test
from typing import Dict, List, Optional, Tuple, Union
import warnings

def kaplan_meier_analysis(data: pd.DataFrame,
                         duration_col: str,
                         event_col: str,
                         group_col: Optional[str] = None,
                         confidence_level: float = 0.95,
                         timeline: Optional[List[float]] = None) -> Dict:
    """
    Perform Kaplan-Meier survival analysis (RRG survival equivalent)
    
    Parameters:
    -----------
    data : pd.DataFrame
        Input dataset
    duration_col : str
        Time to event column name
    event_col : str
        Event indicator column (1=event, 0=censored)
    group_col : str, optional
        Grouping variable for comparison
    confidence_level : float
        Confidence level for survival curves
    timeline : List[float], optional
        Specific time points for survival estimates
        
    Returns:
    --------
    Dict containing survival analysis results
    """
    
    results = {
        'analysis_type': 'Kaplan-Meier Survival Analysis',
        'confidence_level': confidence_level
    }
    
    if group_col is None:
        # Single group analysis
        kmf = KaplanMeierFitter(alpha=1-confidence_level)
        kmf.fit(data[duration_col], data[event_col])
        
        results.update({
            'survival_function': kmf.survival_function_,
            'confidence_interval': kmf.confidence_interval_,
            'median_survival': kmf.median_survival_time_,
            'median_survival_ci': kmf.confidence_interval_survival_times_,
            'event_table': kmf.event_table
        })
        
        if timeline:
            survival_at_times = kmf.survival_function_at_times(timeline)
            results['survival_at_times'] = survival_at_times
            
    else:
        # Group comparison analysis
        groups = data[group_col].unique()
        group_results = {}
        survival_functions = {}
        
        for group in groups:
            group_data = data[data[group_col] == group]
            if len(group_data) > 0:
                kmf = KaplanMeierFitter(alpha=1-confidence_level, label=str(group))
                kmf.fit(group_data[duration_col], group_data[event_col])
                
                group_results[group] = {
                    'median_survival': kmf.median_survival_time_,
                    'median_survival_ci': kmf.confidence_interval_survival_times_,
                    'event_table': kmf.event_table
                }
                survival_functions[group] = kmf.survival_function_
        
        # Perform log-rank test
        if len(groups) == 2:
            group1_data = data[data[group_col] == groups[0]]
            group2_data = data[data[group_col] == groups[1]]
            
            logrank_result = logrank_test(
                group1_data[duration_col], group2_data[duration_col],
                group1_data[event_col], group2_data[event_col]
            )
            
            results['logrank_test'] = {
                'test_statistic': logrank_result.test_statistic,
                'p_value': logrank_result.p_value,
                'degrees_of_freedom': 1
            }
        elif len(groups) > 2:
            # Pairwise log-rank tests
            pairwise_result = pairwise_logrank_test(
                data[duration_col], data[group_col], data[event_col]
            )
            results['pairwise_logrank'] = pairwise_result
        
        results.update({
            'group_results': group_results,
            'survival_functions': survival_functions
        })
        
        if timeline:
            survival_at_times = {}
            for group in groups:
                group_data = data[data[group_col] == group]
                if len(group_data) > 0:
                    kmf = KaplanMeierFitter(alpha=1-confidence_level)
                    kmf.fit(group_data[duration_col], group_data[event_col])
                    survival_at_times[group] = kmf.survival_function_at_times(timeline)
            results['survival_at_times'] = survival_at_times
    
    return results

def cox_regression_analysis(data: pd.DataFrame,
                           duration_col: str,
                           event_col: str,
                           covariates: List[str],
                           strata: Optional[List[str]] = None) -> Dict:
    """
    Perform Cox proportional hazards regression analysis
    
    Parameters:
    -----------
    data : pd.DataFrame
        Input dataset
    duration_col : str
        Time to event column name
    event_col : str
        Event indicator column
    covariates : List[str]
        List of covariate column names
    strata : List[str], optional
        Stratification variables
        
    Returns:
    --------
    Dict containing Cox regression results
    """
    
    # Prepare data for Cox regression
    cox_data = data[[duration_col, event_col] + covariates].copy()
    if strata:
        cox_data = cox_data.join(data[strata])
    
    # Remove missing values
    cox_data = cox_data.dropna()
    
    # Fit Cox model
    cph = CoxPHFitter()
    if strata:
        cph.fit(cox_data, duration_col=duration_col, event_col=event_col, strata=strata)
    else:
        cph.fit(cox_data, duration_col=duration_col, event_col=event_col)
    
    # Extract results
    results = {
        'analysis_type': 'Cox Proportional Hazards Regression',
        'model_summary': cph.summary,
        'hazard_ratios': cph.hazard_ratios_,
        'confidence_intervals': cph.confidence_intervals_,
        'p_values': cph.summary['p'],
        'concordance_index': cph.concordance_index_,
        'log_likelihood': cph.log_likelihood_,
        'aic': cph.AIC_,
        'partial_aic': cph.AIC_partial_
    }
    
    # Proportional hazards test
    try:
        ph_test = cph.check_assumptions(cox_data, show_plots=False)
        results['proportional_hazards_test'] = ph_test
    except Exception as e:
        results['proportional_hazards_test'] = {'error': str(e)}
    
    return results

def time_to_event_summary(data: pd.DataFrame,
                         duration_col: str,
                         event_col: str,
                         group_col: Optional[str] = None,
                         percentiles: List[float] = [0.25, 0.5, 0.75]) -> Dict:
    """
    Generate time-to-event summary statistics
    
    Parameters:
    -----------
    data : pd.DataFrame
        Input dataset
    duration_col : str
        Time to event column name
    event_col : str
        Event indicator column
    group_col : str, optional
        Grouping variable
    percentiles : List[float]
        Percentiles to calculate
        
    Returns:
    --------
    Dict containing summary statistics
    """
    
    def calculate_group_summary(group_data):
        n_total = len(group_data)
        n_events = group_data[event_col].sum()
        n_censored = n_total - n_events
        
        # Kaplan-Meier for percentile estimation
        kmf = KaplanMeierFitter()
        kmf.fit(group_data[duration_col], group_data[event_col])
        
        percentile_estimates = {}
        for p in percentiles:
            try:
                percentile_estimates[f'percentile_{int(p*100)}'] = kmf.percentile(p)
            except:
                percentile_estimates[f'percentile_{int(p*100)}'] = np.nan
        
        return {
            'n_total': n_total,
            'n_events': n_events,
            'n_censored': n_censored,
            'event_rate': n_events / n_total if n_total > 0 else np.nan,
            'median_followup': group_data[duration_col].median(),
            'max_followup': group_data[duration_col].max(),
            'min_followup': group_data[duration_col].min(),
            **percentile_estimates
        }
    
    if group_col is None:
        results = {
            'analysis_type': 'Time-to-Event Summary',
            'overall': calculate_group_summary(data)
        }
    else:
        group_summaries = {}
        for group in data[group_col].unique():
            group_data = data[data[group_col] == group]
            if len(group_data) > 0:
                group_summaries[group] = calculate_group_summary(group_data)
        
        results = {
            'analysis_type': 'Time-to-Event Summary by Group',
            'group_summaries': group_summaries
        }
    
    return results