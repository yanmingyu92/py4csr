"""
Professional RTF Formatter for Clinical Tables and Listings
Generates publication-quality RTF tables and listings with proper formatting

This module provides RTF formatting capabilities that match clinical reporting standards
including proper borders, fonts, footnotes, centered content, and listing formats.
"""

import pandas as pd
from typing import List, Dict, Optional, Any
from pathlib import Path
import re


class ClinicalRTFFormatter:
    """Professional RTF formatter for clinical tables and listings"""
    
    def __init__(self):
        self.font_size = 18  # RTF font size (9pt * 2)
        self.header_font_size = 20  # RTF font size (10pt * 2)
        self.title_font_size = 24  # RTF font size (12pt * 2)
        
        # RTF color table
        self.color_table = r"""{\colortbl;\red0\green0\blue0;\red255\green255\blue255;}"""
        
        # RTF font table with proper encoding
        self.font_table = r"""{\fonttbl{\f0\froman\fcharset0 Times New Roman;}{\f1\fswiss\fcharset0 Arial;}}"""
    
    def _escape_rtf_text(self, text: str) -> str:
        """Escape special RTF characters and handle encoding"""
        if pd.isna(text):
            return ""
        
        text = str(text)
        
        # Handle special characters that cause garbled output
        text = text.replace('\\', '\\\\')
        text = text.replace('{', '\\{')
        text = text.replace('}', '\\}')
        text = text.replace('\n', '\\line ')
        text = text.replace('\r', '')
        
        # Handle non-ASCII characters
        result = ""
        for char in text:
            if ord(char) > 127:
                # Convert to RTF unicode escape
                result += f"\\u{ord(char)}?"
            else:
                result += char
        
        return result
    
    def _create_rtf_header(self, title: str = "", subtitle: str = "") -> str:
        """Create RTF document header with proper encoding"""
        header = r"""{\rtf1\ansi\deff0 """ + self.font_table + self.color_table + r"""
\paperw12240\paperh15840\margl1440\margr1440\margt1440\margb1440
\sectd\pgwsxn12240\pghsxn15840\marglsxn1440\margrsxn1440\margtsxn1440\margbsxn1440
"""
        
        if title:
            # Center-aligned title
            header += r"""{\pard\qc\f0\fs""" + str(self.title_font_size) + r"""\b """ + self._escape_rtf_text(title) + r"""\par}"""
        
        if subtitle:
            # Center-aligned subtitle with line breaks
            subtitle_lines = subtitle.split('\n')
            for line in subtitle_lines:
                header += r"""{\pard\qc\f0\fs""" + str(self.header_font_size) + r""" """ + self._escape_rtf_text(line) + r"""\par}"""
        
        header += r"""{\pard\par}"""  # Empty line
        
        return header
    
    def _create_table_header(self, columns: List[str], col_widths: List[int]) -> str:
        """Create RTF table header with borders and center alignment"""
        # Start table row with center alignment
        header = r"""{\trowd\trgaph108\trleft-108\trqc"""
        
        # Add cell borders and widths
        current_pos = 0
        for i, width in enumerate(col_widths):
            current_pos += width
            # Add cell borders: top, left, bottom, right
            header += r"""\clbrdrt\brdrs\brdrw15\clbrdrl\brdrs\brdrw15\clbrdrb\brdrs\brdrw15\clbrdrr\brdrs\brdrw15"""
            header += r"""\cellx""" + str(current_pos)
        
        # Add header content with center alignment
        header += r"""\pard\intbl\qc\f0\fs""" + str(self.header_font_size) + r"""\b """
        
        for i, col in enumerate(columns):
            if i > 0:
                header += r"""\cell """
            header += self._escape_rtf_text(col)
        
        header += r"""\cell\row}"""
        
        return header
    
    def _create_table_row(self, row_data: List[str], col_widths: List[int], is_data_row: bool = True) -> str:
        """Create RTF table row with center alignment"""
        # Start table row with center alignment
        row = r"""{\trowd\trgaph108\trleft-108\trqc"""
        
        # Add cell borders and widths
        current_pos = 0
        for i, width in enumerate(col_widths):
            current_pos += width
            # Lighter borders for data rows
            border_weight = "10" if is_data_row else "15"
            row += r"""\clbrdrt\brdrs\brdrw""" + border_weight
            row += r"""\clbrdrl\brdrs\brdrw""" + border_weight
            row += r"""\clbrdrb\brdrs\brdrw""" + border_weight
            row += r"""\clbrdrr\brdrs\brdrw""" + border_weight
            row += r"""\cellx""" + str(current_pos)
        
        # Add row content with center alignment
        font_weight = "" if is_data_row else r"""\b """
        row += r"""\pard\intbl\qc\f0\fs""" + str(self.font_size) + font_weight
        
        for i, cell in enumerate(row_data):
            if i > 0:
                row += r"""\cell """
            row += self._escape_rtf_text(cell)
        
        row += r"""\cell\row}"""
        
        return row
    
    def _create_footnotes(self, footnotes: List[str]) -> str:
        """Create RTF footnotes section"""
        if not footnotes:
            return ""
        
        footnote_section = r"""{\pard\par}"""  # Empty line
        footnote_section += r"""{\pard\f0\fs""" + str(self.font_size - 2) + r""" """
        
        for i, footnote in enumerate(footnotes):
            if i > 0:
                footnote_section += r"""\par """
            
            # Add superscript footnote marker
            marker = chr(ord('a') + i) if i < 26 else str(i + 1)
            footnote_section += r"""{\super """ + marker + r"""} """ + self._escape_rtf_text(footnote)
        
        footnote_section += r"""\par}"""
        
        return footnote_section
    
    def _calculate_column_widths(self, df: pd.DataFrame, base_width: int = 1440) -> List[int]:
        """Calculate optimal column widths based on content"""
        col_widths = []
        
        for col in df.columns:
            # Calculate max content length in column
            max_len = max(
                len(str(col)),  # Header length
                df[col].astype(str).str.len().max() if len(df) > 0 else 0  # Data length
            )
            
            # Convert to RTF units (twips) with better scaling
            width = max(base_width, int(max_len * 100))  # 100 twips per character
            col_widths.append(width)
        
        return col_widths
    
    def format_table_to_rtf(self, 
                           df: pd.DataFrame,
                           title: str = "",
                           subtitle: str = "",
                           footnotes: List[str] = None,
                           output_file: Optional[str] = None) -> str:
        """
        Format pandas DataFrame to professional RTF table
        
        Parameters
        ----------
        df : pd.DataFrame
            Data to format
        title : str
            Table title
        subtitle : str
            Table subtitle
        footnotes : List[str]
            List of footnotes
        output_file : str, optional
            Output file path
            
        Returns
        -------
        str
            RTF formatted string
        """
        if footnotes is None:
            footnotes = []
        
        # Calculate column widths
        col_widths = self._calculate_column_widths(df)
        
        # Build RTF document
        rtf_content = self._create_rtf_header(title, subtitle)
        
        # Add table header
        rtf_content += self._create_table_header(df.columns.tolist(), col_widths)
        
        # Add data rows
        for _, row in df.iterrows():
            row_data = [str(val) if not pd.isna(val) else "" for val in row]
            rtf_content += self._create_table_row(row_data, col_widths, is_data_row=True)
        
        # Add footnotes
        rtf_content += self._create_footnotes(footnotes)
        
        # Close RTF document
        rtf_content += r"""}"""
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(rtf_content)
        
        return rtf_content
    
    def format_listing_to_rtf(self,
                             df: pd.DataFrame,
                             title: str = "",
                             subtitle: str = "",
                             footnotes: List[str] = None,
                             output_file: Optional[str] = None) -> str:
        """
        Format pandas DataFrame to professional RTF listing (no borders, left-aligned)
        
        Parameters
        ----------
        df : pd.DataFrame
            Data to format
        title : str
            Listing title
        subtitle : str
            Listing subtitle
        footnotes : List[str]
            List of footnotes
        output_file : str, optional
            Output file path
            
        Returns
        -------
        str
            RTF formatted listing string
        """
        if footnotes is None:
            footnotes = []
        
        # Build RTF document
        rtf_content = self._create_rtf_header(title, subtitle)
        
        # Create listing header (no borders, left-aligned)
        rtf_content += r"""{\pard\f0\fs""" + str(self.header_font_size) + r"""\b """
        
        # Add column headers with spacing
        col_headers = []
        for col in df.columns:
            col_headers.append(self._escape_rtf_text(str(col)))
        
        rtf_content += r"""\tab """.join(col_headers) + r"""\par}"""
        
        # Add separator line
        rtf_content += r"""{\pard\f0\fs""" + str(self.font_size) + r""" """
        rtf_content += "-" * 80 + r"""\par}"""
        
        # Add data rows (no borders, left-aligned)
        for _, row in df.iterrows():
            rtf_content += r"""{\pard\f0\fs""" + str(self.font_size) + r""" """
            
            row_data = []
            for val in row:
                row_data.append(self._escape_rtf_text(str(val) if not pd.isna(val) else ""))
            
            rtf_content += r"""\tab """.join(row_data) + r"""\par}"""
        
        # Add footnotes
        rtf_content += self._create_footnotes(footnotes)
        
        # Close RTF document
        rtf_content += r"""}"""
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(rtf_content)
        
        return rtf_content
    
    def format_clinical_table(self,
                             df: pd.DataFrame,
                             table_number: str,
                             table_title: str,
                             population: str = "Safety Analysis Population",
                             study_info: str = "CDISCPILOT01",
                             footnotes: List[str] = None,
                             output_file: Optional[str] = None,
                             is_listing: bool = False) -> str:
        """
        Format clinical table or listing with standard headers and footnotes
        
        Parameters
        ----------
        df : pd.DataFrame
            Clinical data
        table_number : str
            Table number (e.g., "14.1.1")
        table_title : str
            Descriptive title
        population : str
            Analysis population
        study_info : str
            Study identifier
        footnotes : List[str]
            Custom footnotes
        output_file : str, optional
            Output file path
        is_listing : bool
            Whether to format as listing (no borders) or table (with borders)
            
        Returns
        -------
        str
            RTF formatted clinical table or listing
        """
        if footnotes is None:
            footnotes = []
        
        # Standard clinical table/listing structure
        if is_listing:
            title = f"Listing {table_number}"
        else:
            title = f"Table {table_number}"
            
        subtitle = f"{table_title}\n{population}\nStudy {study_info}"
        
        # Add standard footnotes
        standard_footnotes = [
            f"N = number of subjects in analysis population",
            f"Generated on {pd.Timestamp.now().strftime('%d%b%Y %H:%M')}"
        ]
        
        if not is_listing:
            standard_footnotes.insert(1, "Percentages are based on the number of subjects in each treatment group")
        
        all_footnotes = footnotes + standard_footnotes
        
        if is_listing:
            return self.format_listing_to_rtf(
                df=df,
                title=title,
                subtitle=subtitle,
                footnotes=all_footnotes,
                output_file=output_file
            )
        else:
            return self.format_table_to_rtf(
                df=df,
                title=title,
                subtitle=subtitle,
                footnotes=all_footnotes,
                output_file=output_file
            )


def create_clinical_rtf_table(df: pd.DataFrame,
                             table_number: str,
                             table_title: str,
                             output_file: str,
                             is_listing: bool = False,
                             **kwargs) -> bool:
    """
    Convenience function to create clinical RTF table or listing
    
    Parameters
    ----------
    df : pd.DataFrame
        Data to format
    table_number : str
        Table number
    table_title : str
        Table title
    output_file : str
        Output file path
    is_listing : bool
        Whether to format as listing or table
    **kwargs
        Additional arguments for ClinicalRTFFormatter.format_clinical_table
        
    Returns
    -------
    bool
        Success status
    """
    try:
        formatter = ClinicalRTFFormatter()
        formatter.format_clinical_table(
            df=df,
            table_number=table_number,
            table_title=table_title,
            output_file=output_file,
            is_listing=is_listing,
            **kwargs
        )
        return True
    except Exception as e:
        print(f"Error creating RTF {'listing' if is_listing else 'table'}: {e}")
        return False


# Example usage and testing
if __name__ == "__main__":
    # Create sample clinical data
    sample_data = pd.DataFrame({
        'Treatment': ['Placebo', 'Xanomeline Low Dose', 'Xanomeline High Dose'],
        'N': [86, 84, 84],
        'Subjects with AEs': ['69 (80.2%)', '77 (91.7%)', '79 (94.0%)'],
        'Total Events': [301, 435, 455],
        'Serious AEs': [0, 1, 2]
    })
    
    # Create RTF table
    formatter = ClinicalRTFFormatter()
    rtf_output = formatter.format_clinical_table(
        df=sample_data,
        table_number="14.3.1",
        table_title="Overview of Adverse Events",
        footnotes=["AE = Adverse Event", "Serious AEs defined per ICH E2A guidelines"]
    )
    
    print("RTF table created successfully!")
    print(f"RTF content length: {len(rtf_output)} characters") 