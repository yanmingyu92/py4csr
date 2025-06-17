"""
ClinicalReport - Core RRG-Inspired Declarative Reporting Class

This class implements the main interface for creating clinical reports
using a declarative programming model similar to RRG.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from datetime import datetime

from .clinical_config import ClinicalConfig
from .clinical_statistics import ClinicalStatistics
from .clinical_rtf import ClinicalRTFGenerator


class ClinicalReport:
    """
    RRG-Inspired Clinical Report Generator
    
    This class provides a declarative interface for creating clinical tables
    with automatic statistical calculations and professional formatting.
    
    Example:
        report = ClinicalReport(dataset=adsl, population="safety")
        report.define_report(title="Demographics")
        report.add_treatment(variable="TRT01P")
        report.add_variable(name="AGE", label="Age (years)")
        report.generate("demographics.rtf")
    """
    
    def __init__(self, 
                 dataset: pd.DataFrame,
                 population: str = "safety",
                 study: Optional[str] = None,
                 config: Optional[ClinicalConfig] = None):
        """
        Initialize Clinical Report
        
        Args:
            dataset: Primary analysis dataset (e.g., ADSL)
            population: Analysis population ("safety", "efficacy", "itt", "pp")
            study: Study identifier
            config: Clinical configuration object
        """
        self.dataset = dataset.copy()
        self.population = population
        self.study = study or "Clinical Study"
        self.config = config or ClinicalConfig()
        
        # Report structure
        self.title = ""
        self.subtitle = ""
        self.footnotes = []
        self.population_filter = None
        
        # Variables and treatments
        self.variables = []
        self.treatments = []
        self.groups = []
        
        # Generated data
        self._report_data = None
        self._metadata = {}
        
        # Initialize statistics engine
        self.stats_engine = ClinicalStatistics(self.config)
        
        # Initialize RTF generator
        self.rtf_generator = ClinicalRTFGenerator(self.config)
        
        print(f"✓ ClinicalReport initialized: {len(dataset)} subjects, {population} population")
    
    def define_report(self,
                     title: str,
                     subtitle: str = "",
                     footnotes: Optional[List[str]] = None,
                     population_filter: Optional[str] = None):
        """
        Define report structure and metadata
        
        Args:
            title: Main table title
            subtitle: Table subtitle
            footnotes: List of footnote strings
            population_filter: Additional population filter (pandas query string)
        """
        self.title = title
        self.subtitle = subtitle
        self.footnotes = footnotes or []
        self.population_filter = population_filter
        
        # Add default population subtitle if not provided
        if not subtitle:
            pop_labels = {
                'safety': 'Safety Analysis Population',
                'efficacy': 'Efficacy Analysis Population', 
                'itt': 'Intent-to-Treat Population',
                'pp': 'Per-Protocol Population'
            }
            self.subtitle = pop_labels.get(self.population, f'{self.population.title()} Population')
        
        print(f"✓ Report defined: {title}")
    
    def add_treatment(self,
                     variable: str,
                     label: Optional[str] = None,
                     include_total: bool = True,
                     values: Optional[List] = None):
        """
        Add treatment grouping variable
        
        Args:
            variable: Treatment variable name in dataset
            label: Display label for treatment
            include_total: Whether to include "Total" column
            values: Specific treatment values to include
        """
        treatment = {
            'variable': variable,
            'label': label or variable,
            'include_total': include_total,
            'values': values,
            'type': 'treatment'
        }
        
        self.treatments.append(treatment)
        
        # Validate treatment variable exists
        if variable not in self.dataset.columns:
            raise ValueError(f"Treatment variable '{variable}' not found in dataset")
        
        trt_values = self.dataset[variable].unique()
        print(f"✓ Treatment added: {variable} ({len(trt_values)} groups)")
    
    def add_variable(self,
                    name: str,
                    label: str,
                    stats: Optional[List[str]] = None,
                    where: Optional[str] = None,
                    indent: int = 0,
                    decimal_places: Optional[int] = None):
        """
        Add continuous variable with automatic statistics
        
        Args:
            name: Variable name in dataset
            label: Display label
            stats: List of statistics to calculate
            where: Additional filter condition
            indent: Indentation level
            decimal_places: Number of decimal places
        """
        if stats is None:
            stats = self.config.default_continuous_stats
        
        variable = {
            'name': name,
            'label': label,
            'type': 'continuous',
            'stats': stats,
            'where': where,
            'indent': indent,
            'decimal_places': decimal_places or self.config.get_decimal_places(name)
        }
        
        self.variables.append(variable)
        
        # Validate variable exists
        if name not in self.dataset.columns:
            raise ValueError(f"Variable '{name}' not found in dataset")
        
        print(f"✓ Continuous variable added: {name} ({', '.join(stats)})")
    
    def add_categorical(self,
                       name: str,
                       label: str,
                       stats: Optional[List[str]] = None,
                       where: Optional[str] = None,
                       values: Optional[List] = None,
                       indent: int = 0,
                       show_missing: bool = True):
        """
        Add categorical variable with automatic counts/percentages
        
        Args:
            name: Variable name in dataset
            label: Display label
            stats: List of statistics to calculate
            where: Additional filter condition
            values: Specific values to include
            indent: Indentation level
            show_missing: Whether to show missing values
        """
        if stats is None:
            stats = self.config.default_categorical_stats
        
        variable = {
            'name': name,
            'label': label,
            'type': 'categorical',
            'stats': stats,
            'where': where,
            'values': values,
            'indent': indent,
            'show_missing': show_missing
        }
        
        self.variables.append(variable)
        
        # Validate variable exists
        if name not in self.dataset.columns:
            raise ValueError(f"Variable '{name}' not found in dataset")
        
        cat_values = self.dataset[name].unique()
        print(f"✓ Categorical variable added: {name} ({len(cat_values)} categories)")
    
    def add_group(self,
                 variable: str,
                 label: str,
                 page_break: bool = False):
        """
        Add grouping/stratification variable
        
        Args:
            variable: Grouping variable name
            label: Display label for group
            page_break: Whether to add page breaks between groups
        """
        group = {
            'variable': variable,
            'label': label,
            'page_break': page_break,
            'type': 'group'
        }
        
        self.groups.append(group)
        
        # Validate grouping variable exists
        if variable not in self.dataset.columns:
            raise ValueError(f"Grouping variable '{variable}' not found in dataset")
        
        group_values = self.dataset[variable].unique()
        print(f"✓ Grouping added: {variable} ({len(group_values)} groups)")
    
    def _apply_population_filter(self) -> pd.DataFrame:
        """Apply population filters to dataset"""
        filtered_data = self.dataset.copy()
        
        # Apply population-specific filter
        pop_filters = {
            'safety': 'SAFFL == "Y"' if 'SAFFL' in filtered_data.columns else None,
            'efficacy': 'EFFFL == "Y"' if 'EFFFL' in filtered_data.columns else None,
            'itt': 'ITTFL == "Y"' if 'ITTFL' in filtered_data.columns else None,
            'pp': 'PPROTFL == "Y"' if 'PPROTFL' in filtered_data.columns else None
        }
        
        pop_filter = pop_filters.get(self.population)
        if pop_filter:
            try:
                filtered_data = filtered_data.query(pop_filter)
                print(f"✓ Population filter applied: {len(filtered_data)} subjects")
            except Exception as e:
                print(f"⚠ Population filter failed: {e}")
        
        # Apply additional filter if provided
        if self.population_filter:
            try:
                filtered_data = filtered_data.query(self.population_filter)
                print(f"✓ Additional filter applied: {len(filtered_data)} subjects")
            except Exception as e:
                print(f"⚠ Additional filter failed: {e}")
        
        return filtered_data
    
    def _calculate_statistics(self) -> pd.DataFrame:
        """Calculate all statistics for the report"""
        print("\n📊 Calculating statistics...")
        
        # Apply population filters
        analysis_data = self._apply_population_filter()
        
        if analysis_data.empty:
            raise ValueError("No data remaining after applying population filters")
        
        # Get treatment groups
        if not self.treatments:
            raise ValueError("No treatment variable defined. Use add_treatment() first.")
        
        treatment = self.treatments[0]  # Use first treatment variable
        trt_var = treatment['variable']
        
        # Calculate statistics for each variable
        all_results = []
        
        for var_def in self.variables:
            print(f"  Calculating {var_def['name']}...")
            
            if var_def['type'] == 'continuous':
                results = self.stats_engine.calculate_continuous_stats(
                    data=analysis_data,
                    variable=var_def['name'],
                    treatment_var=trt_var,
                    stats=var_def['stats'],
                    where=var_def.get('where'),
                    decimal_places=var_def['decimal_places']
                )
            elif var_def['type'] == 'categorical':
                results = self.stats_engine.calculate_categorical_stats(
                    data=analysis_data,
                    variable=var_def['name'],
                    treatment_var=trt_var,
                    stats=var_def['stats'],
                    where=var_def.get('where'),
                    values=var_def.get('values'),
                    show_missing=var_def['show_missing']
                )
            
            # Add metadata
            for result in results:
                result.update({
                    'variable_label': var_def['label'],
                    'variable_type': var_def['type'],
                    'indent': var_def['indent']
                })
            
            all_results.extend(results)
        
        # Convert to DataFrame
        report_df = pd.DataFrame(all_results)
        
        print(f"✓ Statistics calculated: {len(report_df)} rows")
        return report_df
    
    def generate(self, output_file: Union[str, Path]) -> bool:
        """
        Generate the clinical report
        
        Args:
            output_file: Output file path (RTF format)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"\n🔧 Generating clinical report: {output_file}")
            
            # Validate report definition
            if not self.title:
                raise ValueError("Report title not defined. Use define_report() first.")
            
            if not self.treatments:
                raise ValueError("No treatment defined. Use add_treatment() first.")
            
            if not self.variables:
                raise ValueError("No variables defined. Use add_variable() or add_categorical() first.")
            
            # Calculate statistics
            self._report_data = self._calculate_statistics()
            
            # Prepare metadata
            self._metadata = {
                'title': self.title,
                'subtitle': self.subtitle,
                'footnotes': self.footnotes,
                'study': self.study,
                'population': self.population,
                'generated_date': datetime.now(),
                'treatment': self.treatments[0],
                'n_subjects': len(self._apply_population_filter())
            }
            
            # Generate RTF output
            success = self.rtf_generator.generate_table(
                data=self._report_data,
                metadata=self._metadata,
                output_file=output_file
            )
            
            if success:
                print(f"✅ Report generated successfully: {output_file}")
                return True
            else:
                print(f"❌ Report generation failed")
                return False
                
        except Exception as e:
            print(f"❌ Error generating report: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def preview(self, n_rows: int = 10) -> pd.DataFrame:
        """
        Preview the report data without generating RTF
        
        Args:
            n_rows: Number of rows to preview
            
        Returns:
            Preview DataFrame
        """
        if self._report_data is None:
            self._report_data = self._calculate_statistics()
        
        return self._report_data.head(n_rows)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary information about the report"""
        analysis_data = self._apply_population_filter()
        
        summary = {
            'title': self.title,
            'population': self.population,
            'n_subjects': len(analysis_data),
            'n_variables': len(self.variables),
            'n_treatments': len(self.treatments),
            'n_groups': len(self.groups),
            'treatment_groups': {}
        }
        
        # Add treatment group counts
        if self.treatments:
            trt_var = self.treatments[0]['variable']
            if trt_var in analysis_data.columns:
                trt_counts = analysis_data[trt_var].value_counts()
                summary['treatment_groups'] = trt_counts.to_dict()
        
        return summary 