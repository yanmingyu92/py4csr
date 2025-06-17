"""
Binomial Analysis Functions for Clinical Trial Data
Implements RRG binomial analysis equivalent: rrg_binom
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import binom
from statsmodels.stats.proportion import proportion_confint, proportions_ztest
from typing import Dict, List, Optional, Tuple, Union

def binomial_proportion_ci(successes: int,
                          trials: int,
                          confidence_level: float = 0.95,
                          method: str = 'wilson') -> Dict:
    """
    Calculate confidence interval for binomial proportion (equivalent to rrg_binom)
    
    Parameters:
    -----------
    successes : int
        Number of successes
    trials : int
        Number of trials
    confidence_level : float
        Confidence level (default 0.95)
    method : str
        Method for CI calculation ('wilson', 'wald', 'agresti_coull', 'beta')
        
    Returns:
    --------
    Dict containing proportion and confidence interval
    """
    
    if trials == 0:
        return {
            'proportion': np.nan,
            'lower_ci': np.nan,
            'upper_ci': np.nan,
            'method': method,
            'confidence_level': confidence_level
        }
    
    proportion = successes / trials
    alpha = 1 - confidence_level
    
    lower_ci, upper_ci = proportion_confint(successes, trials, alpha=alpha, method=method)
    
    result = {
        'successes': successes,
        'trials': trials,
        'proportion': proportion,
        'lower_ci': lower_ci,
        'upper_ci': upper_ci,
        'method': method,
        'confidence_level': confidence_level
    }
    
    return result

def binomial_test(successes: int,
                 trials: int,
                 expected_prob: float = 0.5,
                 alternative: str = 'two-sided') -> Dict:
    """
    Perform exact binomial test
    
    Parameters:
    -----------
    successes : int
        Number of successes
    trials : int
        Number of trials
    expected_prob : float
        Expected probability under null hypothesis
    alternative : str
        Alternative hypothesis ('two-sided', 'less', 'greater')
        
    Returns:
    --------
    Dict containing test results
    """
    
    p_value = stats.binom_test(successes, trials, expected_prob, alternative=alternative)
    observed_prob = successes / trials if trials > 0 else np.nan
    
    result = {
        'test_type': 'Exact binomial test',
        'successes': successes,
        'trials': trials,
        'observed_proportion': observed_prob,
        'expected_proportion': expected_prob,
        'p_value': p_value,
        'alternative': alternative
    }
    
    return result

def proportion_difference_test(data: pd.DataFrame,
                              group_var: str,
                              response_var: str,
                              group1: str,
                              group2: str,
                              confidence_level: float = 0.95) -> Dict:
    """
    Test difference between two proportions
    
    Parameters:
    -----------
    data : pd.DataFrame
        Input dataset
    group_var : str
        Grouping variable name
    response_var : str
        Response variable name (binary)
    group1 : str
        First group value
    group2 : str
        Second group value
    confidence_level : float
        Confidence level for CI
        
    Returns:
    --------
    Dict containing test results
    """
    
    group1_data = data[data[group_var] == group1]
    group2_data = data[data[group_var] == group2]
    
    # Calculate proportions
    n1 = len(group1_data)
    n2 = len(group2_data)
    x1 = group1_data[response_var].sum()
    x2 = group2_data[response_var].sum()
    
    p1 = x1 / n1 if n1 > 0 else np.nan
    p2 = x2 / n2 if n2 > 0 else np.nan
    
    # Perform z-test
    counts = np.array([x1, x2])
    nobs = np.array([n1, n2])
    
    z_stat, p_value = proportions_ztest(counts, nobs)
    
    # Calculate difference and CI
    diff = p1 - p2
    
    # CI for difference using normal approximation
    se_diff = np.sqrt(p1*(1-p1)/n1 + p2*(1-p2)/n2)
    alpha = 1 - confidence_level
    z_critical = stats.norm.ppf(1 - alpha/2)
    
    diff_lower_ci = diff - z_critical * se_diff
    diff_upper_ci = diff + z_critical * se_diff
    
    result = {
        'test_type': 'Two-proportion z-test',
        'group1': group1,
        'group2': group2,
        'n1': n1,
        'n2': n2,
        'x1': x1,
        'x2': x2,
        'proportion1': p1,
        'proportion2': p2,
        'difference': diff,
        'difference_ci_lower': diff_lower_ci,
        'difference_ci_upper': diff_upper_ci,
        'z_statistic': z_stat,
        'p_value': p_value,
        'confidence_level': confidence_level
    }
    
    return result