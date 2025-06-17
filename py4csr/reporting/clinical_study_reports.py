"""
Clinical Study Reports class for py4csr.

This module provides the legacy ClinicalStudyReports class for backward compatibility.
"""

import pandas as pd
from typing import Dict, List, Optional, Any


class ClinicalStudyReports:
    """
    Legacy clinical study reports class.
    
    This class is maintained for backward compatibility.
    New code should use the functional ReportBuilder approach.
    """
    
    def __init__(self, data: Dict[str, pd.DataFrame]):
        """
        Initialize with datasets.
        
        Parameters
        ----------
        data : dict
            Dictionary of datasets
        """
        self.data = data
        self.reports = {}
    
    def generate_demographics_table(self, **kwargs) -> pd.DataFrame:
        """Generate demographics table (legacy method)."""
        # Placeholder implementation
        return pd.DataFrame({
            'Variable': ['Age', 'Sex', 'Race'],
            'Statistic': ['Mean (SD)', 'n (%)', 'n (%)'],
            'Treatment A': ['65.2 (12.1)', '25 (50%)', '40 (80%)'],
            'Treatment B': ['64.8 (11.8)', '23 (46%)', '38 (76%)']
        })
    
    def generate_ae_summary_table(self, **kwargs) -> pd.DataFrame:
        """Generate AE summary table (legacy method)."""
        # Placeholder implementation
        return pd.DataFrame({
            'AE Category': ['Any AE', 'Serious AE', 'Drug-related AE'],
            'Treatment A': ['30 (60%)', '5 (10%)', '15 (30%)'],
            'Treatment B': ['28 (56%)', '4 (8%)', '12 (24%)']
        })
    
    def write_rtf(self, filepath: str) -> None:
        """Write reports to RTF file (legacy method)."""
        # Placeholder implementation
        with open(filepath, 'w') as f:
            f.write(r"{\rtf1\ansi Legacy CSR Report \par}") 