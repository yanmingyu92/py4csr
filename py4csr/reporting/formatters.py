"""
Formatting utilities for RTF tables and reports.

This module provides formatting classes and functions
for consistent styling of clinical study reports.
"""

from typing import Dict, List, Optional, Any


class RTFFormatter:
    """RTF formatting utilities."""
    
    @staticmethod
    def format_title(text: str, size: int = 24) -> str:
        """Format title text for RTF."""
        return f"\\qc\\b\\fs{size} {text}\\b0\\par"
    
    @staticmethod
    def format_subtitle(text: str, size: int = 20) -> str:
        """Format subtitle text for RTF."""
        return f"\\qc\\fs{size} {text}\\par"
    
    @staticmethod
    def format_footnote(text: str, size: int = 16) -> str:
        """Format footnote text for RTF."""
        return f"\\fs{size} {text}\\par"


class TableFormatter:
    """Table formatting utilities."""
    
    @staticmethod
    def format_percentage(value: float, decimals: int = 1) -> str:
        """Format percentage value."""
        return f"{value:.{decimals}f}%"
    
    @staticmethod
    def format_count_percentage(count: int, total: int, decimals: int = 1) -> str:
        """Format count with percentage."""
        pct = (count / total * 100) if total > 0 else 0
        return f"{count} ({pct:.{decimals}f}%)"
    
    @staticmethod
    def format_mean_sd(mean: float, sd: float, decimals: int = 2) -> str:
        """Format mean with standard deviation."""
        return f"{mean:.{decimals}f} ({sd:.{decimals}f})"


def format_rtf_text(text: str, bold: bool = False, italic: bool = False) -> str:
    """
    Format text for RTF output.
    
    Parameters
    ----------
    text : str
        Text to format
    bold : bool, default False
        Whether to make text bold
    italic : bool, default False
        Whether to make text italic
        
    Returns
    -------
    str
        RTF formatted text
    """
    formatted_text = str(text)
    
    if bold:
        formatted_text = f"\\b {formatted_text}\\b0"
    
    if italic:
        formatted_text = f"\\i {formatted_text}\\i0"
    
    return formatted_text


def create_rtf_header(title: str = "") -> str:
    """
    Create RTF document header.
    
    Parameters
    ----------
    title : str, default ""
        Document title
        
    Returns
    -------
    str
        RTF header string
    """
    header = "{\\rtf1\\ansi\\deff0"
    
    if title:
        header += f"\\title {title}"
    
    header += "}"
    
    return header


def create_rtf_footer() -> str:
    """
    Create RTF document footer.
    
    Returns
    -------
    str
        RTF footer string
    """
    return "}" 