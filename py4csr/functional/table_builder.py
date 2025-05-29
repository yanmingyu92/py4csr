"""
Table Builder for Functional Clinical Reporting

This module provides table construction functionality that mirrors the SAS RRG
approach to building clinical tables from statistical components.
"""

from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
from pathlib import Path

from .config import FunctionalConfig, TableTemplate
from .statistical_templates import StatisticalTemplates


class TableResult:
    """Result object from table building process."""
    
    def __init__(self, data: pd.DataFrame, metadata: Dict[str, Any]):
        self.data = data
        self.metadata = metadata
        self.title = metadata.get('title', '')
        self.subtitle = metadata.get('subtitle', '')
        self.footnotes = metadata.get('footnotes', [])
        
    def __repr__(self):
        return f"TableResult(shape={self.data.shape}, title='{self.title[:50]}...')"


class TableBuilder:
    """
    Table builder class (equivalent to SAS RRG table generation process).
    
    This class takes table specifications and builds formatted tables using
    the statistical templates, similar to how SAS RRG generates tables from
    macro specifications.
    """
    
    def __init__(self, session, table_spec: Dict[str, Any]):
        """
        Initialize table builder.
        
        Parameters
        ----------
        session : ReportSession
            Parent report session containing data and configuration
        table_spec : dict
            Table specification dictionary
        """
        self.session = session
        self.spec = table_spec
        self.config = session.config
        self.templates = session.templates
        
    def build(self) -> TableResult:
        """
        Build table according to specification.
        
        Returns
        -------
        TableResult
            Built table with metadata
        """
        table_type = self.spec['type']
        
        # Get table template
        template = self.config.get_template(table_type)
        if not template:
            raise ValueError(f"No template found for table type: {table_type}")
        
        # Route to appropriate builder method
        if table_type == 'demographics':
            return self._build_demographics_table(template)
        elif table_type == 'disposition':
            return self._build_disposition_table(template)
        elif table_type == 'ae_summary':
            return self._build_ae_summary_table(template)
        elif table_type == 'ae_detail':
            return self._build_ae_detail_table(template)
        elif table_type == 'laboratory':
            return self._build_laboratory_table(template)
        elif table_type == 'efficacy':
            return self._build_efficacy_table(template)
        elif table_type == 'vital_signs':
            return self._build_vital_signs_table(template)
        else:
            raise ValueError(f"Unsupported table type: {table_type}")
    
    def _build_demographics_table(self, template: TableTemplate) -> TableResult:
        """Build demographics table (equivalent to SAS RRG demographics template)."""
        
        # Get ADSL data
        if 'ADSL' not in self.session.datasets:
            raise ValueError("ADSL dataset required for demographics table")
        
        adsl = self._get_filtered_data('ADSL')
        treatment_var = self.session.treatments['variable']
        
        # Use template variables or specification variables
        variables = self.spec.get('variables') or template.default_variables
        
        # Build table sections
        table_sections = []
        
        for variable in variables:
            if variable not in adsl.columns:
                print(f"Warning: Variable '{variable}' not found in ADSL, skipping")
                continue
            
            # Determine variable type
            var_type = self._determine_variable_type(adsl[variable])
            
            if var_type == 'continuous':
                stats_df = self.templates.calculate_continuous_statistics(
                    adsl, variable, treatment_var, 
                    statistics=['n', 'mean_sd', 'median', 'min_max']
                )
            else:
                stats_df = self.templates.calculate_categorical_statistics(
                    adsl, variable, treatment_var,
                    statistics=['n_percent']
                )
            
            # Add variable label
            stats_df['VARIABLE_LABEL'] = self._get_variable_label(variable)
            table_sections.append(stats_df)
        
        # Combine all sections
        if table_sections:
            combined_data = pd.concat(table_sections, ignore_index=True)
        else:
            combined_data = pd.DataFrame()
        
        # Format for display
        display_table = self._format_demographics_display(combined_data, treatment_var)
        
        # Create metadata
        metadata = {
            'title': self.spec.get('title', template.title_template),
            'subtitle': self._format_subtitle(template.subtitle_template),
            'footnotes': self.spec.get('footnotes', template.footnotes),
            'population': self.spec.get('population', 'safety'),
            'table_type': 'demographics'
        }
        
        return TableResult(display_table, metadata)
    
    def _build_disposition_table(self, template: TableTemplate) -> TableResult:
        """Build disposition table."""
        
        if 'ADSL' not in self.session.datasets:
            raise ValueError("ADSL dataset required for disposition table")
        
        adsl = self._get_filtered_data('ADSL')
        treatment_var = self.session.treatments['variable']
        
        # Use disposition reason variable
        disp_var = 'DCSREAS' if 'DCSREAS' in adsl.columns else 'DCREASCD'
        
        if disp_var not in adsl.columns:
            raise ValueError(f"Disposition variable not found in ADSL")
        
        # Calculate disposition statistics
        stats_df = self.templates.calculate_categorical_statistics(
            adsl, disp_var, treatment_var, statistics=['n_percent']
        )
        
        # Format for display
        display_table = self._format_disposition_display(stats_df, treatment_var)
        
        metadata = {
            'title': self.spec.get('title', template.title_template),
            'subtitle': self._format_subtitle(template.subtitle_template),
            'footnotes': self.spec.get('footnotes', template.footnotes),
            'population': 'randomized',
            'table_type': 'disposition'
        }
        
        return TableResult(display_table, metadata)
    
    def _build_ae_summary_table(self, template: TableTemplate) -> TableResult:
        """Build AE summary table."""
        
        if 'ADAE' not in self.session.datasets:
            raise ValueError("ADAE dataset required for AE summary table")
        
        adae = self._get_filtered_data('ADAE')
        treatment_var = self.session.treatments['variable']
        
        # Calculate AE summary statistics
        ae_stats = self.templates.calculate_ae_statistics(adae, treatment_var)
        
        # Create summary categories
        summary_stats = self._create_ae_summary_categories(adae, treatment_var)
        
        # Format for display
        display_table = self._format_ae_summary_display(summary_stats, treatment_var)
        
        metadata = {
            'title': self.spec.get('title', template.title_template),
            'subtitle': self._format_subtitle(template.subtitle_template),
            'footnotes': self.spec.get('footnotes', template.footnotes),
            'population': self.spec.get('population', 'safety'),
            'table_type': 'ae_summary'
        }
        
        return TableResult(display_table, metadata)
    
    def _build_ae_detail_table(self, template: TableTemplate) -> TableResult:
        """Build detailed AE table by SOC and PT."""
        
        if 'ADAE' not in self.session.datasets:
            raise ValueError("ADAE dataset required for AE detail table")
        
        adae = self._get_filtered_data('ADAE')
        treatment_var = self.session.treatments['variable']
        
        # Calculate detailed AE statistics
        ae_stats = self.templates.calculate_ae_statistics(adae, treatment_var)
        
        # Format for display
        display_table = self._format_ae_detail_display(ae_stats, treatment_var)
        
        metadata = {
            'title': self.spec.get('title', template.title_template),
            'subtitle': self._format_subtitle(template.subtitle_template),
            'footnotes': self.spec.get('footnotes', template.footnotes),
            'population': self.spec.get('population', 'safety'),
            'table_type': 'ae_detail'
        }
        
        return TableResult(display_table, metadata)
    
    def _build_laboratory_table(self, template: TableTemplate) -> TableResult:
        """Build laboratory parameters table."""
        
        if 'ADLB' not in self.session.datasets:
            raise ValueError("ADLB dataset required for laboratory table")
        
        adlb = self._get_filtered_data('ADLB')
        treatment_var = self.session.treatments['variable']
        
        # Get laboratory parameters
        lab_params = adlb['PARAMCD'].unique() if 'PARAMCD' in adlb.columns else []
        
        table_sections = []
        
        for param in lab_params:
            param_data = adlb[adlb['PARAMCD'] == param]
            
            # Use change from baseline if available
            value_var = 'CHG' if 'CHG' in param_data.columns else 'AVAL'
            
            if value_var in param_data.columns:
                stats_df = self.templates.calculate_continuous_statistics(
                    param_data, value_var, treatment_var,
                    statistics=['n', 'mean_sd', 'median', 'min_max']
                )
                stats_df['PARAMETER'] = param
                table_sections.append(stats_df)
        
        # Combine all parameters
        if table_sections:
            combined_data = pd.concat(table_sections, ignore_index=True)
        else:
            combined_data = pd.DataFrame()
        
        # Format for display
        display_table = self._format_laboratory_display(combined_data, treatment_var)
        
        metadata = {
            'title': self.spec.get('title', template.title_template),
            'subtitle': self._format_subtitle(template.subtitle_template),
            'footnotes': self.spec.get('footnotes', template.footnotes),
            'population': self.spec.get('population', 'safety'),
            'table_type': 'laboratory'
        }
        
        return TableResult(display_table, metadata)
    
    def _build_efficacy_table(self, template: TableTemplate) -> TableResult:
        """Build efficacy analysis table."""
        
        # This is a placeholder - actual efficacy tables would depend on study design
        # For now, create a simple efficacy summary
        
        if 'ADSL' not in self.session.datasets:
            raise ValueError("ADSL dataset required for efficacy table")
        
        adsl = self._get_filtered_data('ADSL')
        treatment_var = self.session.treatments['variable']
        
        # Simple efficacy placeholder
        display_table = pd.DataFrame({
            'Parameter': ['Primary Endpoint Analysis'],
            'Statistic': ['To be implemented'],
            **{trt: ['--'] for trt in sorted(adsl[treatment_var].unique())},
            'Total': ['--']
        })
        
        metadata = {
            'title': self.spec.get('title', template.title_template),
            'subtitle': self._format_subtitle(template.subtitle_template),
            'footnotes': self.spec.get('footnotes', template.footnotes),
            'population': self.spec.get('population', 'efficacy'),
            'table_type': 'efficacy'
        }
        
        return TableResult(display_table, metadata)
    
    def _build_vital_signs_table(self, template: TableTemplate) -> TableResult:
        """Build vital signs table."""
        
        if 'ADVS' not in self.session.datasets:
            raise ValueError("ADVS dataset required for vital signs table")
        
        advs = self._get_filtered_data('ADVS')
        treatment_var = self.session.treatments['variable']
        
        # Get vital signs parameters
        vs_params = advs['PARAMCD'].unique() if 'PARAMCD' in advs.columns else []
        
        table_sections = []
        
        for param in vs_params:
            param_data = advs[advs['PARAMCD'] == param]
            
            # Use change from baseline if available
            value_var = 'CHG' if 'CHG' in param_data.columns else 'AVAL'
            
            if value_var in param_data.columns:
                stats_df = self.templates.calculate_continuous_statistics(
                    param_data, value_var, treatment_var,
                    statistics=['n', 'mean_sd', 'median', 'min_max']
                )
                stats_df['PARAMETER'] = param
                table_sections.append(stats_df)
        
        # Combine all parameters
        if table_sections:
            combined_data = pd.concat(table_sections, ignore_index=True)
        else:
            combined_data = pd.DataFrame()
        
        # Format for display
        display_table = self._format_vital_signs_display(combined_data, treatment_var)
        
        metadata = {
            'title': self.spec.get('title', template.title_template),
            'subtitle': self._format_subtitle(template.subtitle_template),
            'footnotes': self.spec.get('footnotes', template.footnotes),
            'population': self.spec.get('population', 'safety'),
            'table_type': 'vital_signs'
        }
        
        return TableResult(display_table, metadata)
    
    def _get_filtered_data(self, dataset_name: str) -> pd.DataFrame:
        """Get filtered dataset based on population and filters."""
        
        if dataset_name not in self.session.datasets:
            raise ValueError(f"Dataset '{dataset_name}' not found")
        
        data = self.session.datasets[dataset_name]['data'].copy()
        
        # Apply population filter
        population = self.spec.get('population', 'safety')
        if population in self.session.populations:
            pop_filter = self.session.populations[population]
            try:
                data = data.query(pop_filter)
            except Exception as e:
                print(f"Warning: Failed to apply population filter '{pop_filter}': {e}")
        
        # Apply additional filters
        filters = self.spec.get('filters', {})
        for filter_name, filter_expr in filters.items():
            try:
                data = data.query(filter_expr)
            except Exception as e:
                print(f"Warning: Failed to apply filter '{filter_name}': {e}")
        
        return data
    
    def _determine_variable_type(self, series: pd.Series) -> str:
        """Determine if variable is continuous or categorical."""
        
        # Check if numeric
        if pd.api.types.is_numeric_dtype(series):
            # Check number of unique values
            unique_count = series.nunique()
            total_count = len(series.dropna())
            
            # If less than 10 unique values or less than 5% unique, treat as categorical
            if unique_count < 10 or (unique_count / total_count) < 0.05:
                return 'categorical'
            else:
                return 'continuous'
        else:
            return 'categorical'
    
    def _get_variable_label(self, variable: str) -> str:
        """Get variable label from dataset metadata or use variable name."""
        
        # Try to get from ADSL metadata
        if 'ADSL' in self.session.datasets:
            adsl_attrs = getattr(self.session.datasets['ADSL']['data'], 'attrs', {})
            var_labels = adsl_attrs.get('variable_labels', {})
            if variable in var_labels:
                return var_labels[variable]
        
        # Default labels for common variables
        default_labels = {
            'AGE': 'Age (years)',
            'AGEGR1': 'Age Group',
            'SEX': 'Sex',
            'RACE': 'Race',
            'WEIGHT': 'Weight (kg)',
            'HEIGHT': 'Height (cm)',
            'BMI': 'BMI (kg/m²)',
            'DCSREAS': 'Primary Reason for Discontinuation'
        }
        
        return default_labels.get(variable, variable)
    
    def _format_subtitle(self, subtitle_template: str) -> str:
        """Format subtitle template with session metadata."""
        
        replacements = {
            'study_title': self.session.metadata.get('title', 'Clinical Study'),
            'population_label': self._get_population_label()
        }
        
        formatted = subtitle_template
        for key, value in replacements.items():
            formatted = formatted.replace(f'{{{key}}}', str(value))
        
        return formatted
    
    def _get_population_label(self) -> str:
        """Get population label for subtitle."""
        
        population = self.spec.get('population', 'safety')
        
        labels = {
            'safety': 'Safety Analysis Population',
            'efficacy': 'Efficacy Analysis Population',
            'itt': 'Intent-to-Treat Population',
            'randomized': 'All Randomized Subjects'
        }
        
        return labels.get(population, f'{population.title()} Population')
    
    def _format_demographics_display(self, stats_df: pd.DataFrame, treatment_var: str) -> pd.DataFrame:
        """Format demographics statistics for display."""
        
        if stats_df.empty:
            return pd.DataFrame()
        
        # Get treatment levels
        treatments = sorted(stats_df['TREATMENT'].unique())
        treatments = [t for t in treatments if t != 'Total'] + ['Total']
        
        # Pivot data for display
        display_rows = []
        
        for variable in stats_df['VARIABLE'].unique():
            var_data = stats_df[stats_df['VARIABLE'] == variable]
            var_label = var_data['VARIABLE_LABEL'].iloc[0] if 'VARIABLE_LABEL' in var_data.columns else variable
            
            # Check if categorical (has CATEGORY column)
            if 'CATEGORY' in var_data.columns:
                # Categorical variable
                for category in sorted(var_data['CATEGORY'].unique()):
                    cat_data = var_data[var_data['CATEGORY'] == category]
                    
                    row = {'Parameter': f'  {category}'}
                    for treatment in treatments:
                        trt_data = cat_data[cat_data['TREATMENT'] == treatment]
                        if not trt_data.empty:
                            row[treatment] = trt_data['FORMATTED_VALUE'].iloc[0]
                        else:
                            row[treatment] = '0 (0.0%)'
                    
                    display_rows.append(row)
            else:
                # Continuous variable - group by statistic
                for statistic in var_data['STATISTIC'].unique():
                    stat_data = var_data[var_data['STATISTIC'] == statistic]
                    
                    row = {'Parameter': f'{var_label} - {statistic}'}
                    for treatment in treatments:
                        trt_data = stat_data[stat_data['TREATMENT'] == treatment]
                        if not trt_data.empty:
                            row[treatment] = trt_data['FORMATTED_VALUE'].iloc[0]
                        else:
                            row[treatment] = ''
                    
                    display_rows.append(row)
        
        return pd.DataFrame(display_rows)
    
    def _format_disposition_display(self, stats_df: pd.DataFrame, treatment_var: str) -> pd.DataFrame:
        """Format disposition statistics for display."""
        
        if stats_df.empty:
            return pd.DataFrame()
        
        treatments = sorted(stats_df['TREATMENT'].unique())
        treatments = [t for t in treatments if t != 'Total'] + ['Total']
        
        display_rows = []
        
        for category in sorted(stats_df['CATEGORY'].unique()):
            cat_data = stats_df[stats_df['CATEGORY'] == category]
            
            row = {'Disposition': category}
            for treatment in treatments:
                trt_data = cat_data[cat_data['TREATMENT'] == treatment]
                if not trt_data.empty:
                    row[treatment] = trt_data['FORMATTED_VALUE'].iloc[0]
                else:
                    row[treatment] = '0 (0.0%)'
            
            display_rows.append(row)
        
        return pd.DataFrame(display_rows)
    
    def _create_ae_summary_categories(self, adae: pd.DataFrame, treatment_var: str) -> pd.DataFrame:
        """Create AE summary categories."""
        
        subject_var = 'USUBJID' if 'USUBJID' in adae.columns else 'SUBJID'
        
        # Get denominators from ADSL
        if 'ADSL' in self.session.datasets:
            adsl = self._get_filtered_data('ADSL')
            denominators = adsl.groupby(treatment_var).size().to_dict()
        else:
            denominators = adae.groupby(treatment_var)[subject_var].nunique().to_dict()
        
        results = []
        treatments = sorted(adae[treatment_var].unique())
        
        # Summary categories
        categories = [
            ('Any adverse event', adae),
            ('Any serious adverse event', adae[adae.get('AESER', 'N') == 'Y'] if 'AESER' in adae.columns else pd.DataFrame()),
            ('Any severe adverse event', adae[adae.get('AESEV', '') == 'SEVERE'] if 'AESEV' in adae.columns else pd.DataFrame()),
            ('Any drug-related adverse event', adae[adae.get('AEREL', '').isin(['RELATED', 'PROBABLE', 'POSSIBLE'])] if 'AEREL' in adae.columns else pd.DataFrame())
        ]
        
        for category_name, category_data in categories:
            if category_data.empty:
                continue
                
            for treatment in treatments:
                trt_data = category_data[category_data[treatment_var] == treatment]
                subject_count = trt_data[subject_var].nunique() if not trt_data.empty else 0
                denominator = denominators.get(treatment, 1)
                percentage = (subject_count / denominator * 100) if denominator > 0 else 0
                
                results.append({
                    'CATEGORY': category_name,
                    'TREATMENT': treatment,
                    'SUBJECT_COUNT': subject_count,
                    'PERCENTAGE': percentage,
                    'FORMATTED_VALUE': f"{subject_count} ({percentage:.1f}%)"
                })
        
        return pd.DataFrame(results)
    
    def _format_ae_summary_display(self, stats_df: pd.DataFrame, treatment_var: str) -> pd.DataFrame:
        """Format AE summary for display."""
        
        if stats_df.empty:
            return pd.DataFrame()
        
        treatments = sorted(stats_df['TREATMENT'].unique())
        
        display_rows = []
        
        for category in stats_df['CATEGORY'].unique():
            cat_data = stats_df[stats_df['CATEGORY'] == category]
            
            row = {'Adverse Event Category': category}
            for treatment in treatments:
                trt_data = cat_data[cat_data['TREATMENT'] == treatment]
                if not trt_data.empty:
                    row[treatment] = trt_data['FORMATTED_VALUE'].iloc[0]
                else:
                    row[treatment] = '0 (0.0%)'
            
            display_rows.append(row)
        
        return pd.DataFrame(display_rows)
    
    def _format_ae_detail_display(self, ae_stats: pd.DataFrame, treatment_var: str) -> pd.DataFrame:
        """Format detailed AE statistics for display."""
        
        if ae_stats.empty:
            return pd.DataFrame()
        
        treatments = sorted(ae_stats['TREATMENT'].unique())
        
        display_rows = []
        
        # Group by SOC, then PT
        for soc in sorted(ae_stats[ae_stats['LEVEL'] == 'SOC']['TERM'].unique()):
            # Add SOC header
            soc_data = ae_stats[(ae_stats['LEVEL'] == 'SOC') & (ae_stats['TERM'] == soc)]
            
            soc_row = {'System Organ Class / Preferred Term': soc}
            for treatment in treatments:
                trt_data = soc_data[soc_data['TREATMENT'] == treatment]
                if not trt_data.empty:
                    soc_row[treatment] = trt_data['FORMATTED_VALUE'].iloc[0]
                else:
                    soc_row[treatment] = '0 (0.0%)'
            
            display_rows.append(soc_row)
            
            # Add PTs under this SOC
            pt_data = ae_stats[(ae_stats['LEVEL'] == 'PT') & (ae_stats['PARENT_TERM'] == soc)]
            
            for pt in sorted(pt_data['TERM'].unique()):
                pt_row_data = pt_data[pt_data['TERM'] == pt]
                
                pt_row = {'System Organ Class / Preferred Term': f'  {pt}'}
                for treatment in treatments:
                    trt_data = pt_row_data[pt_row_data['TREATMENT'] == treatment]
                    if not trt_data.empty:
                        pt_row[treatment] = trt_data['FORMATTED_VALUE'].iloc[0]
                    else:
                        pt_row[treatment] = '0 (0.0%)'
                
                display_rows.append(pt_row)
        
        return pd.DataFrame(display_rows)
    
    def _format_laboratory_display(self, stats_df: pd.DataFrame, treatment_var: str) -> pd.DataFrame:
        """Format laboratory statistics for display."""
        
        if stats_df.empty:
            return pd.DataFrame()
        
        treatments = sorted(stats_df['TREATMENT'].unique())
        treatments = [t for t in treatments if t != 'Total'] + ['Total']
        
        display_rows = []
        
        for parameter in stats_df['PARAMETER'].unique():
            param_data = stats_df[stats_df['PARAMETER'] == parameter]
            
            for statistic in param_data['STATISTIC'].unique():
                stat_data = param_data[param_data['STATISTIC'] == statistic]
                
                row = {'Parameter': f'{parameter} - {statistic}'}
                for treatment in treatments:
                    trt_data = stat_data[stat_data['TREATMENT'] == treatment]
                    if not trt_data.empty:
                        row[treatment] = trt_data['FORMATTED_VALUE'].iloc[0]
                    else:
                        row[treatment] = ''
                
                display_rows.append(row)
        
        return pd.DataFrame(display_rows)
    
    def _format_vital_signs_display(self, stats_df: pd.DataFrame, treatment_var: str) -> pd.DataFrame:
        """Format vital signs statistics for display."""
        
        # Same format as laboratory
        return self._format_laboratory_display(stats_df, treatment_var) 