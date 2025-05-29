"""
RTF table generation for py4csr.

This module provides RTF table generation capabilities compatible with r2rtf,
supporting the functional reporting system's output requirements.
"""

from typing import List, Dict, Any, Optional, Union
import pandas as pd
from pathlib import Path
import re


class RTFTable:
    """
    RTF table generator compatible with r2rtf.
    
    This class provides comprehensive RTF table generation with support for
    headers, footers, titles, subtitles, footnotes, and formatted table content.
    """
    
    def __init__(self):
        self.page_header = ""
        self.page_footer = ""
        self.title = ""
        self.subtitle = ""
        self.colheader = []
        self.body = []
        self.footnote = []
        self.source = ""
        self.page_settings = {
            'orientation': 'portrait',
            'margins': {'top': 1.0, 'bottom': 1.0, 'left': 1.0, 'right': 1.0},
            'font_size': 10,
            'font_family': 'Times New Roman'
        }
    
    def rtf_page_header(self, text: str) -> 'RTFTable':
        """Add page header."""
        self.page_header = text
        return self
    
    def rtf_page_footer(self, text: str) -> 'RTFTable':
        """Add page footer."""
        self.page_footer = text
        return self
    
    def rtf_title(self, title: str, subtitle: str = "") -> 'RTFTable':
        """Add title and optional subtitle."""
        self.title = title
        if subtitle:
            self.subtitle = subtitle
        return self
    
    def rtf_subline(self, text: str) -> 'RTFTable':
        """Add subtitle/subline."""
        self.subtitle = text
        return self
    
    def rtf_colheader(self, headers: List[str]) -> 'RTFTable':
        """Add column headers."""
        self.colheader = headers
        return self
    
    def rtf_body(self, data: Union[pd.DataFrame, List[List[str]]]) -> 'RTFTable':
        """Add table body data."""
        if isinstance(data, pd.DataFrame):
            self.body = data.values.tolist()
        else:
            self.body = data
        return self
    
    def rtf_footnote(self, footnotes: Union[str, List[str]]) -> 'RTFTable':
        """Add footnotes."""
        if isinstance(footnotes, str):
            self.footnote = [footnotes]
        else:
            self.footnote = footnotes
        return self
    
    def rtf_source(self, source: str) -> 'RTFTable':
        """Add source line."""
        self.source = source
        return self
    
    def rtf_page(self, **kwargs) -> 'RTFTable':
        """Set page settings."""
        self.page_settings.update(kwargs)
        return self
    
    def rtf_encode(self) -> str:
        """
        Generate RTF content.
        
        Returns
        -------
        str
            Complete RTF document content
        """
        rtf_content = []
        
        # RTF header
        rtf_content.append(r"{\rtf1\ansi\deff0")
        rtf_content.append(r"{\fonttbl{\f0 " + self.page_settings['font_family'] + r";}}")
        
        # Page setup
        if self.page_settings['orientation'] == 'landscape':
            rtf_content.append(r"\landscape")
        
        # Margins (convert inches to twips: 1 inch = 1440 twips)
        margins = self.page_settings['margins']
        rtf_content.append(f"\\margt{int(margins['top'] * 1440)}")
        rtf_content.append(f"\\margb{int(margins['bottom'] * 1440)}")
        rtf_content.append(f"\\margl{int(margins['left'] * 1440)}")
        rtf_content.append(f"\\margr{int(margins['right'] * 1440)}")
        
        # Font size
        font_size = self.page_settings['font_size'] * 2  # RTF uses half-points
        rtf_content.append(f"\\fs{font_size}")
        
        # Page header
        if self.page_header:
            rtf_content.append(r"{\header\pard\qr " + self._escape_rtf(self.page_header) + r"\par}")
        
        # Page footer
        if self.page_footer:
            rtf_content.append(r"{\footer\pard\qc " + self._escape_rtf(self.page_footer) + r"\par}")
        
        # Title
        if self.title:
            rtf_content.append(r"\pard\qc\b\fs" + str(font_size + 4))
            rtf_content.append(self._escape_rtf(self.title))
            rtf_content.append(r"\b0\fs" + str(font_size) + r"\par\par")
        
        # Subtitle
        if self.subtitle:
            rtf_content.append(r"\pard\qc\fs" + str(font_size))
            rtf_content.append(self._escape_rtf(self.subtitle))
            rtf_content.append(r"\par\par")
        
        # Table
        if self.colheader or self.body:
            rtf_content.append(self._generate_table())
        
        # Footnotes
        if self.footnote:
            rtf_content.append(r"\par")
            for i, footnote in enumerate(self.footnote):
                rtf_content.append(r"\pard\ql\fs" + str(font_size - 2))
                rtf_content.append(self._escape_rtf(footnote))
                rtf_content.append(r"\par")
        
        # Source
        if self.source:
            rtf_content.append(r"\par\pard\ql\fs" + str(font_size - 2))
            rtf_content.append(self._escape_rtf(self.source))
            rtf_content.append(r"\par")
        
        # RTF footer
        rtf_content.append("}")
        
        return "".join(rtf_content)
    
    def _generate_table(self) -> str:
        """Generate RTF table content."""
        if not self.colheader and not self.body:
            return ""
        
        table_content = []
        
        # Calculate column widths (simple equal distribution)
        n_cols = len(self.colheader) if self.colheader else len(self.body[0]) if self.body else 0
        if n_cols == 0:
            return ""
        
        col_width = int(6.5 * 1440 / n_cols)  # 6.5 inches total width in twips
        
        # Table definition
        table_content.append(r"\pard")
        
        # Column headers
        if self.colheader:
            # Header row definition
            for i in range(n_cols):
                table_content.append(f"\\cellx{(i + 1) * col_width}")
            
            table_content.append(r"\trowd\trhdr")
            for i in range(n_cols):
                table_content.append(f"\\cellx{(i + 1) * col_width}")
            
            # Header content
            for header in self.colheader:
                table_content.append(r"\pard\intbl\qc\b ")
                table_content.append(self._escape_rtf(str(header)))
                table_content.append(r"\b0\cell")
            
            table_content.append(r"\row")
        
        # Body rows
        if self.body:
            for row in self.body:
                # Row definition
                table_content.append(r"\trowd")
                for i in range(n_cols):
                    table_content.append(f"\\cellx{(i + 1) * col_width}")
                
                # Row content
                for i, cell in enumerate(row):
                    if i < n_cols:
                        table_content.append(r"\pard\intbl\ql ")
                        table_content.append(self._escape_rtf(str(cell)))
                        table_content.append(r"\cell")
                
                table_content.append(r"\row")
        
        table_content.append(r"\pard\par")
        
        return "".join(table_content)
    
    def _escape_rtf(self, text: str) -> str:
        """Escape special RTF characters."""
        if not isinstance(text, str):
            text = str(text)
        
        # Replace special characters
        text = text.replace("\\", "\\\\")
        text = text.replace("{", "\\{")
        text = text.replace("}", "\\}")
        text = text.replace("\n", "\\par ")
        
        return text
    
    def write_rtf(self, filepath: Union[str, Path]) -> None:
        """
        Write RTF content to file.
        
        Parameters
        ----------
        filepath : str or Path
            Output file path
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.rtf_encode())


# Standalone functions for r2rtf compatibility
def rtf_page_header(text: str) -> RTFTable:
    """Create RTF table with page header."""
    return RTFTable().rtf_page_header(text)

def rtf_page_footer(text: str) -> RTFTable:
    """Create RTF table with page footer."""
    return RTFTable().rtf_page_footer(text)

def rtf_title(title: str, subtitle: str = "") -> RTFTable:
    """Create RTF table with title."""
    return RTFTable().rtf_title(title, subtitle)

def rtf_subline(text: str) -> RTFTable:
    """Create RTF table with subtitle."""
    return RTFTable().rtf_subline(text)

def rtf_colheader(headers: List[str]) -> RTFTable:
    """Create RTF table with column headers."""
    return RTFTable().rtf_colheader(headers)

def rtf_body(data: Union[pd.DataFrame, List[List[str]]]) -> RTFTable:
    """Create RTF table with body data."""
    return RTFTable().rtf_body(data)

def rtf_footnote(footnotes: Union[str, List[str]]) -> RTFTable:
    """Create RTF table with footnotes."""
    return RTFTable().rtf_footnote(footnotes)

def rtf_source(source: str) -> RTFTable:
    """Create RTF table with source."""
    return RTFTable().rtf_source(source)

def rtf_page(**kwargs) -> RTFTable:
    """Create RTF table with page settings."""
    return RTFTable().rtf_page(**kwargs)

def rtf_encode(rtf_table: RTFTable) -> str:
    """Encode RTF table to string."""
    return rtf_table.rtf_encode()

def write_rtf(rtf_table: RTFTable, filepath: Union[str, Path]) -> None:
    """Write RTF table to file."""
    rtf_table.write_rtf(filepath) 