"""
Odds Ratio Analysis Functions for Clinical Trial Data
Implements RRG odds ratio equivalent: rrg_oddsev
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import chi2
from typing import Dict, List, Optional, Tuple, Union
import warnings

def odds_ratio_analysis(data: pd.DataFrame,
                       exposure_var: str,
                       outcome_var: str,
                       strata: Optional[str] = None,
                       confidence_level: float = 0.95) -> Dict:
    """
    Calculate odds ratio with confidence intervals (equivalent to rrg_oddsev)
    
    Parameters:
    -----------
    data : pd.DataFrame
        Input dataset
    exposure_var : str
        Exposure variable name (binary)
    outcome_var : str
        Outcome variable name (binary)
    strata : str, optional
        Stratification variable
    confidence_level : float
        Confidence level (default 0.95)
        
    Returns:
    --------
    Dict containing odds ratio analysis results
    """
    
    alpha = 1 - confidence_level
    z_critical = stats.norm.ppf(1 - alpha/2)
    
    if strata is None:
        # Simple odds ratio
        contingency_table = pd.crosstab(data[exposure_var], data[outcome_var])
        
        if contingency_table.shape != (2, 2):
            raise ValueError("Odds ratio requires 2x2 contingency table")
        
        a, b = contingency_table.iloc[0, 0], contingency_table.iloc[0, 1]
        c, d = contingency_table.iloc[1, 0], contingency_table.iloc[1, 1]
        
        # Calculate odds ratio
        if b == 0 or c == 0:
            odds_ratio = np.inf if a*d > 0 else 0
            log_or = np.inf
            se_log_or = np.inf
        else:
            odds_ratio = (a * d) / (b * c)
            log_or = np.log(odds_ratio)
            se_log_or = np.sqrt(1/a + 1/b + 1/c + 1/d)
        
        # Confidence interval
        if se_log_or != np.inf:
            log_or_lower = log_or - z_critical * se_log_or
            log_or_upper = log_or + z_critical * se_log_or
            or_lower = np.exp(log_or_lower)
            or_upper = np.exp(log_or_upper)
        else:
            or_lower = or_upper = np.nan
        
        result = {
            'odds_ratio': odds_ratio,
            'or_lower_ci': or_lower,
            'or_upper_ci': or_upper,
            'log_odds_ratio': log_or,
            'se_log_or': se_log_or,
            'contingency_table': contingency_table,
            'confidence_level': confidence_level
        }
        
    else:
        # Stratified odds ratio (Mantel-Haenszel)
        strata_results = []
        mh_numerator = 0
        mh_denominator = 0
        var_log_or_mh = 0
        
        for stratum in data[strata].unique():
            stratum_data = data[data[strata] == stratum]
            if len(stratum_data) > 0:
                ct = pd.crosstab(stratum_data[exposure_var], stratum_data[outcome_var])
                
                if ct.shape == (2, 2):
                    a, b = ct.iloc[0, 0], ct.iloc[0, 1]
                    c, d = ct.iloc[1, 0], ct.iloc[1, 1]
                    n = a + b + c + d
                    
                    if n > 0 and b > 0 and c > 0:
                        # Stratum-specific OR
                        or_stratum = (a * d) / (b * c)
                        
                        # Mantel-Haenszel components
                        mh_numerator += (a * d) / n
                        mh_denominator += (b * c) / n
                        
                        # Variance components
                        var_log_or_mh += ((a*d*(a+d) + b*c*(b+c)) / (2*n*n)) / ((a*d/n) * (b*c/n))
                        
                        strata_results.append({
                            'stratum': stratum,
                            'odds_ratio': or_stratum,
                            'contingency_table': ct
                        })
        
        # Mantel-Haenszel odds ratio
        if mh_denominator > 0:
            or_mh = mh_numerator / mh_denominator
            log_or_mh = np.log(or_mh)
            se_log_or_mh = np.sqrt(var_log_or_mh)
            
            # Confidence interval
            log_or_lower = log_or_mh - z_critical * se_log_or_mh
            log_or_upper = log_or_mh + z_critical * se_log_or_mh
            or_lower = np.exp(log_or_lower)
            or_upper = np.exp(log_or_upper)
        else:
            or_mh = or_lower = or_upper = np.nan
            log_or_mh = se_log_or_mh = np.nan
        
        result = {
            'mantel_haenszel_or': or_mh,
            'or_lower_ci': or_lower,
            'or_upper_ci': or_upper,
            'log_odds_ratio': log_or_mh,
            'se_log_or': se_log_or_mh,
            'strata_results': strata_results,
            'confidence_level': confidence_level
        }
    
    return result


def conditional_odds_ratio(data: pd.DataFrame,
                          exposure_var: str,
                          outcome_var: str,
                          conditioning_vars: List[str],
                          confidence_level: float = 0.95) -> Dict:
    """
    Calculate conditional odds ratio controlling for specified variables
    
    Parameters:
    -----------
    data : pd.DataFrame
        Input dataset
    exposure_var : str
        Exposure variable name (binary)
    outcome_var : str
        Outcome variable name (binary)
    conditioning_vars : List[str]
        List of variables to condition on
    confidence_level : float
        Confidence level (default 0.95)
        
    Returns:
    --------
    Dict containing conditional odds ratio results
    """
    try:
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import LabelEncoder
        
        # Prepare data for logistic regression
        model_data = data[[exposure_var, outcome_var] + conditioning_vars].dropna()
        
        # Encode categorical variables if needed
        X = model_data[[exposure_var] + conditioning_vars].copy()
        y = model_data[outcome_var]
        
        # Fit logistic regression
        model = LogisticRegression(fit_intercept=True)
        model.fit(X, y)
        
        # Extract coefficient for exposure variable (first column)
        exposure_coef = model.coef_[0][0]
        
        # Calculate odds ratio
        odds_ratio = np.exp(exposure_coef)
        
        # Calculate confidence interval (approximate)
        alpha = 1 - confidence_level
        z_critical = stats.norm.ppf(1 - alpha/2)
        
        # Standard error approximation
        se_coef = np.sqrt(np.diag(np.linalg.inv(X.T @ X)))[0] if X.shape[0] > X.shape[1] else 0.1
        
        log_or_lower = exposure_coef - z_critical * se_coef
        log_or_upper = exposure_coef + z_critical * se_coef
        or_lower = np.exp(log_or_lower)
        or_upper = np.exp(log_or_upper)
        
        return {
            'conditional_odds_ratio': odds_ratio,
            'or_lower_ci': or_lower,
            'or_upper_ci': or_upper,
            'log_odds_ratio': exposure_coef,
            'se_log_or': se_coef,
            'conditioning_variables': conditioning_vars,
            'confidence_level': confidence_level,
            'model_summary': {
                'coefficients': model.coef_[0],
                'intercept': model.intercept_[0],
                'variables': [exposure_var] + conditioning_vars
            }
        }
        
    except ImportError:
        # Fallback without sklearn
        warnings.warn("sklearn not available, using stratified analysis as approximation")
        return stratified_odds_ratio(data, exposure_var, outcome_var, conditioning_vars[0] if conditioning_vars else None, confidence_level)
    except Exception as e:
        return {
            'error': str(e),
            'method': 'Conditional Odds Ratio'
        }


def stratified_odds_ratio(data: pd.DataFrame,
                         exposure_var: str,
                         outcome_var: str,
                         strata_var: Optional[str] = None,
                         confidence_level: float = 0.95) -> Dict:
    """
    Calculate stratified odds ratio using Mantel-Haenszel method
    
    Parameters:
    -----------
    data : pd.DataFrame
        Input dataset
    exposure_var : str
        Exposure variable name (binary)
    outcome_var : str
        Outcome variable name (binary)
    strata_var : str, optional
        Stratification variable
    confidence_level : float
        Confidence level (default 0.95)
        
    Returns:
    --------
    Dict containing stratified odds ratio results
    """
    if strata_var is None:
        # If no strata specified, return simple odds ratio
        return odds_ratio_analysis(data, exposure_var, outcome_var, None, confidence_level)
    
    # Use the existing stratified logic from odds_ratio_analysis
    return odds_ratio_analysis(data, exposure_var, outcome_var, strata_var, confidence_level)