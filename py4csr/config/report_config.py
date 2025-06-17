"""
Core configuration classes for py4csr functional reporting system.

This module defines the configuration structure for statistical reporting,
following the SAS RRG system's configuration-driven approach.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
import yaml
from pathlib import Path


@dataclass
class StatisticConfig:
    """Configuration for statistical displays"""
    name: str
    display: str
    label: str
    precision: int
    format_func: Optional[str] = None
    
    def format_value(self, value: Any) -> str:
        """Format a value according to this statistic's configuration"""
        if self.format_func:
            # Would implement custom formatting functions
            return str(value)
        
        if isinstance(value, (int, float)):
            return f"{value:.{self.precision}f}"
        return str(value)


@dataclass
class PageSettings:
    """Page layout settings"""
    orientation: str = "portrait"
    margins: Dict[str, float] = field(default_factory=lambda: {
        "top": 1.0, "bottom": 1.0, "left": 1.0, "right": 1.0
    })
    font_size: int = 10
    font_family: str = "Times New Roman"
    col_width: float = 6.5


@dataclass
class ReportConfig:
    """Master configuration for report generation"""
    
    # Statistical definitions
    statistics: Dict[str, StatisticConfig] = field(default_factory=dict)
    
    # Format definitions
    formats: Dict[str, str] = field(default_factory=dict)
    
    # Layout settings
    page_settings: PageSettings = field(default_factory=PageSettings)
    
    # Template mappings
    templates: Dict[str, str] = field(default_factory=dict)
    
    # Population definitions
    populations: Dict[str, str] = field(default_factory=dict)
    
    # Treatment definitions
    treatments: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def clinical_standard(cls) -> 'ReportConfig':
        """Load standard clinical trial configuration"""
        from .clinical_standard import get_clinical_standard_config
        return get_clinical_standard_config()
    
    @classmethod
    def from_yaml(cls, config_path: str) -> 'ReportConfig':
        """Load configuration from YAML file"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)
        
        return cls._from_dict(config_data)
    
    @classmethod
    def _from_dict(cls, config_data: Dict[str, Any]) -> 'ReportConfig':
        """Create ReportConfig from dictionary"""
        
        # Parse statistics
        statistics = {}
        if 'statistics' in config_data:
            for name, stat_config in config_data['statistics'].items():
                statistics[name] = StatisticConfig(
                    name=name,
                    **stat_config
                )
        
        # Parse page settings
        page_settings = PageSettings()
        if 'page_settings' in config_data:
            page_data = config_data['page_settings']
            page_settings = PageSettings(
                orientation=page_data.get('orientation', 'portrait'),
                margins=page_data.get('margins', page_settings.margins),
                font_size=page_data.get('font_size', 10),
                font_family=page_data.get('font_family', 'Times New Roman'),
                col_width=page_data.get('col_width', 6.5)
            )
        
        return cls(
            statistics=statistics,
            formats=config_data.get('formats', {}),
            page_settings=page_settings,
            templates=config_data.get('templates', {}),
            populations=config_data.get('populations', {}),
            treatments=config_data.get('treatments', {})
        )
    
    def get_statistic(self, name: str) -> Optional[StatisticConfig]:
        """Get statistic configuration by name"""
        return self.statistics.get(name)
    
    def get_format(self, name: str) -> Optional[str]:
        """Get format string by name"""
        return self.formats.get(name)
    
    def add_statistic(self, stat_config: StatisticConfig) -> None:
        """Add a statistic configuration"""
        self.statistics[stat_config.name] = stat_config
    
    def add_format(self, name: str, format_str: str) -> None:
        """Add a format definition"""
        self.formats[name] = format_str
    
    def to_yaml(self, output_path: str) -> None:
        """Save configuration to YAML file"""
        config_dict = {
            'statistics': {
                name: {
                    'display': stat.display,
                    'label': stat.label,
                    'precision': stat.precision,
                    'format_func': stat.format_func
                }
                for name, stat in self.statistics.items()
            },
            'formats': self.formats,
            'page_settings': {
                'orientation': self.page_settings.orientation,
                'margins': self.page_settings.margins,
                'font_size': self.page_settings.font_size,
                'font_family': self.page_settings.font_family,
                'col_width': self.page_settings.col_width
            },
            'templates': self.templates,
            'populations': self.populations,
            'treatments': self.treatments
        }
        
        with open(output_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2) 