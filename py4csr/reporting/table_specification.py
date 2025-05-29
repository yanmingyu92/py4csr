"""
Table specification system for py4csr functional reporting.

This module defines how tables are specified and configured,
similar to the SAS RRG system's variable and table definitions.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
import pandas as pd

from ..config import ReportConfig


@dataclass
class TableSpecification:
    """
    Specification for a single table.
    
    This class defines all parameters needed to generate a specific table,
    similar to the SAS RRG system's variable definitions.
    
    Parameters
    ----------
    type : str
        Type of table (e.g., 'demographics', 'ae_summary')
    config : ReportConfig
        Configuration for the report
    datasets : dict
        Available datasets
    populations : dict
        Population definitions
    treatments : dict
        Treatment definitions
    title : str, optional
        Table title
    subtitle : str, optional
        Table subtitle
    footnotes : list, optional
        Table footnotes
    population : str
        Population to use for analysis
    variables : list, optional
        Variables to include in analysis
    statistics : list, optional
        Statistics to calculate
    grouping : list, optional
        Grouping variables
    filters : dict, optional
        Additional filters to apply
    """
    
    type: str
    config: ReportConfig
    datasets: Dict[str, Any]
    populations: Dict[str, str]
    treatments: Dict[str, Any]
    title: Optional[str] = None
    subtitle: Optional[str] = None
    footnotes: Optional[List[str]] = None
    population: str = "safety"
    variables: Optional[List[str]] = None
    statistics: Optional[List[str]] = None
    grouping: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None
    analysis_type: Optional[str] = None
    parameters: Optional[List[str]] = None
    visits: Optional[List[str]] = None
    endpoint: Optional[str] = None
    time_var: Optional[str] = None
    event_var: Optional[str] = None
    min_frequency: Optional[int] = None
    sort_by: Optional[str] = None
    include_total: bool = True
    page_by: Optional[str] = None
    custom_template: Optional[str] = None
    
    def get_filename(self) -> str:
        """
        Generate filename for this table.
        
        Returns
        -------
        str
            Filename without extension
        """
        filename_map = {
            'demographics': 'tlf_base',
            'disposition': 'tbl_disp',
            'ae_summary': 'tlf_ae_summary',
            'ae_detail': 'tlf_spec_ae',
            'efficacy': 'tlf_eff',
            'laboratory': 'tlf_lab',
            'survival': 'tlf_km',
            'vital_signs': 'tlf_vs',
            'concomitant_meds': 'tlf_cm',
            'medical_history': 'tlf_mh',
            'exposure': 'tlf_exp',
            'pk_parameters': 'tlf_pk',
            'immunogenicity': 'tlf_immuno',
            'biomarkers': 'tlf_biomarker',
            'protocol_deviations': 'tlf_pd',
            'prior_therapy': 'tlf_prior',
            'ecg_parameters': 'tlf_ecg',
            'laboratory_shifts': 'tlf_lab_shift',
            'laboratory_outliers': 'tlf_lab_outlier'
        }
        return filename_map.get(self.type, f'tlf_{self.type}')
    
    def get_data(self) -> pd.DataFrame:
        """
        Get filtered data for this table.
        
        Returns
        -------
        pd.DataFrame
            Filtered dataset for analysis
        """
        # Determine primary dataset
        dataset_map = {
            'demographics': 'adsl',
            'disposition': 'adsl', 
            'ae_summary': 'adae',
            'ae_detail': 'adae',
            'efficacy': 'adlb',
            'laboratory': 'adlb',
            'survival': 'adsl',
            'vital_signs': 'advs',
            'concomitant_meds': 'adcm',
            'medical_history': 'admh',
            'exposure': 'adex',
            'pk_parameters': 'adpp',
            'immunogenicity': 'adis',
            'biomarkers': 'adlb',
            'protocol_deviations': 'addv',
            'prior_therapy': 'adcm',
            'ecg_parameters': 'adeg',
            'laboratory_shifts': 'adlb',
            'laboratory_outliers': 'adlb'
        }
        
        primary_dataset = dataset_map.get(self.type, 'adsl')
        
        if primary_dataset not in self.datasets:
            raise ValueError(f"Required dataset '{primary_dataset}' not found for table type '{self.type}'")
        
        data = self.datasets[primary_dataset]['data'].copy()
        
        # Apply population filter
        if self.population in self.populations:
            population_filter = self.populations[self.population]
            try:
                data = data.query(population_filter)
            except Exception as e:
                raise ValueError(f"Failed to apply population filter '{population_filter}': {str(e)}")
        
        # Apply additional filters
        if self.filters:
            for filter_name, filter_expr in self.filters.items():
                try:
                    data = data.query(filter_expr)
                except Exception as e:
                    raise ValueError(f"Failed to apply filter '{filter_name}': {str(e)}")
        
        return data
    
    def get_treatment_variable(self) -> str:
        """
        Get the treatment variable to use for analysis.
        
        Returns
        -------
        str
            Treatment variable name
        """
        return self.treatments.get('variable', 'TRT01P')
    
    def get_treatment_decode(self) -> str:
        """
        Get the treatment decode variable.
        
        Returns
        -------
        str
            Treatment decode variable name
        """
        return self.treatments.get('decode', self.get_treatment_variable())
    
    def get_default_variables(self) -> List[str]:
        """
        Get default variables for this table type.
        
        Returns
        -------
        list
            Default variable list
        """
        defaults = {
            'demographics': ['AGE', 'AGEGR1', 'SEX', 'RACE', 'WEIGHT', 'HEIGHT', 'BMI'],
            'disposition': ['DCSREAS', 'DCREASCD'],
            'ae_summary': ['AESEV', 'AEREL', 'AESER'],
            'ae_detail': ['AEBODSYS', 'AEDECOD', 'AESEV'],
            'efficacy': ['CHG', 'PCHG'],
            'laboratory': ['PARAMCD', 'AVAL', 'CHG'],
            'vital_signs': ['PARAMCD', 'AVAL', 'CHG'],
            'concomitant_meds': ['CMDECOD', 'CMCLAS'],
            'medical_history': ['MHDECOD', 'MHBODSYS'],
            'exposure': ['EXDOSE', 'EXDUR'],
            'survival': ['AVAL', 'CNSR']
        }
        return defaults.get(self.type, [])
    
    def get_default_statistics(self) -> List[str]:
        """
        Get default statistics for this table type.
        
        Returns
        -------
        list
            Default statistics list
        """
        defaults = {
            'demographics': ['n', 'mean_sd', 'median', 'min_max'],
            'disposition': ['n', 'percent'],
            'ae_summary': ['n', 'percent'],
            'ae_detail': ['n', 'percent'],
            'efficacy': ['n', 'mean_sd', 'median', 'min_max'],
            'laboratory': ['n', 'mean_sd', 'median', 'min_max'],
            'vital_signs': ['n', 'mean_sd', 'median', 'min_max'],
            'concomitant_meds': ['n', 'percent'],
            'medical_history': ['n', 'percent'],
            'exposure': ['n', 'mean_sd', 'median', 'min_max'],
            'survival': ['n', 'median', 'ci_95']
        }
        return defaults.get(self.type, ['n', 'mean_sd'])
    
    def get_title(self) -> str:
        """
        Get the table title.
        
        Returns
        -------
        str
            Table title
        """
        if self.title:
            return self.title
        
        default_titles = {
            'demographics': 'Baseline Demographics and Clinical Characteristics',
            'disposition': 'Subject Disposition',
            'ae_summary': 'Summary of Adverse Events',
            'ae_detail': 'Adverse Events by System Organ Class and Preferred Term',
            'efficacy': 'Analysis of Primary Efficacy Endpoint',
            'laboratory': 'Laboratory Parameters - Summary Statistics',
            'survival': 'Kaplan-Meier Analysis of Time to Event',
            'vital_signs': 'Vital Signs - Summary Statistics',
            'concomitant_meds': 'Concomitant Medications',
            'medical_history': 'Medical History',
            'exposure': 'Extent of Exposure'
        }
        return default_titles.get(self.type, f'{self.type.title()} Analysis')
    
    def get_subtitle(self) -> str:
        """
        Get the table subtitle.
        
        Returns
        -------
        str
            Table subtitle
        """
        if self.subtitle:
            return self.subtitle
        
        population_labels = {
            'safety': 'Safety Analysis Population',
            'efficacy': 'Efficacy Analysis Population',
            'itt': 'Intent-to-Treat Population',
            'pp': 'Per-Protocol Population',
            'randomized': 'All Randomized Subjects',
            'treated': 'All Treated Subjects'
        }
        return population_labels.get(self.population, f'{self.population.title()} Population')
    
    def get_footnotes(self) -> List[str]:
        """
        Get table footnotes.
        
        Returns
        -------
        list
            Table footnotes
        """
        if self.footnotes:
            return self.footnotes
        
        default_footnotes = {
            'demographics': [
                'Values are mean (SD) for continuous variables and n (%) for categorical variables.',
                'Missing values are excluded from percentage calculations.'
            ],
            'disposition': [
                'Percentages are based on the number of randomized subjects.'
            ],
            'ae_summary': [
                'Each subject is counted once per category.',
                'Percentages are based on the number of subjects in the safety population.'
            ],
            'ae_detail': [
                'Subjects with multiple events in the same category are counted once.',
                'Events are sorted by decreasing frequency in the total column.'
            ],
            'efficacy': [
                'Analysis based on ANCOVA model with treatment and baseline as covariates.',
                'Missing values are excluded from the analysis.'
            ],
            'laboratory': [
                'Values are mean (SD) unless otherwise specified.',
                'Change from baseline = Post-baseline value - Baseline value.'
            ],
            'survival': [
                'Kaplan-Meier estimates with 95% confidence intervals.',
                'Subjects without events are censored at last known alive date.'
            ]
        }
        return default_footnotes.get(self.type, [])
    
    def validate(self) -> List[str]:
        """
        Validate the table specification.
        
        Returns
        -------
        list
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required datasets
        primary_dataset = self.get_data()
        if primary_dataset.empty:
            errors.append(f"No data available after applying filters for {self.type} table")
        
        # Check treatment variable
        trt_var = self.get_treatment_variable()
        if trt_var not in primary_dataset.columns:
            errors.append(f"Treatment variable '{trt_var}' not found in dataset")
        
        # Check variables exist
        if self.variables:
            missing_vars = [var for var in self.variables if var not in primary_dataset.columns]
            if missing_vars:
                errors.append(f"Variables not found in dataset: {missing_vars}")
        
        # Check population definition
        if self.population not in self.populations:
            errors.append(f"Population '{self.population}' not defined")
        
        return errors 