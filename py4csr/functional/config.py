"""
Functional Configuration System for py4csr

This module provides configuration management for the functional reporting system,
mirroring the SAS RRG configuration approach with centralized definitions for
statistics, formats, and report templates.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Union
import yaml
from pathlib import Path


@dataclass
class StatisticDefinition:
    """Definition of a statistical calculation (equivalent to SAS RRG stat definitions)."""
    name: str
    display_name: str
    description: str
    precision: int = 1
    format_function: Optional[str] = None
    applicable_types: List[str] = field(default_factory=lambda: ['continuous'])
    
    
@dataclass
class FormatDefinition:
    """Definition of a display format (equivalent to SAS RRG format definitions)."""
    name: str
    pattern: str
    description: str
    example: str = ""


@dataclass
class TableTemplate:
    """Template definition for table types (equivalent to SAS RRG templates)."""
    name: str
    title_template: str
    subtitle_template: str
    default_variables: List[str] = field(default_factory=list)
    default_statistics: List[str] = field(default_factory=list)
    default_population: str = "safety"
    footnotes: List[str] = field(default_factory=list)
    special_processing: Optional[str] = None


@dataclass
class FunctionalConfig:
    """
    Main configuration class for functional reporting system.
    
    This class centralizes all configuration similar to the SAS RRG __rrgconfig
    dataset, providing definitions for statistics, formats, and templates.
    """
    
    # Statistical definitions
    statistics: Dict[str, StatisticDefinition] = field(default_factory=dict)
    
    # Format definitions  
    formats: Dict[str, FormatDefinition] = field(default_factory=dict)
    
    # Table templates
    templates: Dict[str, TableTemplate] = field(default_factory=dict)
    
    # Output settings
    output_formats: List[str] = field(default_factory=lambda: ['rtf', 'pdf'])
    
    # Page settings
    page_orientation: str = "portrait"
    page_margins: Dict[str, float] = field(default_factory=lambda: {
        'top': 1.0, 'bottom': 1.0, 'left': 1.0, 'right': 1.0
    })
    font_family: str = "Times New Roman"
    font_size: int = 10
    
    # Clinical trial specific settings
    regulatory_compliance: str = "ICH-E3"
    decimal_precision: Dict[str, int] = field(default_factory=lambda: {
        'default': 1, 'age': 0, 'weight': 1, 'height': 1, 'bmi': 1
    })
    
    @classmethod
    def clinical_standard(cls) -> 'FunctionalConfig':
        """
        Create standard clinical trial configuration.
        
        This provides the equivalent of SAS RRG's standard clinical configuration
        with predefined statistics, formats, and templates.
        
        Returns
        -------
        FunctionalConfig
            Standard clinical configuration
        """
        config = cls()
        
        # Define standard statistics (equivalent to SAS RRG [A1] section)
        config.statistics = {
            'n': StatisticDefinition(
                name='n',
                display_name='n',
                description='Number of subjects',
                precision=0,
                applicable_types=['continuous', 'categorical']
            ),
            'mean': StatisticDefinition(
                name='mean',
                display_name='Mean',
                description='Arithmetic mean',
                precision=1,
                applicable_types=['continuous']
            ),
            'std': StatisticDefinition(
                name='std',
                display_name='SD',
                description='Standard deviation',
                precision=2,
                applicable_types=['continuous']
            ),
            'mean_sd': StatisticDefinition(
                name='mean_sd',
                display_name='Mean (SD)',
                description='Mean with standard deviation',
                precision=1,
                format_function='format_mean_sd',
                applicable_types=['continuous']
            ),
            'median': StatisticDefinition(
                name='median',
                display_name='Median',
                description='Median value',
                precision=1,
                applicable_types=['continuous']
            ),
            'q1_q3': StatisticDefinition(
                name='q1_q3',
                display_name='Q1, Q3',
                description='First and third quartiles',
                precision=1,
                format_function='format_quartiles',
                applicable_types=['continuous']
            ),
            'min_max': StatisticDefinition(
                name='min_max',
                display_name='Min, Max',
                description='Minimum and maximum values',
                precision=1,
                format_function='format_min_max',
                applicable_types=['continuous']
            ),
            'percent': StatisticDefinition(
                name='percent',
                display_name='%',
                description='Percentage',
                precision=1,
                applicable_types=['categorical']
            ),
            'n_percent': StatisticDefinition(
                name='n_percent',
                display_name='n (%)',
                description='Count with percentage',
                precision=1,
                format_function='format_n_percent',
                applicable_types=['categorical']
            )
        }
        
        # Define standard formats (equivalent to SAS RRG [A2] section)
        config.formats = {
            'decimal_1': FormatDefinition(
                name='decimal_1',
                pattern='{:.1f}',
                description='One decimal place',
                example='12.3'
            ),
            'decimal_2': FormatDefinition(
                name='decimal_2', 
                pattern='{:.2f}',
                description='Two decimal places',
                example='12.34'
            ),
            'integer': FormatDefinition(
                name='integer',
                pattern='{:.0f}',
                description='Integer format',
                example='12'
            ),
            'percent_1': FormatDefinition(
                name='percent_1',
                pattern='({:.1f}%)',
                description='Percentage with one decimal',
                example='(12.3%)'
            ),
            'pvalue': FormatDefinition(
                name='pvalue',
                pattern='{:.4f}',
                description='P-value format',
                example='0.0123'
            ),
            'pvalue_threshold': FormatDefinition(
                name='pvalue_threshold',
                pattern='<0.0001',
                description='P-value with threshold',
                example='<0.0001'
            )
        }
        
        # Define standard table templates (equivalent to SAS RRG templates)
        config.templates = {
            'demographics': TableTemplate(
                name='demographics',
                title_template='Baseline Demographics and Clinical Characteristics',
                subtitle_template='{study_title} - {population_label}',
                default_variables=['AGE', 'AGEGR1', 'SEX', 'RACE', 'WEIGHT', 'HEIGHT', 'BMI'],
                default_statistics=['n', 'mean_sd', 'median', 'min_max', 'n_percent'],
                footnotes=[
                    'Continuous variables: n, mean (SD), median, min, max',
                    'Categorical variables: n (%)'
                ]
            ),
            'disposition': TableTemplate(
                name='disposition',
                title_template='Subject Disposition',
                subtitle_template='{study_title} - All Randomized Subjects',
                default_variables=['DCSREAS'],
                default_statistics=['n_percent'],
                footnotes=[
                    'Percentages based on number of randomized subjects'
                ]
            ),
            'ae_summary': TableTemplate(
                name='ae_summary',
                title_template='Summary of Adverse Events',
                subtitle_template='{study_title} - {population_label}',
                default_statistics=['n_percent'],
                footnotes=[
                    'Subjects are counted once per category',
                    'Percentages based on number of subjects in treatment group'
                ]
            ),
            'ae_detail': TableTemplate(
                name='ae_detail',
                title_template='Adverse Events by System Organ Class and Preferred Term',
                subtitle_template='{study_title} - {population_label}',
                default_statistics=['n_percent'],
                footnotes=[
                    'Subjects are counted once per preferred term',
                    'System organ classes ordered by decreasing frequency in total column'
                ]
            ),
            'laboratory': TableTemplate(
                name='laboratory',
                title_template='Laboratory Parameters - Descriptive Statistics',
                subtitle_template='{study_title} - {population_label}',
                default_statistics=['n', 'mean_sd', 'median', 'min_max'],
                footnotes=[
                    'Statistics based on change from baseline values',
                    'n = number of subjects with non-missing values'
                ]
            ),
            'efficacy': TableTemplate(
                name='efficacy',
                title_template='Efficacy Analysis',
                subtitle_template='{study_title} - {population_label}',
                default_statistics=['n', 'mean_sd', 'median'],
                default_population='efficacy',
                footnotes=[
                    'Analysis based on efficacy analysis population'
                ]
            )
        }
        
        return config
    
    @classmethod
    def from_yaml(cls, config_path: Union[str, Path]) -> 'FunctionalConfig':
        """
        Load configuration from YAML file.
        
        Parameters
        ----------
        config_path : str or Path
            Path to YAML configuration file
            
        Returns
        -------
        FunctionalConfig
            Configuration loaded from file
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Convert dictionaries to dataclass objects
        config = cls()
        
        if 'statistics' in config_data:
            for name, stat_data in config_data['statistics'].items():
                config.statistics[name] = StatisticDefinition(name=name, **stat_data)
        
        if 'formats' in config_data:
            for name, fmt_data in config_data['formats'].items():
                config.formats[name] = FormatDefinition(name=name, **fmt_data)
        
        if 'templates' in config_data:
            for name, tmpl_data in config_data['templates'].items():
                config.templates[name] = TableTemplate(name=name, **tmpl_data)
        
        # Update other settings
        for key, value in config_data.items():
            if key not in ['statistics', 'formats', 'templates'] and hasattr(config, key):
                setattr(config, key, value)
        
        return config
    
    def to_yaml(self, output_path: Union[str, Path]) -> None:
        """
        Save configuration to YAML file.
        
        Parameters
        ----------
        output_path : str or Path
            Path for output YAML file
        """
        output_path = Path(output_path)
        
        # Convert dataclass objects to dictionaries
        config_data = {
            'statistics': {
                name: {
                    'display_name': stat.display_name,
                    'description': stat.description,
                    'precision': stat.precision,
                    'format_function': stat.format_function,
                    'applicable_types': stat.applicable_types
                }
                for name, stat in self.statistics.items()
            },
            'formats': {
                name: {
                    'pattern': fmt.pattern,
                    'description': fmt.description,
                    'example': fmt.example
                }
                for name, fmt in self.formats.items()
            },
            'templates': {
                name: {
                    'title_template': tmpl.title_template,
                    'subtitle_template': tmpl.subtitle_template,
                    'default_variables': tmpl.default_variables,
                    'default_statistics': tmpl.default_statistics,
                    'default_population': tmpl.default_population,
                    'footnotes': tmpl.footnotes,
                    'special_processing': tmpl.special_processing
                }
                for name, tmpl in self.templates.items()
            },
            'output_formats': self.output_formats,
            'page_orientation': self.page_orientation,
            'page_margins': self.page_margins,
            'font_family': self.font_family,
            'font_size': self.font_size,
            'regulatory_compliance': self.regulatory_compliance,
            'decimal_precision': self.decimal_precision
        }
        
        with open(output_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, indent=2)
    
    def get_statistic(self, name: str) -> Optional[StatisticDefinition]:
        """Get statistic definition by name."""
        return self.statistics.get(name)
    
    def get_format(self, name: str) -> Optional[FormatDefinition]:
        """Get format definition by name."""
        return self.formats.get(name)
    
    def get_template(self, name: str) -> Optional[TableTemplate]:
        """Get table template by name."""
        return self.templates.get(name)
    
    def get_applicable_statistics(self, var_type: str) -> List[str]:
        """Get list of statistics applicable to a variable type."""
        return [
            name for name, stat in self.statistics.items()
            if var_type in stat.applicable_types
        ]
    
    def validate(self) -> List[str]:
        """
        Validate configuration and return list of issues.
        
        Returns
        -------
        list
            List of validation issues (empty if valid)
        """
        issues = []
        
        # Check that all format functions referenced in statistics exist
        for stat_name, stat in self.statistics.items():
            if stat.format_function and stat.format_function not in self.formats:
                issues.append(f"Statistic '{stat_name}' references unknown format '{stat.format_function}'")
        
        # Check that all templates reference valid statistics
        for tmpl_name, tmpl in self.templates.items():
            for stat_name in tmpl.default_statistics:
                if stat_name not in self.statistics:
                    issues.append(f"Template '{tmpl_name}' references unknown statistic '{stat_name}'")
        
        return issues 