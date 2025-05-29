"""
Clinical data analysis and reporting for py4csr.

This module provides tools for clinical data analysis and report generation.
"""

from .clinical_config import ClinicalConfig
from .session import ClinicalSession
from .statistical_engine import ClinicalStatisticalEngine

# Only import ClinicalReport if its dependencies exist
try:
    from .clinical_report import ClinicalReport
    _has_clinical_report = True
except ImportError:
    _has_clinical_report = False

__all__ = [
    'ClinicalConfig',
    'ClinicalSession', 
    'ClinicalStatisticalEngine'
]

if _has_clinical_report:
    __all__.append('ClinicalReport')

__version__ = "2.0.0"
__author__ = "py4csr Development Team"
__description__ = "RRG-Inspired Clinical Reporting System" 