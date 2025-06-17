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
try:
    from . import data
except ImportError:
    data = None

try:
    from . import analysis
except ImportError:
    analysis = None

try:
    from . import plotting
except ImportError:
    plotting = None

try:
    from . import reporting
except ImportError:
    reporting = None

try:
    from . import config
except ImportError:
    config = None

try:
    from . import tables
except ImportError:
    tables = None

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
    'config',
    'tables',
    
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
