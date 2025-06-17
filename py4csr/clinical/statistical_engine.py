"""
Statistical calculation engine for py4csr clinical reporting.

This module implements the core statistical calculations for continuous and 
categorical variables, equivalent to the SAS statistical processing engines.
"""

from typing import Dict, List, Optional, Any, Union
import pandas as pd
import numpy as np
from scipy import stats
import warnings


class ClinicalStatisticalEngine:
    """
    Statistical calculation engine for clinical reporting.
    
    This class implements the core statistical calculations for both continuous
    and categorical variables, providing formatted results suitable for 
    clinical table generation.
    """
    
    def __init__(self):
        """Initialize the statistical engine."""
        self.decimal_places = {
            'age': 1,
            'weight': 1, 'wgt': 1, 'wgtbl': 1,
            'height': 1, 'hgt': 1, 'hgtbl': 1,
            'bmi': 1, 'bmibl': 1,
            'default': 1
        }
    
    def calculate_continuous_stats(self,
                                 data: pd.DataFrame,
                                 variable: str,
                                 treatment_var: str,
                                 stats_spec: str,
                                 where_clause: str = "",
                                 base_decimals: int = 1) -> pd.DataFrame:
        """
        Calculate statistics for continuous variables.
        
        Parameters
        ----------
        data : pd.DataFrame
            Input dataset
        variable : str
            Variable name to analyze
        treatment_var : str
            Treatment variable name
        stats_spec : str
            Statistics specification (e.g., "n mean+sd median q1q3 min+max")
        where_clause : str
            Additional filter condition
        base_decimals : int
            Base number of decimal places
            
        Returns
        -------
        pd.DataFrame
            Statistical results with formatted values
        """
        # Apply additional filter if specified
        filtered_data = data.copy()
        if where_clause and where_clause.strip():
            try:
                filtered_data = filtered_data.query(where_clause)
            except Exception as e:
                warnings.warn(f"Where clause failed for {variable}: {e}")
        
        # Ensure variable exists and is numeric
        if variable not in filtered_data.columns:
            raise ValueError(f"Variable '{variable}' not found in dataset")
        
        # Convert to numeric, coercing errors to NaN
        filtered_data[variable] = pd.to_numeric(filtered_data[variable], errors='coerce')
        
        # Parse statistics specification
        requested_stats = self._parse_stats_spec(stats_spec)
        
        # Get decimal places for this variable
        decimals = self.decimal_places.get(variable.lower(), base_decimals)
        
        results = []
        
        # Calculate for each treatment group
        treatment_groups = sorted(filtered_data[treatment_var].unique())
        
        for treatment in treatment_groups:
            trt_data = filtered_data[filtered_data[treatment_var] == treatment]
            var_data = trt_data[variable].dropna()
            
            # Calculate each requested statistic
            for stat_name in requested_stats:
                stat_result = self._calculate_single_continuous_stat(
                    var_data, stat_name, decimals
                )
                
                results.append({
                    'treatment': treatment,
                    'variable': variable,
                    'statistic': stat_result['name'],
                    'value': stat_result['value'],
                    'formatted_value': stat_result['formatted']
                })
        
        # Add Total column - statistics across all treatment groups
        all_var_data = filtered_data[variable].dropna()
        
        for stat_name in requested_stats:
            stat_result = self._calculate_single_continuous_stat(
                all_var_data, stat_name, decimals
            )
            
            results.append({
                'treatment': 'Total',
                'variable': variable,
                'statistic': stat_result['name'],
                'value': stat_result['value'],
                'formatted_value': stat_result['formatted']
            })
        
        return pd.DataFrame(results)
    
    def calculate_categorical_stats(self,
                                  data: pd.DataFrame,
                                  variable: str,
                                  treatment_var: str,
                                  stats_spec: str,
                                  where_clause: str = "",
                                  decode_var: str = "",
                                  show_missing: str = "Y") -> pd.DataFrame:
        """
        Calculate statistics for categorical variables.
        
        Parameters
        ----------
        data : pd.DataFrame
            Input dataset
        variable : str
            Variable name to analyze
        treatment_var : str
            Treatment variable name
        stats_spec : str
            Statistics specification (e.g., "npct")
        where_clause : str
            Additional filter condition
        decode_var : str
            Decode variable name for category labels
        show_missing : str
            Whether to show missing values
            
        Returns
        -------
        pd.DataFrame
            Statistical results with formatted values
        """
        # Apply additional filter if specified
        filtered_data = data.copy()
        if where_clause and where_clause.strip():
            try:
                filtered_data = filtered_data.query(where_clause)
            except Exception as e:
                warnings.warn(f"Where clause failed for {variable}: {e}")
        
        # Ensure variable exists
        if variable not in filtered_data.columns:
            raise ValueError(f"Variable '{variable}' not found in dataset")
        
        # Use decode variable if specified and exists
        if decode_var and decode_var in filtered_data.columns:
            category_var = decode_var
        else:
            category_var = variable
        
        # Parse statistics specification
        requested_stats = self._parse_categorical_stats_spec(stats_spec)
        
        results = []
        
        # Get treatment groups and categories
        treatment_groups = sorted(filtered_data[treatment_var].unique())
        
        # Get all categories (including missing if requested)
        if show_missing.upper() == 'Y':
            categories = filtered_data[category_var].fillna('Missing').unique()
        else:
            categories = filtered_data[category_var].dropna().unique()
        
        categories = sorted([str(cat) for cat in categories])
        
        # Apply proper case formatting to categories
        categories = [self._format_category_name(cat) for cat in categories]
        
        # Calculate for each treatment and category combination
        for treatment in treatment_groups:
            trt_data = filtered_data[filtered_data[treatment_var] == treatment]
            
            # Calculate denominator (total subjects in treatment group)
            total_n = len(trt_data)
            
            for category in categories:
                # Count subjects in this category
                if category == 'Missing':
                    cat_data = trt_data[trt_data[category_var].isna()]
                else:
                    # Match against original category (before formatting)
                    original_cat = self._get_original_category(category, filtered_data[category_var])
                    cat_data = trt_data[trt_data[category_var] == original_cat]
                
                category_n = len(cat_data)
                
                # Calculate percentage
                if total_n > 0:
                    percentage = (category_n / total_n) * 100
                else:
                    percentage = 0.0
                
                # Format according to requested statistics
                for stat_name in requested_stats:
                    formatted_value = self._format_categorical_stat(
                        category_n, percentage, total_n, stat_name
                    )
                    
                    results.append({
                        'treatment': treatment,
                        'variable': variable,
                        'category': category,
                        'statistic': stat_name,
                        'n': category_n,
                        'percentage': percentage,
                        'total_n': total_n,
                        'formatted_value': formatted_value
                    })
        
        # Add Total column - statistics across all treatment groups
        all_total_n = len(filtered_data)
        
        for category in categories:
            # Count subjects in this category across all treatments
            if category == 'Missing':
                cat_data = filtered_data[filtered_data[category_var].isna()]
            else:
                # Match against original category (before formatting)
                original_cat = self._get_original_category(category, filtered_data[category_var])
                cat_data = filtered_data[filtered_data[category_var] == original_cat]
            
            category_n = len(cat_data)
            
            # Calculate percentage
            if all_total_n > 0:
                percentage = (category_n / all_total_n) * 100
            else:
                percentage = 0.0
            
            # Format according to requested statistics
            for stat_name in requested_stats:
                formatted_value = self._format_categorical_stat(
                    category_n, percentage, all_total_n, stat_name
                )
                
                results.append({
                    'treatment': 'Total',
                    'variable': variable,
                    'category': category,
                    'statistic': stat_name,
                    'n': category_n,
                    'percentage': percentage,
                    'total_n': all_total_n,
                    'formatted_value': formatted_value
                })
        
        return pd.DataFrame(results)
    
    def _parse_stats_spec(self, stats_spec: str) -> List[str]:
        """Parse continuous statistics specification."""
        # Common statistics mappings
        stat_map = {
            'n': 'N',
            'mean': 'Mean',
            'sd': 'SD', 
            'mean+sd': 'Mean (SD)',
            'median': 'Median',
            'q1': 'Q1',
            'q3': 'Q3',
            'q1q3': 'Q1, Q3',
            'q1q3.q1q3': 'Q1, Q3',
            'min': 'Min',
            'max': 'Max',
            'min+max': 'Min, Max',
            'std': 'SD',
            'var': 'Variance'
        }
        
        # Parse the specification
        parts = stats_spec.lower().replace(',', ' ').split()
        parsed_stats = []
        
        for part in parts:
            part = part.strip()
            if part in stat_map:
                parsed_stats.append(stat_map[part])
            elif '+' in part:
                # Handle combined statistics like mean+sd
                if part in stat_map:
                    parsed_stats.append(stat_map[part])
                else:
                    # Split and add individually
                    sub_parts = part.split('+')
                    for sub_part in sub_parts:
                        if sub_part in stat_map:
                            parsed_stats.append(stat_map[sub_part])
            else:
                # Add as-is if not found in mapping
                parsed_stats.append(part.title())
        
        # Default statistics if none specified
        if not parsed_stats:
            parsed_stats = ['N', 'Mean (SD)', 'Median', 'Min, Max']
        
        return parsed_stats
    
    def _parse_categorical_stats_spec(self, stats_spec: str) -> List[str]:
        """Parse categorical statistics specification."""
        stat_map = {
            'n': 'n',
            'pct': 'pct',
            'npct': 'n_pct',
            'nnpct': 'nn_pct',
            'n+pct': 'n_pct'
        }
        
        parts = stats_spec.lower().replace(',', ' ').split()
        parsed_stats = []
        
        for part in parts:
            part = part.strip()
            if part in stat_map:
                parsed_stats.append(stat_map[part])
            else:
                parsed_stats.append('n_pct')  # Default
        
        if not parsed_stats:
            parsed_stats = ['n_pct']
        
        return parsed_stats
    
    def _calculate_single_continuous_stat(self, 
                                        data: pd.Series, 
                                        stat_name: str, 
                                        decimals: int) -> Dict[str, Any]:
        """Calculate a single continuous statistic."""
        if len(data) == 0:
            return {
                'name': stat_name,
                'value': None,
                'formatted': ''
            }
        
        if stat_name == 'N':
            value = len(data)
            formatted = str(value)
            
        elif stat_name == 'Mean':
            value = data.mean()
            formatted = f"{value:.{decimals}f}"
            
        elif stat_name == 'SD':
            value = data.std()
            formatted = f"{value:.{decimals}f}"
            
        elif stat_name == 'Mean (SD)':
            mean_val = data.mean()
            sd_val = data.std()
            value = (mean_val, sd_val)
            formatted = f"{mean_val:.{decimals}f} ({sd_val:.{decimals}f})"
            
        elif stat_name == 'Median':
            value = data.median()
            formatted = f"{value:.{decimals}f}"
            
        elif stat_name == 'Q1':
            value = data.quantile(0.25)
            formatted = f"{value:.{decimals}f}"
            
        elif stat_name == 'Q3':
            value = data.quantile(0.75)
            formatted = f"{value:.{decimals}f}"
            
        elif stat_name in ['Q1, Q3', 'Q1Q3']:
            q1 = data.quantile(0.25)
            q3 = data.quantile(0.75)
            value = (q1, q3)
            formatted = f"{q1:.{decimals}f}, {q3:.{decimals}f}"
            
        elif stat_name == 'Min':
            value = data.min()
            formatted = f"{value:.{decimals}f}"
            
        elif stat_name == 'Max':
            value = data.max()
            formatted = f"{value:.{decimals}f}"
            
        elif stat_name in ['Min, Max', 'Min+Max']:
            min_val = data.min()
            max_val = data.max()
            value = (min_val, max_val)
            formatted = f"{min_val:.{decimals}f}, {max_val:.{decimals}f}"
            
        elif stat_name == 'Variance':
            value = data.var()
            formatted = f"{value:.{decimals}f}"
            
        else:
            # Unknown statistic
            value = None
            formatted = 'N/A'
        
        return {
            'name': stat_name,
            'value': value,
            'formatted': formatted
        }
    
    def _format_categorical_stat(self, 
                               n: int, 
                               percentage: float, 
                               total_n: int, 
                               stat_name: str) -> str:
        """Format categorical statistic."""
        if stat_name == 'n':
            return str(n)
        elif stat_name == 'pct':
            return f"{percentage:.1f}%"
        elif stat_name == 'n_pct':
            return f"{n} ({percentage:.1f}%)"
        elif stat_name == 'nn_pct':
            return f"{n}/{total_n} ({percentage:.1f}%)"
        else:
            return f"{n} ({percentage:.1f}%)"  # Default
    
    def _format_category_name(self, category: str) -> str:
        """Format category names to proper case."""
        if category == 'Missing':
            return category
        
        # Convert to proper case for common categories
        category_str = str(category).strip()
        
        # Handle race categories specifically
        race_mappings = {
            'AMERICAN INDIAN OR ALASKA NATIVE': 'American Indian or Alaska Native',
            'BLACK OR AFRICAN AMERICAN': 'Black or African American',
            'WHITE': 'White',
            'ASIAN': 'Asian',
            'NATIVE HAWAIIAN OR OTHER PACIFIC ISLANDER': 'Native Hawaiian or Other Pacific Islander',
            'MULTIPLE': 'Multiple',
            'OTHER': 'Other',
            'UNKNOWN': 'Unknown'
        }
        
        # Check if it's a known race category
        if category_str.upper() in race_mappings:
            return race_mappings[category_str.upper()]
        
        # For other categories, use title case with some adjustments
        formatted = category_str.title()
        
        # Keep some words lowercase (articles, conjunctions, prepositions)
        lowercase_words = ['of', 'or', 'and', 'the', 'in', 'on', 'at', 'to', 'for', 'with']
        words = formatted.split()
        
        for i, word in enumerate(words):
            if i > 0 and word.lower() in lowercase_words:
                words[i] = word.lower()
        
        return ' '.join(words)
    
    def _get_original_category(self, formatted_category: str, original_data: pd.Series) -> str:
        """Get the original category value that matches the formatted category."""
        # Create a mapping of formatted categories back to original values
        unique_values = original_data.dropna().unique()
        
        for original_val in unique_values:
            if self._format_category_name(str(original_val)) == formatted_category:
                return original_val
        
        # If no match found, return the formatted category (fallback)
        return formatted_category
    
    def perform_anova(self, 
                     data: pd.DataFrame,
                     variable: str,
                     treatment_var: str) -> Dict[str, Any]:
        """
        Perform ANOVA test for continuous variable by treatment.
        
        Parameters
        ----------
        data : pd.DataFrame
            Input dataset
        variable : str
            Continuous variable to test
        treatment_var : str
            Treatment grouping variable
            
        Returns
        -------
        dict
            ANOVA results including F-statistic and p-value
        """
        # Prepare data
        clean_data = data[[variable, treatment_var]].dropna()
        
        if len(clean_data) == 0:
            return {'f_stat': None, 'p_value': None, 'error': 'No valid data'}
        
        # Get treatment groups
        groups = [group[variable].values for name, group in clean_data.groupby(treatment_var)]
        
        if len(groups) < 2:
            return {'f_stat': None, 'p_value': None, 'error': 'Less than 2 groups'}
        
        try:
            # Perform one-way ANOVA
            f_stat, p_value = stats.f_oneway(*groups)
            
            return {
                'f_stat': f_stat,
                'p_value': p_value,
                'error': None,
                'formatted_p': f"{p_value:.4f}" if p_value >= 0.0001 else "<0.0001"
            }
        except Exception as e:
            return {'f_stat': None, 'p_value': None, 'error': str(e)}
    
    def perform_chi_square(self,
                          data: pd.DataFrame,
                          variable: str,
                          treatment_var: str) -> Dict[str, Any]:
        """
        Perform Chi-square test for categorical variable by treatment.
        
        Parameters
        ----------
        data : pd.DataFrame
            Input dataset
        variable : str
            Categorical variable to test
        treatment_var : str
            Treatment grouping variable
            
        Returns
        -------
        dict
            Chi-square test results
        """
        # Create contingency table
        try:
            contingency_table = pd.crosstab(data[variable], data[treatment_var])
            
            if contingency_table.size == 0:
                return {'chi2': None, 'p_value': None, 'error': 'No valid data'}
            
            # Perform chi-square test
            chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
            
            return {
                'chi2': chi2,
                'p_value': p_value,
                'dof': dof,
                'error': None,
                'formatted_p': f"{p_value:.4f}" if p_value >= 0.0001 else "<0.0001"
            }
        except Exception as e:
            return {'chi2': None, 'p_value': None, 'error': str(e)}
    
    def perform_fisher_exact(self,
                           data: pd.DataFrame,
                           variable: str,
                           treatment_var: str) -> Dict[str, Any]:
        """
        Perform Fisher's exact test for 2x2 categorical data.
        
        Parameters
        ----------
        data : pd.DataFrame
            Input dataset
        variable : str
            Binary categorical variable
        treatment_var : str
            Binary treatment variable
            
        Returns
        -------
        dict
            Fisher's exact test results
        """
        try:
            contingency_table = pd.crosstab(data[variable], data[treatment_var])
            
            if contingency_table.shape != (2, 2):
                return {'odds_ratio': None, 'p_value': None, 
                       'error': 'Not a 2x2 table'}
            
            # Perform Fisher's exact test
            odds_ratio, p_value = stats.fisher_exact(contingency_table)
            
            return {
                'odds_ratio': odds_ratio,
                'p_value': p_value,
                'error': None,
                'formatted_p': f"{p_value:.4f}" if p_value >= 0.0001 else "<0.0001"
            }
        except Exception as e:
            return {'odds_ratio': None, 'p_value': None, 'error': str(e)} 