"""
Configuration system for py4csr functional reporting.

This module provides configuration management for statistical reporting,
inspired by the SAS RRG system's configuration-driven approach.
"""

from .clinical_standard import get_clinical_standard_config
from .report_config import ReportConfig, StatisticConfig

__all__ = ["ReportConfig", "StatisticConfig", "get_clinical_standard_config"]
