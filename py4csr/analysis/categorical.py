"""
Categorical Analysis Functions for Clinical Trial Data
Implements RRG categorical analysis equivalents: rrg_chi, rrg_fisher, rrg_cmh
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import chi2_contingency, fisher_exact
from statsmodels.stats.contingency_tables import mcnemar, StratifiedTable
from typing import Dict, List, Optional, Tuple, Union
import warnings

def chi_square_test(data: pd.DataFrame, 
                   row_var: str, 
                   col_var: str,
                   strata: Optional[str] = None,
                   alpha: float = 0.05) -> Dict:
    """
    Perform Chi-square test of independence (equivalent to rrg_chi)
    
    Parameters:
    -----------
    data : pd.DataFrame
        Input dataset
    row_var : str
        Row variable name
    col_var : str
        Column variable name  
    strata : str, optional
        Stratification variable
    alpha : float
        Significance level (default 0.05)
        
    Returns:
    --------
    Dict containing test results
    """
    
    if strata is None:
        # Simple chi-square test
        contingency_table = pd.crosstab(data[row_var], data[col_var])
        chi2_stat, p_value, dof, expected = chi2_contingency(contingency_table)
        
        result = {
            'test_type': 'Chi-square test of independence',
            'chi2_statistic': chi2_stat,
            'p_value': p_value,
            'degrees_of_freedom': dof,
            'contingency_table': contingency_table,
            'expected_frequencies': expected,
            'significant': p_value < alpha
        }
    else:
        # Stratified chi-square test
        strata_results = []
        overall_chi2 = 0
        overall_dof = 0
        
        for stratum in data[strata].unique():
            stratum_data = data[data[strata] == stratum]
            if len(stratum_data) > 0:
                contingency_table = pd.crosstab(stratum_data[row_var], stratum_data[col_var])
                if contingency_table.size > 1:
                    chi2_stat, p_value, dof, expected = chi2_contingency(contingency_table)
                    overall_chi2 += chi2_stat
                    overall_dof += dof
                    
                    strata_results.append({
                        'stratum': stratum,
                        'chi2_statistic': chi2_stat,
                        'p_value': p_value,
                        'degrees_of_freedom': dof,
                        'contingency_table': contingency_table
                    })
        
        overall_p = 1 - stats.chi2.cdf(overall_chi2, overall_dof)
        
        result = {
            'test_type': 'Stratified Chi-square test',
            'overall_chi2_statistic': overall_chi2,
            'overall_p_value': overall_p,
            'overall_degrees_of_freedom': overall_dof,
            'strata_results': strata_results,
            'significant': overall_p < alpha
        }
    
    return result

def fisher_exact_test(data: pd.DataFrame,
                     row_var: str,
                     col_var: str,
                     alternative: str = 'two-sided') -> Dict:
    """
    Perform Fisher's exact test (equivalent to rrg_fisher)
    
    Parameters:
    -----------
    data : pd.DataFrame
        Input dataset
    row_var : str
        Row variable name
    col_var : str
        Column variable name
    alternative : str
        Alternative hypothesis ('two-sided', 'less', 'greater')
        
    Returns:
    --------
    Dict containing test results
    """
    
    contingency_table = pd.crosstab(data[row_var], data[col_var])
    
    if contingency_table.shape != (2, 2):
        raise ValueError("Fisher's exact test requires a 2x2 contingency table")
    
    odds_ratio, p_value = fisher_exact(contingency_table.values, alternative=alternative)
    
    result = {
        'test_type': "Fisher's exact test",
        'odds_ratio': odds_ratio,
        'p_value': p_value,
        'contingency_table': contingency_table,
        'alternative': alternative
    }
    
    return result

def cochran_mantel_haenszel_test(data: pd.DataFrame,
                                row_var: str,
                                col_var: str,
                                strata: str) -> Dict:
    """
    Perform Cochran-Mantel-Haenszel test (equivalent to rrg_cmh)
    
    Parameters:
    -----------
    data : pd.DataFrame
        Input dataset
    row_var : str
        Row variable name
    col_var : str
        Column variable name
    strata : str
        Stratification variable
        
    Returns:
    --------
    Dict containing test results
    """
    
    # Create stratified tables
    tables = []
    for stratum in data[strata].unique():
        stratum_data = data[data[strata] == stratum]
        if len(stratum_data) > 0:
            table = pd.crosstab(stratum_data[row_var], stratum_data[col_var])
            if table.shape == (2, 2) and table.sum().sum() > 0:
                tables.append(table.values)
    
    if len(tables) == 0:
        raise ValueError("No valid 2x2 tables found in strata")
    
    # Calculate CMH statistic
    tables_array = np.array(tables)
    stratified_table = StratifiedTable(tables_array)
    
    cmh_stat = stratified_table.test_null_odds()
    
    result = {
        'test_type': 'Cochran-Mantel-Haenszel test',
        'cmh_statistic': cmh_stat.statistic,
        'p_value': cmh_stat.pvalue,
        'common_odds_ratio': stratified_table.oddsratio_pooled,
        'num_strata': len(tables)
    }
    
    return result

def mcnemar_test(data: pd.DataFrame,
                var1: str,
                var2: str,
                exact: bool = True) -> Dict:
    """
    Perform McNemar's test for paired categorical data
    
    Parameters:
    -----------
    data : pd.DataFrame
        Input dataset
    var1 : str
        First variable name
    var2 : str
        Second variable name
    exact : bool
        Whether to use exact test
        
    Returns:
    --------
    Dict containing test results
    """
    
    contingency_table = pd.crosstab(data[var1], data[var2])
    
    if contingency_table.shape != (2, 2):
        raise ValueError("McNemar's test requires a 2x2 contingency table")
    
    result_stats = mcnemar(contingency_table.values, exact=exact)
    
    result = {
        'test_type': "McNemar's test",
        'statistic': result_stats.statistic,
        'p_value': result_stats.pvalue,
        'contingency_table': contingency_table,
        'exact': exact
    }
    
    return result