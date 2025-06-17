import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Any, Optional

def geometric_mean_analysis(data: pd.DataFrame, 
                          variable: str,
                          treatment_var: Optional[str] = None,
                          grouping_vars: Optional[list] = None) -> Dict[str, Any]:
    """
    Calculate geometric mean statistics (equivalent to rrg_gmean)
    """
    # Filter positive values only
    positive_data = data[data[variable] > 0].copy()
    
    if positive_data.empty:
        return {'error': 'No positive values found for geometric mean calculation'}
    
    # Calculate log-transformed values
    positive_data['log_var'] = np.log(positive_data[variable])
    
    grouping_cols = []
    if treatment_var:
        grouping_cols.append(treatment_var)
    if grouping_vars:
        grouping_cols.extend(grouping_vars)
    
    if grouping_cols:
        grouped = positive_data.groupby(grouping_cols)['log_var']
        results = {
            'geometric_mean': np.exp(grouped.mean()),
            'geometric_se': np.exp(grouped.std() / np.sqrt(grouped.count())),
            'n': grouped.count()
        }
    else:
        log_mean = positive_data['log_var'].mean()
        log_se = positive_data['log_var'].std() / np.sqrt(len(positive_data))
        results = {
            'geometric_mean': np.exp(log_mean),
            'geometric_se': np.exp(log_se),
            'n': len(positive_data)
        }
    
    return results

def wald_test_proportions(data: pd.DataFrame,
                         treatment_var: str,
                         outcome_var: str,
                         reference_group: str,
                         confidence_level: float = 0.95) -> Dict[str, Any]:
    """
    Perform Wald test for proportion differences (equivalent to rrg_wald)
    """
    # Calculate proportions by treatment group
    prop_table = data.groupby(treatment_var)[outcome_var].agg(['sum', 'count'])
    prop_table['proportion'] = prop_table['sum'] / prop_table['count']
    
    if reference_group not in prop_table.index:
        return {'error': f'Reference group {reference_group} not found'}
    
    ref_prop = prop_table.loc[reference_group, 'proportion']
    ref_n = prop_table.loc[reference_group, 'count']
    
    results = {}
    alpha = 1 - confidence_level
    z_critical = stats.norm.ppf(1 - alpha/2)
    
    for group in prop_table.index:
        if group != reference_group:
            group_prop = prop_table.loc[group, 'proportion']
            group_n = prop_table.loc[group, 'count']
            
            # Calculate difference and standard error
            diff = group_prop - ref_prop
            se_diff = np.sqrt((ref_prop * (1 - ref_prop) / ref_n) + 
                             (group_prop * (1 - group_prop) / group_n))
            
            # Wald test statistic
            z_stat = diff / se_diff if se_diff > 0 else 0
            p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
            
            # Confidence interval for difference
            ci_lower = diff - z_critical * se_diff
            ci_upper = diff + z_critical * se_diff
            
            results[f'{group}_vs_{reference_group}'] = {
                'difference': diff,
                'standard_error': se_diff,
                'z_statistic': z_stat,
                'p_value': p_value,
                'ci_lower': ci_lower,
                'ci_upper': ci_upper,
                'confidence_level': confidence_level
            }
    
    return results

def exact_binomial_ci(successes: int, trials: int, 
                     confidence_level: float = 0.95) -> Dict[str, Any]:
    """
    Calculate exact binomial confidence intervals (equivalent to rrg_binomex)
    """
    if trials == 0:
        return {
            'proportion': np.nan,
            'exact_lower_ci': np.nan,
            'exact_upper_ci': np.nan
        }
    
    proportion = successes / trials
    alpha = 1 - confidence_level
    
    # Use beta distribution for exact CI
    if successes == 0:
        lower_ci = 0
    else:
        lower_ci = stats.beta.ppf(alpha/2, successes, trials - successes + 1)
    
    if successes == trials:
        upper_ci = 1
    else:
        upper_ci = stats.beta.ppf(1 - alpha/2, successes + 1, trials - successes)
    
    return {
        'successes': successes,
        'trials': trials,
        'proportion': proportion,
        'exact_lower_ci': lower_ci,
        'exact_upper_ci': upper_ci,
        'confidence_level': confidence_level,
        'method': 'exact'
    }