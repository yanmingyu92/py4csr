"""
Statistical Templates for Functional Clinical Reporting

This module provides reusable statistical calculation templates that mirror
the SAS RRG system's approach to standardized clinical trial statistics.
"""

from typing import Dict, List, Optional, Any, Callable
import pandas as pd
import numpy as np
from scipy import stats
import warnings

from .config import FunctionalConfig, StatisticDefinition


class StatisticalTemplates:
    """
    Statistical calculation templates (equivalent to SAS RRG statistical macros).
    
    This class provides standardized statistical calculations for clinical trials,
    similar to how SAS RRG provides reusable statistical templates through macros.
    """
    
    def __init__(self, config: FunctionalConfig):
        """
        Initialize statistical templates.
        
        Parameters
        ----------
        config : FunctionalConfig
            Configuration containing statistical definitions
        """
        self.config = config
        self._format_functions = self._register_format_functions()
        
    def calculate_continuous_statistics(self, data: pd.DataFrame, variable: str, 
                                      treatment_var: str, statistics: List[str] = None) -> pd.DataFrame:
        """
        Calculate continuous variable statistics (equivalent to SAS RRG %__cont macro).
        
        Parameters
        ----------
        data : pd.DataFrame
            Input dataset
        variable : str
            Variable to analyze
        treatment_var : str
            Treatment grouping variable
        statistics : list, optional
            List of statistics to calculate
            
        Returns
        -------
        pd.DataFrame
            Statistics results
        """
        if variable not in data.columns:
            raise ValueError(f"Variable '{variable}' not found in data")
            
        if treatment_var not in data.columns:
            raise ValueError(f"Treatment variable '{treatment_var}' not found in data")
        
        # Default statistics for continuous variables
        if statistics is None:
            statistics = self.config.get_applicable_statistics('continuous')
        
        # Clean data - remove missing values
        clean_data = data[[variable, treatment_var]].dropna()
        
        results = []
        
        # Calculate statistics by treatment group
        for treatment in sorted(clean_data[treatment_var].unique()):
            trt_data = clean_data[clean_data[treatment_var] == treatment][variable]
            
            if len(trt_data) == 0:
                continue
                
            row = {
                'TREATMENT': treatment,
                'VARIABLE': variable,
                'STATISTIC': '',
                'VALUE': '',
                'FORMATTED_VALUE': ''
            }
            
            for stat_name in statistics:
                stat_def = self.config.get_statistic(stat_name)
                if not stat_def or 'continuous' not in stat_def.applicable_types:
                    continue
                    
                stat_row = row.copy()
                stat_row['STATISTIC'] = stat_def.display_name
                
                # Calculate statistic
                if stat_name == 'n':
                    value = len(trt_data)
                elif stat_name == 'mean':
                    value = trt_data.mean()
                elif stat_name == 'std':
                    value = trt_data.std()
                elif stat_name == 'median':
                    value = trt_data.median()
                elif stat_name == 'min':
                    value = trt_data.min()
                elif stat_name == 'max':
                    value = trt_data.max()
                elif stat_name == 'q1':
                    value = trt_data.quantile(0.25)
                elif stat_name == 'q3':
                    value = trt_data.quantile(0.75)
                elif stat_name == 'mean_sd':
                    # Combined statistic
                    mean_val = trt_data.mean()
                    std_val = trt_data.std()
                    value = (mean_val, std_val)
                elif stat_name == 'min_max':
                    # Combined statistic
                    min_val = trt_data.min()
                    max_val = trt_data.max()
                    value = (min_val, max_val)
                elif stat_name == 'q1_q3':
                    # Combined statistic
                    q1_val = trt_data.quantile(0.25)
                    q3_val = trt_data.quantile(0.75)
                    value = (q1_val, q3_val)
                else:
                    continue
                
                stat_row['VALUE'] = value
                stat_row['FORMATTED_VALUE'] = self._format_statistic(value, stat_def)
                results.append(stat_row)
        
        # Add overall statistics (Total column)
        if len(clean_data) > 0:
            overall_data = clean_data[variable]
            
            for stat_name in statistics:
                stat_def = self.config.get_statistic(stat_name)
                if not stat_def or 'continuous' not in stat_def.applicable_types:
                    continue
                    
                stat_row = {
                    'TREATMENT': 'Total',
                    'VARIABLE': variable,
                    'STATISTIC': stat_def.display_name,
                    'VALUE': '',
                    'FORMATTED_VALUE': ''
                }
                
                # Calculate overall statistic
                if stat_name == 'n':
                    value = len(overall_data)
                elif stat_name == 'mean':
                    value = overall_data.mean()
                elif stat_name == 'std':
                    value = overall_data.std()
                elif stat_name == 'median':
                    value = overall_data.median()
                elif stat_name == 'min':
                    value = overall_data.min()
                elif stat_name == 'max':
                    value = overall_data.max()
                elif stat_name == 'q1':
                    value = overall_data.quantile(0.25)
                elif stat_name == 'q3':
                    value = overall_data.quantile(0.75)
                elif stat_name == 'mean_sd':
                    mean_val = overall_data.mean()
                    std_val = overall_data.std()
                    value = (mean_val, std_val)
                elif stat_name == 'min_max':
                    min_val = overall_data.min()
                    max_val = overall_data.max()
                    value = (min_val, max_val)
                elif stat_name == 'q1_q3':
                    q1_val = overall_data.quantile(0.25)
                    q3_val = overall_data.quantile(0.75)
                    value = (q1_val, q3_val)
                else:
                    continue
                
                stat_row['VALUE'] = value
                stat_row['FORMATTED_VALUE'] = self._format_statistic(value, stat_def)
                results.append(stat_row)
        
        return pd.DataFrame(results)
    
    def calculate_categorical_statistics(self, data: pd.DataFrame, variable: str,
                                       treatment_var: str, statistics: List[str] = None) -> pd.DataFrame:
        """
        Calculate categorical variable statistics (equivalent to SAS RRG %__cnts macro).
        
        Parameters
        ----------
        data : pd.DataFrame
            Input dataset
        variable : str
            Variable to analyze
        treatment_var : str
            Treatment grouping variable
        statistics : list, optional
            List of statistics to calculate
            
        Returns
        -------
        pd.DataFrame
            Statistics results
        """
        if variable not in data.columns:
            raise ValueError(f"Variable '{variable}' not found in data")
            
        if treatment_var not in data.columns:
            raise ValueError(f"Treatment variable '{treatment_var}' not found in data")
        
        # Default statistics for categorical variables
        if statistics is None:
            statistics = self.config.get_applicable_statistics('categorical')
        
        # Clean data - remove missing values
        clean_data = data[[variable, treatment_var]].dropna()
        
        results = []
        
        # Get all unique categories
        all_categories = sorted(clean_data[variable].unique())
        
        # Calculate statistics by treatment group
        for treatment in sorted(clean_data[treatment_var].unique()):
            trt_data = clean_data[clean_data[treatment_var] == treatment]
            trt_total = len(trt_data)
            
            for category in all_categories:
                cat_count = len(trt_data[trt_data[variable] == category])
                
                for stat_name in statistics:
                    stat_def = self.config.get_statistic(stat_name)
                    if not stat_def or 'categorical' not in stat_def.applicable_types:
                        continue
                    
                    stat_row = {
                        'TREATMENT': treatment,
                        'VARIABLE': variable,
                        'CATEGORY': category,
                        'STATISTIC': stat_def.display_name,
                        'VALUE': '',
                        'FORMATTED_VALUE': ''
                    }
                    
                    if stat_name == 'n':
                        value = cat_count
                    elif stat_name == 'percent':
                        value = (cat_count / trt_total * 100) if trt_total > 0 else 0
                    elif stat_name == 'n_percent':
                        percent = (cat_count / trt_total * 100) if trt_total > 0 else 0
                        value = (cat_count, percent)
                    else:
                        continue
                    
                    stat_row['VALUE'] = value
                    stat_row['FORMATTED_VALUE'] = self._format_statistic(value, stat_def)
                    results.append(stat_row)
        
        # Add overall statistics (Total column)
        overall_total = len(clean_data)
        
        for category in all_categories:
            cat_count = len(clean_data[clean_data[variable] == category])
            
            for stat_name in statistics:
                stat_def = self.config.get_statistic(stat_name)
                if not stat_def or 'categorical' not in stat_def.applicable_types:
                    continue
                
                stat_row = {
                    'TREATMENT': 'Total',
                    'VARIABLE': variable,
                    'CATEGORY': category,
                    'STATISTIC': stat_def.display_name,
                    'VALUE': '',
                    'FORMATTED_VALUE': ''
                }
                
                if stat_name == 'n':
                    value = cat_count
                elif stat_name == 'percent':
                    value = (cat_count / overall_total * 100) if overall_total > 0 else 0
                elif stat_name == 'n_percent':
                    percent = (cat_count / overall_total * 100) if overall_total > 0 else 0
                    value = (cat_count, percent)
                else:
                    continue
                
                stat_row['VALUE'] = value
                stat_row['FORMATTED_VALUE'] = self._format_statistic(value, stat_def)
                results.append(stat_row)
        
        return pd.DataFrame(results)
    
    def calculate_ae_statistics(self, data: pd.DataFrame, treatment_var: str,
                               soc_var: str = 'AEBODSYS', pt_var: str = 'AEDECOD') -> pd.DataFrame:
        """
        Calculate adverse event statistics (equivalent to SAS RRG AE templates).
        
        Parameters
        ----------
        data : pd.DataFrame
            Adverse events dataset
        treatment_var : str
            Treatment variable
        soc_var : str
            System organ class variable
        pt_var : str
            Preferred term variable
            
        Returns
        -------
        pd.DataFrame
            AE statistics results
        """
        results = []
        
        # Calculate subject-level AE counts (subjects counted once per SOC/PT)
        subject_var = 'USUBJID' if 'USUBJID' in data.columns else 'SUBJID'
        
        if subject_var not in data.columns:
            raise ValueError("Subject ID variable not found in data")
        
        # Get unique subjects per treatment
        treatment_counts = data.groupby(treatment_var)[subject_var].nunique().to_dict()
        
        # Calculate SOC-level statistics
        soc_stats = self._calculate_ae_level_stats(
            data, treatment_var, subject_var, soc_var, treatment_counts, 'SOC'
        )
        results.extend(soc_stats)
        
        # Calculate PT-level statistics within each SOC
        for soc in data[soc_var].unique():
            soc_data = data[data[soc_var] == soc]
            pt_stats = self._calculate_ae_level_stats(
                soc_data, treatment_var, subject_var, pt_var, treatment_counts, 'PT', parent_term=soc
            )
            results.extend(pt_stats)
        
        return pd.DataFrame(results)
    
    def _calculate_ae_level_stats(self, data: pd.DataFrame, treatment_var: str, 
                                 subject_var: str, term_var: str, treatment_counts: Dict,
                                 level: str, parent_term: str = None) -> List[Dict]:
        """Calculate AE statistics at SOC or PT level."""
        results = []
        
        for treatment in sorted(data[treatment_var].unique()):
            trt_data = data[data[treatment_var] == treatment]
            trt_total = treatment_counts.get(treatment, 0)
            
            for term in sorted(trt_data[term_var].unique()):
                term_data = trt_data[trt_data[term_var] == term]
                subject_count = term_data[subject_var].nunique()
                event_count = len(term_data)
                
                # Subject count and percentage
                percent = (subject_count / trt_total * 100) if trt_total > 0 else 0
                
                result_row = {
                    'TREATMENT': treatment,
                    'LEVEL': level,
                    'TERM': term,
                    'PARENT_TERM': parent_term,
                    'SUBJECT_COUNT': subject_count,
                    'EVENT_COUNT': event_count,
                    'PERCENTAGE': percent,
                    'FORMATTED_VALUE': f"{subject_count} ({percent:.1f}%)"
                }
                
                results.append(result_row)
        
        return results
    
    def _format_statistic(self, value: Any, stat_def: StatisticDefinition) -> str:
        """Format a statistic value according to its definition."""
        if pd.isna(value) or value is None:
            return ""
        
        # Handle combined statistics
        if isinstance(value, tuple):
            if stat_def.format_function:
                format_func = self._format_functions.get(stat_def.format_function)
                if format_func:
                    return format_func(value, stat_def.precision)
            
            # Default formatting for tuples
            if len(value) == 2:
                if stat_def.name == 'mean_sd':
                    return f"{value[0]:.{stat_def.precision}f} ({value[1]:.{stat_def.precision}f})"
                elif stat_def.name in ['min_max', 'q1_q3']:
                    return f"{value[0]:.{stat_def.precision}f}, {value[1]:.{stat_def.precision}f}"
            
            return str(value)
        
        # Handle single values
        if isinstance(value, (int, float)):
            if stat_def.precision == 0:
                return f"{value:.0f}"
            else:
                return f"{value:.{stat_def.precision}f}"
        
        return str(value)
    
    def _register_format_functions(self) -> Dict[str, Callable]:
        """Register format functions for combined statistics."""
        return {
            'format_mean_sd': self._format_mean_sd,
            'format_min_max': self._format_min_max,
            'format_quartiles': self._format_quartiles,
            'format_n_percent': self._format_n_percent
        }
    
    def _format_mean_sd(self, value: tuple, precision: int) -> str:
        """Format mean (SD) statistic."""
        if len(value) != 2:
            return str(value)
        mean_val, sd_val = value
        return f"{mean_val:.{precision}f} ({sd_val:.{precision}f})"
    
    def _format_min_max(self, value: tuple, precision: int) -> str:
        """Format min, max statistic."""
        if len(value) != 2:
            return str(value)
        min_val, max_val = value
        return f"{min_val:.{precision}f}, {max_val:.{precision}f}"
    
    def _format_quartiles(self, value: tuple, precision: int) -> str:
        """Format Q1, Q3 statistic."""
        if len(value) != 2:
            return str(value)
        q1_val, q3_val = value
        return f"{q1_val:.{precision}f}, {q3_val:.{precision}f}"
    
    def _format_n_percent(self, value: tuple, precision: int) -> str:
        """Format n (%) statistic."""
        if len(value) != 2:
            return str(value)
        n_val, pct_val = value
        return f"{n_val:.0f} ({pct_val:.{precision}f}%)" 