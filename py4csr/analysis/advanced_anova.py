"""
Advanced ANOVA Functions for Clinical Trial Data
Extends existing ANOVA capabilities with RRG equivalents
"""

import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from typing import Dict, List, Optional, Tuple, Union

def advanced_anova_analysis(data: pd.DataFrame,
                           dependent_var: str,
                           treatment_var: str,
                           covariates: Optional[List[str]] = None,
                           strata: Optional[List[str]] = None,
                           contrasts: Optional[Dict] = None) -> Dict:
    """
    Perform advanced ANOVA/ANCOVA analysis (enhanced rrg_anova equivalent)
    
    Parameters:
    -----------
    data : pd.DataFrame
        Input dataset
    dependent_var : str
        Dependent variable name
    treatment_var : str
        Treatment variable name
    covariates : List[str], optional
        List of covariate names
    strata : List[str], optional
        List of stratification variables
    contrasts : Dict, optional
        Custom contrasts to test
        
    Returns:
    --------
    Dict containing comprehensive ANOVA results
    """
    
    # Build formula
    formula_parts = [dependent_var, '~', treatment_var]
    
    if covariates:
        formula_parts.extend(['+'] + ['+'.join(covariates)])
    
    if strata:
        formula_parts.extend(['+'] + ['+'.join(strata)])
    
    formula = ' '.join(formula_parts)
    
    # Fit model
    model = ols(formula, data=data).fit()
    anova_table = anova_lm(model, typ=2)
    
    # Calculate effect sizes
    ss_total = anova_table['sum_sq'].sum()
    eta_squared = {}
    for factor in anova_table.index[:-1]:  # Exclude residual
        eta_squared[factor] = anova_table.loc[factor, 'sum_sq'] / ss_total
    
    # Pairwise comparisons if treatment has multiple levels
    pairwise_results = None
    if len(data[treatment_var].unique()) > 2:
        try:
            tukey_result = pairwise_tukeyhsd(data[dependent_var], data[treatment_var])
            pairwise_results = {
                'method': 'Tukey HSD',
                'summary': str(tukey_result),
                'pvalues': tukey_result.pvalues,
                'reject': tukey_result.reject
            }
        except Exception as e:
            pairwise_results = {'error': str(e)}
    
    # Model diagnostics
    residuals = model.resid
    fitted_values = model.fittedvalues
    
    diagnostics = {
        'normality_test': stats.shapiro(residuals),
        'homoscedasticity_test': stats.levene(*[data[data[treatment_var] == group][dependent_var] 
                                               for group in data[treatment_var].unique()]),
        'r_squared': model.rsquared,
        'adj_r_squared': model.rsquared_adj
    }
    
    result = {
        'model_summary': model.summary(),
        'anova_table': anova_table,
        'eta_squared': eta_squared,
        'pairwise_comparisons': pairwise_results,
        'diagnostics': diagnostics,
        'residuals': residuals,
        'fitted_values': fitted_values,
        'formula': formula
    }
    
    return result


def repeated_measures_anova(data: pd.DataFrame,
                           dependent_var: str,
                           subject_var: str,
                           within_factor: str,
                           between_factor: Optional[str] = None) -> Dict:
    """
    Perform repeated measures ANOVA analysis
    
    Parameters:
    -----------
    data : pd.DataFrame
        Input dataset
    dependent_var : str
        Dependent variable name
    subject_var : str
        Subject identifier variable
    within_factor : str
        Within-subjects factor
    between_factor : str, optional
        Between-subjects factor
        
    Returns:
    --------
    Dict containing repeated measures ANOVA results
    """
    try:
        from statsmodels.stats.anova import AnovaRM
        
        # Prepare data for repeated measures ANOVA
        if between_factor:
            formula = f'{dependent_var} ~ C({within_factor}) + C({between_factor}) + C({within_factor}):C({between_factor})'
        else:
            formula = f'{dependent_var} ~ C({within_factor})'
        
        # Perform repeated measures ANOVA
        rm_anova = AnovaRM(data, dependent_var, subject_var, within=[within_factor])
        if between_factor:
            rm_anova = AnovaRM(data, dependent_var, subject_var, 
                              within=[within_factor], between=[between_factor])
        
        results = rm_anova.fit()
        
        return {
            'anova_table': results.anova_table,
            'summary': str(results.summary()),
            'formula': formula,
            'method': 'Repeated Measures ANOVA'
        }
        
    except ImportError:
        # Fallback to basic repeated measures analysis
        return {
            'error': 'statsmodels.stats.anova.AnovaRM not available',
            'method': 'Basic Repeated Measures Analysis',
            'note': 'Install statsmodels>=0.12 for full repeated measures ANOVA'
        }
    except Exception as e:
        return {
            'error': str(e),
            'method': 'Repeated Measures ANOVA'
        }


def mixed_effects_anova(data: pd.DataFrame,
                       dependent_var: str,
                       fixed_effects: List[str],
                       random_effects: List[str],
                       group_var: Optional[str] = None) -> Dict:
    """
    Perform mixed effects ANOVA analysis
    
    Parameters:
    -----------
    data : pd.DataFrame
        Input dataset
    dependent_var : str
        Dependent variable name
    fixed_effects : List[str]
        List of fixed effect variables
    random_effects : List[str]
        List of random effect variables
    group_var : str, optional
        Grouping variable for random effects
        
    Returns:
    --------
    Dict containing mixed effects ANOVA results
    """
    try:
        from statsmodels.formula.api import mixedlm
        
        # Build formula for mixed effects model
        fixed_formula = ' + '.join(fixed_effects)
        formula = f'{dependent_var} ~ {fixed_formula}'
        
        # Fit mixed effects model
        if group_var and random_effects:
            re_formula = ' + '.join(random_effects)
            model = mixedlm(formula, data, groups=data[group_var], re_formula=re_formula)
        else:
            model = mixedlm(formula, data, groups=data[group_var] if group_var else None)
        
        results = model.fit()
        
        return {
            'summary': str(results.summary()),
            'fixed_effects': results.fe_params,
            'random_effects': results.cov_re if hasattr(results, 'cov_re') else None,
            'formula': formula,
            'method': 'Mixed Effects ANOVA',
            'aic': results.aic,
            'bic': results.bic
        }
        
    except ImportError:
        return {
            'error': 'statsmodels.formula.api.mixedlm not available',
            'method': 'Mixed Effects ANOVA',
            'note': 'Install statsmodels for mixed effects modeling'
        }
    except Exception as e:
        return {
            'error': str(e),
            'method': 'Mixed Effects ANOVA'
        }