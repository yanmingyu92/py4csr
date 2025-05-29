"""
Report templates for clinical study reports.

This module provides template functions for common
clinical study report formats and layouts.
"""

from typing import Dict, Any, Optional
import json


def get_template(template_name: str) -> Dict[str, Any]:
    """
    Get a predefined report template.
    
    Parameters
    ----------
    template_name : str
        Name of the template
        
    Returns
    -------
    dict
        Template configuration
    """
    
    templates = {
        'demographics': {
            'title': 'Baseline Characteristics',
            'subtitle': '(All Participants Randomized)',
            'footnote': 'Values are presented as mean (SD) for continuous variables and n (%) for categorical variables.',
            'columns': ['Variable', 'Category', 'Treatment A', 'Treatment B', 'P-value'],
            'col_widths': [2.5, 1.5, 1.5, 1.5, 1.0],
            'justification': ['l', 'l', 'c', 'c', 'c']
        },
        
        'adverse_events': {
            'title': 'Adverse Events Summary',
            'subtitle': '(Safety Population)',
            'footnote': 'Percentages are based on the number of subjects in each treatment group.',
            'columns': ['Adverse Event', 'Placebo', 'Treatment A', 'Treatment B'],
            'col_widths': [3.0, 2.0, 2.0, 2.0],
            'justification': ['l', 'c', 'c', 'c']
        },
        
        'efficacy': {
            'title': 'Efficacy Analysis',
            'subtitle': '(Efficacy Population)',
            'footnote': 'Analysis based on ANCOVA model with baseline as covariate.',
            'columns': ['Parameter', 'Estimate', 'CI Lower', 'CI Upper', 'P-value'],
            'col_widths': [2.0, 1.5, 1.5, 1.5, 1.5],
            'justification': ['l', 'c', 'c', 'c', 'c']
        }
    }
    
    return templates.get(template_name, {})


def load_template(filepath: str) -> Dict[str, Any]:
    """
    Load a template from a JSON file.
    
    Parameters
    ----------
    filepath : str
        Path to the template file
        
    Returns
    -------
    dict
        Template configuration
    """
    
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading template: {e}")
        return {}


def save_template(template: Dict[str, Any], filepath: str) -> None:
    """
    Save a template to a JSON file.
    
    Parameters
    ----------
    template : dict
        Template configuration
    filepath : str
        Output file path
    """
    
    try:
        with open(filepath, 'w') as f:
            json.dump(template, f, indent=2)
    except Exception as e:
        print(f"Error saving template: {e}")


class BaseTemplate:
    """
    Base template for clinical reports.
    """
    
    def __init__(self, title: str = "", subtitle: str = ""):
        """
        Initialize base template.
        
        Parameters
        ----------
        title : str, default ""
            Report title
        subtitle : str, default ""
            Report subtitle
        """
        self.title = title
        self.subtitle = subtitle
        self.headers = []
        self.footers = []
    
    def add_header(self, text: str):
        """Add header text."""
        self.headers.append(text)
    
    def add_footer(self, text: str):
        """Add footer text."""
        self.footers.append(text)


class AETemplate(BaseTemplate):
    """
    Template for adverse events reports.
    """
    
    def __init__(self):
        super().__init__(title="Adverse Events Analysis", subtitle="Safety Analysis Population")
        self.add_footer("Every subject is counted a single time for each applicable row and column.")


class EfficacyTemplate(BaseTemplate):
    """
    Template for efficacy analysis reports.
    """
    
    def __init__(self):
        super().__init__(title="Efficacy Analysis", subtitle="ANCOVA Model Results")
        self.add_footer("Analysis based on change from baseline using ANCOVA model.") 