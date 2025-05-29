"""
Demographics table generator for py4csr functional reporting system.

This module generates demographic and baseline characteristics tables,
equivalent to the SAS RRG system's demographic analysis templates.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any
from datetime import datetime

from .base_generator import BaseTableGenerator
from ..table_specification import TableSpecification
from ..table_result import TableResult


class DemographicsGenerator(BaseTableGenerator):
    """
    Generator for demographics and baseline characteristics tables.
    
    This generator creates comprehensive demographic summaries with both
    categorical and continuous variables, following ICH E3 guidelines.
    """
    
    def __init__(self):
        super().__init__()
        self._register_templates()
    
    def generate(self, spec: TableSpecification) -> TableResult:
        """
        Generate demographics table.
        
        Parameters
        ----------
        spec : TableSpecification
            Table specification
            
        Returns
        -------
        TableResult
            Generated demographics table
        """
        # Get and validate data
        data = spec.get_data()
        validation_result = self.validate_data(data, spec)
        
        if not validation_result['passed']:
            raise ValueError(f"Data validation failed: {validation_result['errors']}")
        
        # Get variables to analyze
        variables = spec.variables or spec.get_default_variables()
        trt_var = spec.get_treatment_variable()
        
        # Generate summary for each variable
        summary_results = []
        
        for var in variables:
            if var in data.columns:
                if self._is_categorical(data[var]):
                    var_summary = self._generate_categorical_summary(data, var, trt_var, spec)
                else:
                    var_summary = self._generate_continuous_summary(data, var, trt_var, spec)
                
                if not var_summary.empty:
                    summary_results.append(var_summary)
        
        # Combine all results
        if summary_results:
            final_summary = pd.concat(summary_results, ignore_index=True)
        else:
            final_summary = pd.DataFrame()
        
        # Post-process data
        final_summary = self.post_process_data(final_summary, spec)
        
        # Create RTF table
        rtf_table = self.create_rtf_table(final_summary, spec)
        
        # Generate metadata
        metadata = self.generate_metadata(spec)
        metadata.update({
            'n_variables': len(variables),
            'n_subjects': len(data),
            'treatment_groups': data[trt_var].value_counts().to_dict()
        })
        
        return TableResult(
            data=final_summary,
            rtf_table=rtf_table,
            metadata=metadata,
            validation_results=validation_result
        )
    
    def _generate_categorical_summary(self, data: pd.DataFrame, var: str, 
                                    trt_var: str, spec: TableSpecification) -> pd.DataFrame:
        """Generate summary for categorical variable."""
        
        # Create frequency table
        freq_data = []
        
        # Get unique categories
        categories = data[var].dropna().unique()
        treatments = data[trt_var].unique()
        
        # Overall header
        var_label = self._get_variable_label(var)
        header_row = {
            'Variable': var_label,
            'Category': '',
            'Statistic': 'n (%)'
        }
        
        # Add treatment columns
        for trt in treatments:
            header_row[trt] = ''
        
        # Add total column if specified
        if spec.include_total:
            header_row['Total'] = ''
        
        freq_data.append(header_row)
        
        # Generate statistics for each category
        for category in sorted(categories):
            if pd.isna(category):
                continue
                
            row = {
                'Variable': '',
                'Category': f'  {category}',
                'Statistic': ''
            }
            
            # Calculate for each treatment
            for trt in treatments:
                trt_data = data[data[trt_var] == trt]
                n_category = len(trt_data[trt_data[var] == category])
                n_total = len(trt_data[trt_data[var].notna()])
                
                if n_total > 0:
                    pct = (n_category / n_total) * 100
                    row[trt] = f"{n_category} ({pct:.1f}%)"
                else:
                    row[trt] = "0"
            
            # Total column
            if spec.include_total:
                total_data = data[data[var].notna()]
                n_category_total = len(total_data[total_data[var] == category])
                n_total_total = len(total_data)
                
                if n_total_total > 0:
                    pct_total = (n_category_total / n_total_total) * 100
                    row['Total'] = f"{n_category_total} ({pct_total:.1f}%)"
                else:
                    row['Total'] = "0"
            
            freq_data.append(row)
        
        return pd.DataFrame(freq_data)
    
    def _generate_continuous_summary(self, data: pd.DataFrame, var: str,
                                   trt_var: str, spec: TableSpecification) -> pd.DataFrame:
        """Generate summary for continuous variable."""
        
        # Get statistics to calculate
        statistics = spec.statistics or ['n', 'mean_sd', 'median', 'min_max']
        
        summary_data = []
        treatments = data[trt_var].unique()
        
        # Variable header
        var_label = self._get_variable_label(var)
        
        # Generate each statistic
        for stat in statistics:
            row = {
                'Variable': var_label if stat == statistics[0] else '',
                'Category': '',
                'Statistic': self._get_statistic_label(stat)
            }
            
            # Calculate for each treatment
            for trt in treatments:
                trt_data = data[data[trt_var] == trt][var].dropna()
                
                if len(trt_data) > 0:
                    stat_value = self._calculate_statistic(trt_data, stat)
                    row[trt] = self.format_statistics(stat_value, stat, spec.config)
                else:
                    row[trt] = ""
            
            # Total column
            if spec.include_total:
                total_data = data[var].dropna()
                if len(total_data) > 0:
                    stat_value = self._calculate_statistic(total_data, stat)
                    row['Total'] = self.format_statistics(stat_value, stat, spec.config)
                else:
                    row['Total'] = ""
            
            summary_data.append(row)
        
        return pd.DataFrame(summary_data)
    
    def _calculate_statistic(self, series: pd.Series, stat: str) -> Any:
        """Calculate a specific statistic."""
        if stat == 'n':
            return len(series)
        elif stat == 'mean':
            return series.mean()
        elif stat == 'std':
            return series.std()
        elif stat == 'mean_sd':
            return f"{series.mean():.1f} ({series.std():.2f})"
        elif stat == 'median':
            return series.median()
        elif stat == 'min':
            return series.min()
        elif stat == 'max':
            return series.max()
        elif stat == 'min_max':
            return f"{series.min():.0f}, {series.max():.0f}"
        elif stat == 'q1':
            return series.quantile(0.25)
        elif stat == 'q3':
            return series.quantile(0.75)
        elif stat == 'q1_q3':
            return f"{series.quantile(0.25):.1f}, {series.quantile(0.75):.1f}"
        else:
            return ""
    
    def _get_statistic_label(self, stat: str) -> str:
        """Get display label for statistic."""
        labels = {
            'n': 'n',
            'mean': 'Mean',
            'std': 'SD',
            'mean_sd': 'Mean (SD)',
            'median': 'Median',
            'min': 'Min',
            'max': 'Max',
            'min_max': 'Min, Max',
            'q1': 'Q1',
            'q3': 'Q3',
            'q1_q3': 'Q1, Q3'
        }
        return labels.get(stat, stat)
    
    def _get_variable_label(self, var: str) -> str:
        """Get display label for variable."""
        labels = {
            'AGE': 'Age (years)',
            'AGEGR1': 'Age Group',
            'SEX': 'Sex',
            'RACE': 'Race',
            'WEIGHT': 'Weight (kg)',
            'HEIGHT': 'Height (cm)',
            'BMI': 'BMI (kg/m²)',
            'BMIGR1': 'BMI Category'
        }
        return labels.get(var, var)
    
    def _is_categorical(self, series: pd.Series) -> bool:
        """Determine if a variable is categorical."""
        # Check data type
        if series.dtype == 'object' or series.dtype.name == 'category':
            return True
        
        # Check number of unique values
        n_unique = series.nunique()
        n_total = len(series.dropna())
        
        # If less than 10 unique values or less than 5% unique, treat as categorical
        if n_unique < 10 or (n_unique / n_total) < 0.05:
            return True
        
        return False
    
    def _register_templates(self):
        """Register demographic analysis templates."""
        
        def continuous_template(data: pd.DataFrame, var: str, by_var: str, **kwargs):
            """Template for continuous variable analysis."""
            stats = kwargs.get('stats', ['n', 'mean', 'std', 'median', 'min', 'max'])
            result = data.groupby(by_var)[var].agg(stats).round(2)
            return result.reset_index()
        
        def categorical_template(data: pd.DataFrame, var: str, by_var: str, **kwargs):
            """Template for categorical variable analysis."""
            crosstab = pd.crosstab(data[var], data[by_var], margins=True)
            pct_tab = pd.crosstab(data[var], data[by_var], normalize='columns') * 100
            
            # Combine counts and percentages
            result_data = []
            for category in crosstab.index[:-1]:  # Exclude 'All' row
                row = {'Category': category}
                for treatment in crosstab.columns[:-1]:  # Exclude 'All' column
                    n = crosstab.loc[category, treatment]
                    pct = pct_tab.loc[category, treatment]
                    row[f'{treatment}'] = f"{n} ({pct:.1f}%)"
                result_data.append(row)
            
            return pd.DataFrame(result_data)
        
        self.register_template('continuous_summary', continuous_template)
        self.register_template('categorical_summary', categorical_template) 