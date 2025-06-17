"""
Configuration system for py4csr functional reporting.

This module provides configuration management for statistical reporting,
inspired by the SAS RRG system's configuration-driven approach.
"""

from .report_config import ReportConfig, StatisticConfig
from .clinical_standard import get_clinical_standard_config

__all__ = [
    "ReportConfig",
    "StatisticConfig", 
    "get_clinical_standard_config"
] 