"""
ClinicalConfig - Configuration Management for Clinical Reporting

This module manages configuration settings, default statistics,
formatting standards, and clinical conventions.
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path


class ClinicalConfig:
    """
    Clinical Reporting Configuration Manager
    
    Manages default settings, statistical standards, and formatting
    conventions for clinical reporting.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize clinical configuration
        
        Args:
            config_file: Optional configuration file path
        """
        self.config_file = config_file
        self._load_defaults()
        
        if config_file and Path(config_file).exists():
            self._load_config_file(config_file)
    
    def _load_defaults(self):
        """Load default clinical reporting standards"""
        
        # Default statistics for different variable types
        self.default_continuous_stats = ["n", "mean_sd", "median", "min_max"]
        self.default_categorical_stats = ["n_pct"]
        
        # Decimal places by variable type/name
        self.decimal_places = {
            # Common clinical variables
            'age': 1,
            'weight': 1,
            'height': 1,
            'bmi': 1,
            'bsa': 2,
            'creatinine': 2,
            'egfr': 1,
            
            # Lab values
            'hemoglobin': 1,
            'hematocrit': 1,
            'platelets': 0,
            'wbc': 1,
            'neutrophils': 1,
            'lymphocytes': 1,
            
            # Vital signs
            'systolic': 1,
            'diastolic': 1,
            'pulse': 1,
            'temperature': 1,
            
            # Default by data type
            'continuous': 1,
            'percentages': 1,
            'counts': 0
        }
        
        # Statistical test preferences
        self.statistical_tests = {
            'continuous': {
                'two_group': 'ttest',
                'multi_group': 'anova',
                'non_parametric': 'wilcoxon'
            },
            'categorical': {
                'two_group': 'chisq',
                'multi_group': 'chisq',
                'small_counts': 'fisher'
            }
        }
        
        # RTF formatting settings
        self.rtf_settings = {
            'font_family': 'Times New Roman',
            'font_size': 10,
            'title_font_size': 12,
            'header_font_size': 10,
            'page_margins': {
                'top': 1.0,
                'bottom': 1.0,
                'left': 1.0,
                'right': 1.0
            },
            'table_spacing': 0.1,
            'line_spacing': 1.0
        }
        
        # Population definitions
        self.populations = {
            'safety': {
                'label': 'Safety Analysis Population',
                'filter': 'SAFFL == "Y"',
                'description': 'All subjects who received at least one dose of study medication'
            },
            'efficacy': {
                'label': 'Efficacy Analysis Population', 
                'filter': 'EFFFL == "Y"',
                'description': 'All subjects in the safety population with at least one post-baseline efficacy assessment'
            },
            'itt': {
                'label': 'Intent-to-Treat Population',
                'filter': 'ITTFL == "Y"',
                'description': 'All randomized subjects'
            },
            'pp': {
                'label': 'Per-Protocol Population',
                'filter': 'PPROTFL == "Y"',
                'description': 'All subjects who completed the study without major protocol violations'
            }
        }
        
        # Standard footnotes
        self.standard_footnotes = {
            'continuous_stats': [
                'SD = Standard Deviation',
                'Statistical tests: ANOVA for continuous variables'
            ],
            'categorical_stats': [
                'Statistical tests: Chi-square test for categorical variables',
                'Fisher\'s exact test used when expected cell count < 5'
            ],
            'missing_data': [
                'Missing values are not included in the analysis',
                'Percentages are based on non-missing values'
            ]
        }
        
        # Clinical conventions
        self.conventions = {
            'missing_display': 'Missing',
            'total_label': 'Total',
            'pvalue_threshold': 0.05,
            'pvalue_format': '0.001' if 'pvalue < 0.001' else '0.000',
            'percentage_format': '(##.#)',
            'count_format': '###'
        }
    
    def _load_config_file(self, config_file: str):
        """Load configuration from file"""
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            # Update settings with config file values
            for section, values in config_data.items():
                if hasattr(self, section):
                    current_section = getattr(self, section)
                    if isinstance(current_section, dict):
                        current_section.update(values)
                    else:
                        setattr(self, section, values)
            
            print(f"✓ Configuration loaded from: {config_file}")
            
        except Exception as e:
            print(f"⚠ Failed to load config file {config_file}: {e}")
    
    def get_decimal_places(self, variable_name: str, variable_type: str = 'continuous') -> int:
        """
        Get decimal places for a variable
        
        Args:
            variable_name: Variable name
            variable_type: Variable type ('continuous', 'categorical')
            
        Returns:
            Number of decimal places
        """
        # Check specific variable name first
        var_lower = variable_name.lower()
        if var_lower in self.decimal_places:
            return self.decimal_places[var_lower]
        
        # Check for partial matches
        for key, value in self.decimal_places.items():
            if key in var_lower:
                return value
        
        # Default by variable type
        if variable_type in self.decimal_places:
            return self.decimal_places[variable_type]
        
        # Final default
        return 1
    
    def get_statistical_test(self, variable_type: str, n_groups: int, 
                           small_counts: bool = False) -> str:
        """
        Get appropriate statistical test
        
        Args:
            variable_type: 'continuous' or 'categorical'
            n_groups: Number of treatment groups
            small_counts: Whether there are small cell counts
            
        Returns:
            Statistical test name
        """
        if variable_type not in self.statistical_tests:
            return 'none'
        
        tests = self.statistical_tests[variable_type]
        
        if variable_type == 'categorical' and small_counts:
            return tests.get('small_counts', 'fisher')
        elif n_groups == 2:
            return tests.get('two_group', 'ttest')
        else:
            return tests.get('multi_group', 'anova')
    
    def get_population_info(self, population: str) -> Dict[str, str]:
        """
        Get population information
        
        Args:
            population: Population name
            
        Returns:
            Population information dictionary
        """
        return self.populations.get(population, {
            'label': f'{population.title()} Population',
            'filter': None,
            'description': f'{population.title()} analysis population'
        })
    
    def get_standard_footnotes(self, footnote_type: str) -> List[str]:
        """
        Get standard footnotes by type
        
        Args:
            footnote_type: Type of footnotes
            
        Returns:
            List of footnote strings
        """
        return self.standard_footnotes.get(footnote_type, [])
    
    def format_statistic(self, value: float, stat_type: str, 
                        decimal_places: int = None) -> str:
        """
        Format a statistical value according to conventions
        
        Args:
            value: Statistical value
            stat_type: Type of statistic ('mean', 'sd', 'pct', etc.)
            decimal_places: Number of decimal places
            
        Returns:
            Formatted string
        """
        if pd.isna(value):
            return ""
        
        if decimal_places is None:
            decimal_places = self.decimal_places.get(stat_type, 1)
        
        if stat_type in ['count', 'n']:
            return f"{int(value)}"
        elif stat_type in ['pct', 'percentage']:
            return f"({value:.{decimal_places}f})"
        else:
            return f"{value:.{decimal_places}f}"
    
    def save_config(self, output_file: str):
        """
        Save current configuration to file
        
        Args:
            output_file: Output file path
        """
        config_data = {
            'default_continuous_stats': self.default_continuous_stats,
            'default_categorical_stats': self.default_categorical_stats,
            'decimal_places': self.decimal_places,
            'statistical_tests': self.statistical_tests,
            'rtf_settings': self.rtf_settings,
            'populations': self.populations,
            'standard_footnotes': self.standard_footnotes,
            'conventions': self.conventions
        }
        
        try:
            with open(output_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            print(f"✓ Configuration saved to: {output_file}")
        except Exception as e:
            print(f"❌ Failed to save configuration: {e}")
    
    def update_setting(self, section: str, key: str, value: Any):
        """
        Update a configuration setting
        
        Args:
            section: Configuration section
            key: Setting key
            value: New value
        """
        if hasattr(self, section):
            section_obj = getattr(self, section)
            if isinstance(section_obj, dict):
                section_obj[key] = value
                print(f"✓ Updated {section}.{key} = {value}")
            else:
                print(f"⚠ Section {section} is not a dictionary")
        else:
            print(f"⚠ Section {section} not found")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get configuration summary"""
        return {
            'config_file': self.config_file,
            'continuous_stats': self.default_continuous_stats,
            'categorical_stats': self.default_categorical_stats,
            'n_decimal_rules': len(self.decimal_places),
            'n_populations': len(self.populations),
            'rtf_font': self.rtf_settings['font_family'],
            'rtf_font_size': self.rtf_settings['font_size']
        } 