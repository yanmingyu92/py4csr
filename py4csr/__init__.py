"""
py4csr: Python for Clinical Study Reporting

Professional clinical trial data analysis and reporting package for pharmaceutical
and biotech companies, providing equivalent functionality to established clinical
reporting systems for regulatory submissions.

Author: py4csr Contributors
License: MIT
"""

__version__ = "0.1.0"
__author__ = "py4csr Contributors"
__email__ = "info@py4csr.com"

# Clinical reporting system
try:
    from .clinical import ClinicalSession
except ImportError:
    ClinicalSession = None

# Functional reporting system 
try:
    from .functional import ReportSession, FunctionalConfig
except ImportError:
    ReportSession = None
    FunctionalConfig = None

# Core modules
from . import (
    data,
    analysis, 
    plotting,
    reporting,
    validation,
    config,
    tables,
    templates,
    cli
)

__all__ = [
    # Main session classes
    'ClinicalSession',
    'ReportSession', 
    'FunctionalConfig',
    
    # Core modules
    'data',
    'analysis',
    'plotting', 
    'reporting',
    'validation',
    'config',
    'tables',
    'templates',
    'cli',
    
    # Metadata
    '__version__',
    '__author__',
    '__email__'
]

# Package metadata
__title__ = "py4csr"
__description__ = "Python for Clinical Study Reports and Submission"
__url__ = "https://github.com/py4csr/py4csr"
__license__ = "MIT" 
