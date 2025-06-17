"""
Enhanced RTF formatter for clinical tables matching professional standards.

This formatter creates RTF output that matches the format and structure
of established clinical reporting systems like RRG.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
from pathlib import Path


class EnhancedClinicalRTFFormatter:
    """
    Enhanced RTF formatter for clinical tables with professional layout.
    
    Features:
    - Proper header with title, website/company, date, page numbers
    - Professional treatment column headers with N counts
    - P-value column integration
    - Proper indentation and spacing
    - Clinical table formatting standards
    - Footnotes with statistical methods
    """
    
    def __init__(self, 
                 company_name: str = "py4csr Clinical Reporting",
                 website: str = "www.py4csr.com",
                 font_size: int = 18):
        """
        Initialize the enhanced RTF formatter.
        
        Parameters
        ----------
        company_name : str
            Company/system name for header
        website : str
            Website for header
        font_size : int
            Base font size
        """
        self.company_name = company_name
        self.website = website
        self.font_size = font_size
    
    def create_professional_table(self,
                                 table_data: pd.DataFrame,
                                 title1: str = "",
                                 title2: str = "",
                                 title3: str = "",
                                 footnotes: List[str] = None,
                                 treatment_info: Dict[str, Any] = None,
                                 p_values: Dict[str, str] = None) -> str:
        """
        Create a professional clinical table in RTF format.
        
        Parameters
        ----------
        table_data : DataFrame
            The table data to format
        title1, title2, title3 : str
            Table titles
        footnotes : List[str]
            Table footnotes
        treatment_info : Dict
            Information about treatments and N counts
        p_values : Dict
            P-values for each row/variable
            
        Returns
        -------
        str
            RTF formatted table
        """
        footnotes = footnotes or []
        treatment_info = treatment_info or {}
        p_values = p_values or {}
        
        # Build RTF content
        rtf_parts = []
        
        # RTF Header
        rtf_parts.append(self._get_rtf_header())
        
        # Page Header
        rtf_parts.append(self._get_page_header())
        
        # Table Titles
        rtf_parts.append(self._get_table_titles(title1, title2, title3))
        
        # Main Table
        rtf_parts.append(self._get_main_table(table_data, treatment_info, p_values))
        
        # Footnotes
        if footnotes:
            rtf_parts.append(self._get_footnotes(footnotes))
        
        # Program Path (like in reference)
        rtf_parts.append(self._get_program_path())
        
        # RTF Footer
        rtf_parts.append("}")
        
        return "".join(rtf_parts)
    
    def _get_rtf_header(self) -> str:
        """Get RTF document header with fonts and formatting."""
        return (
            "{\\rtf1\\adeflang1025\\ansi\\ansicpg1252\\uc1\\adeff0\\deff0\\stshfdbch0\\stshfloch0\\stshfhich0\\stshfbi0"
            "\\deflang1033\\deflangfe1033\\themelang1033\\themelangfe0\\themelangcs0"
            "{\\fonttbl{\\f0\\fbidi \\froman\\fcharset0\\fprq2{\\*\\panose 02020603050405020304}Times New Roman;}"
            "{\\f34\\fbidi \\froman\\fcharset0\\fprq2{\\*\\panose 02040503050406030204}Cambria Math;}}"
            "{\\colortbl;\\red0\\green0\\blue0;\\red0\\green0\\blue255;\\red0\\green255\\blue255;"
            "\\red0\\green255\\blue0;\\red255\\green0\\blue255;\\red255\\green0\\blue0;"
            "\\red255\\green255\\blue0;\\red255\\green255\\blue255;\\red0\\green0\\blue128;"
            "\\red0\\green128\\blue128;\\red0\\green128\\blue0;\\red128\\green0\\blue128;"
            "\\red128\\green0\\blue0;\\red128\\green128\\blue0;\\red128\\green128\\blue128;"
            "\\red192\\green192\\blue192;\\red255\\green255\\blue255;}"
            "\\paperw12240\\paperh15820\\margl1440\\margr1440\\margt1440\\margb1440\\gutter0\\ltrsect "
            "\\widowctrl\\ftnbj\\aenddoc\\noxlattoyen\\expshrtn\\noultrlspc\\dntblnsbdb\\nospaceforul"
            "\\horzdoc\\dghspace120\\dgvspace120\\dghorigin1701\\dgvorigin1984\\dghshow0\\dgvshow3"
        )
    
    def _get_page_header(self) -> str:
        """Get the professional page header in RRG format."""
        date_str = datetime.now().strftime("%d%b%Y %H:%M").upper()
        
        return (
            "\\ltrrow\\trowd \\irow0\\irowband0\\ltrrow\\ts11\\trqc\\trleft0\\trkeep\\trhdr\\trftsWidth1\\tblind0\\tblindtype3 "
            "\\clvertalt\\clbrdrt\\brdrnone \\clbrdrl\\brdrnone \\clbrdrb\\brdrnone \\clbrdrr\\brdrnone "
            "\\cltxlrtb\\clftsWidth3\\clwWidth3120\\clshdrawnil \\cellx3120"
            "\\clvertalt\\clbrdrt\\brdrnone \\clbrdrl\\brdrnone \\clbrdrb\\brdrnone \\clbrdrr\\brdrnone "
            "\\cltxlrtb\\clftsWidth3\\clwWidth3120\\clshdrawnil \\cellx6240"
            "\\clvertalt\\clbrdrt\\brdrnone \\clbrdrl\\brdrnone \\clbrdrb\\brdrnone \\clbrdrr\\brdrnone "
            "\\cltxlrtb\\clftsWidth3\\clwWidth3120\\clshdrawnil \\cellx9360"
            "\\pard \\ltrpar\\ql \\li0\\ri0\\sa80\\sl220\\slmult0\\nowidctlpar\\intbl\\wrapdefault\\faauto\\rin0\\lin0 "
            f"{{\\rtlch\\fcs1 \\af0\\afs{self.font_size} \\ltrch\\fcs0 \\fs{self.font_size} {self.company_name}\\cell }}"
            "\\pard \\ltrpar\\qc \\li0\\ri0\\sa80\\sl220\\slmult0\\nowidctlpar\\intbl\\wrapdefault\\faauto\\rin0\\lin0 "
            f"{{\\rtlch\\fcs1 \\af0\\afs{self.font_size} \\ltrch\\fcs0 \\fs{self.font_size} {self.website}\\cell }}"
            "\\pard \\ltrpar\\qr \\li0\\ri0\\sl220\\slmult0\\nowidctlpar\\intbl\\wrapdefault\\faauto\\rin0\\lin0 "
            f"{{\\rtlch\\fcs1 \\af0\\afs{self.font_size} \\ltrch\\fcs0 \\fs{self.font_size} {date_str}\\par }}"
            "\\pard \\ltrpar\\qr \\li0\\ri0\\sa80\\sl220\\slmult0\\nowidctlpar\\intbl\\wrapdefault\\faauto\\rin0\\lin0 "
            "{\\rtlch\\fcs1 \\af0\\afs18 \\ltrch\\fcs0 \\fs18 Page 1 of 1\\cell }\\row "
        )
    
    def _get_table_titles(self, title1: str, title2: str, title3: str) -> str:
        """Get formatted table titles."""
        titles = []
        if title1:
            titles.append(title1)
        if title2:
            titles.append(title2)
        
        if not titles:
            return ""
        
        title_rtf = (
            "\\ltrrow\\trowd \\irow1\\irowband1\\ltrrow\\ts11\\trqc\\trleft0\\trkeep\\trhdr\\trftsWidth1\\tblind0\\tblindtype3 "
            "\\clvertalt\\clbrdrt\\brdrnone \\clbrdrl\\brdrnone \\clbrdrb\\brdrnone \\clbrdrr\\brdrnone "
            "\\cltxlrtb\\clftsWidth3\\clwWidth9360\\clshdrawnil \\cellx9360"
            "\\pard \\ltrpar\\qc \\li0\\ri0\\sl220\\slmult0\\nowidctlpar\\intbl\\wrapdefault\\faauto\\rin0\\lin0 "
            "{\\rtlch\\fcs1 \\af0\\afs18 \\ltrch\\fcs0 \\fs18 "
            + "\\par ".join(titles) + 
            "\\cell }\\row "
        )
        
        # Add population line only once (title3 is the population text)
        if title3:
            title_rtf += (
                "\\ltrrow\\trowd \\irow2\\irowband2\\ltrrow\\ts11\\trqc\\trleft0\\trkeep\\trhdr\\trftsWidth1\\tblind0\\tblindtype3 "
                "\\clvertalt\\clbrdrt\\brdrnone \\clbrdrl\\brdrnone \\clbrdrb\\brdrnone \\clbrdrr\\brdrnone "
                "\\cltxlrtb\\clftsWidth3\\clwWidth9360\\clshdrawnil \\cellx9360"
                "\\pard \\ltrpar\\qc \\li0\\ri0\\sa80\\sl220\\slmult0\\nowidctlpar\\intbl\\wrapdefault\\faauto\\rin0\\lin0 "
                "{\\rtlch\\fcs1 \\af0\\afs18 \\ltrch\\fcs0 \\fs18 " + title3 + "\\cell }\\row "
            )
        
        return title_rtf
    
    def _get_main_table(self, 
                       table_data: pd.DataFrame, 
                       treatment_info: Dict[str, Any],
                       p_values: Dict[str, str]) -> str:
        """Get the main data table with proper clinical formatting."""
        if table_data.empty:
            return ""
        
        # Extract treatment columns (exclude Parameter)
        param_col = "Parameter"
        treatment_cols = [col for col in table_data.columns if col != param_col]
        
        # Calculate column widths - use RRG reference dimensions
        # Standard page width with margins is approximately 9360 twips
        total_width = 9360  # Reduced from 12960 to fit in page margins
        param_width = 1560   # First column (Category)
        remaining_width = total_width - param_width
        
        if len(treatment_cols) > 0:
            # Reserve space for p-value column (same as treatment columns)
            trt_width = remaining_width // (len(treatment_cols) + 1)  # +1 for p-value column
            pval_width = trt_width
        else:
            trt_width = 1560
            pval_width = 1560
        
        # Build column definitions
        col_defs = []
        current_x = param_width
        col_defs.append(f"\\clvertalt\\clbrdrt\\brdrs\\brdrw10 \\clbrdrl\\brdrnone \\clbrdrb\\brdrs\\brdrw10 \\clbrdrr\\brdrnone \\cltxlrtb\\clftsWidth3\\clwWidth{param_width}\\clshdrawnil \\cellx{current_x}")
        
        for i, col in enumerate(treatment_cols):
            current_x += trt_width
            col_defs.append(f"\\clvertalt\\clbrdrt\\brdrs\\brdrw10 \\clbrdrl\\brdrnone \\clbrdrb\\brdrs\\brdrw10 \\clbrdrr\\brdrnone \\cltxlrtb\\clftsWidth3\\clwWidth{trt_width}\\clshdrawnil \\cellx{current_x}")
        
        # P-value column
        current_x += pval_width
        col_defs.append(f"\\clvertalt\\clbrdrt\\brdrs\\brdrw10 \\clbrdrl\\brdrnone \\clbrdrb\\brdrs\\brdrw10 \\clbrdrr\\brdrnone \\cltxlrtb\\clftsWidth3\\clwWidth{pval_width}\\clshdrawnil \\cellx{current_x}")
        
        col_def_str = "".join(col_defs)
        
        # Header row
        header_rtf = (
            f"\\trowd \\irow3\\irowband3\\ltrrow\\ts11\\trqc\\trleft0\\trkeep\\trhdr\\trftsWidth1\\trftsWidthA3\\trwWidthA20\\tblind0\\tblindtype3 {col_def_str}"
            "\\pard \\ltrpar\\ql \\li0\\ri0\\sa80\\sl220\\slmult0\\nowidctlpar\\intbl\\wrapdefault\\faauto\\rin0\\lin0 "
            "{\\rtlch\\fcs1 \\af0\\afs18 \\ltrch\\fcs0 \\fs18 Category\\cell }"
        )
        
        # Treatment headers with N counts
        for col in treatment_cols:
            # Get treatment name and N count from treatment_info
            trt_name = col
            n_count = "?"
            
            if treatment_info and col in treatment_info:
                trt_name = treatment_info[col].get('name', col)
                n_count = str(treatment_info[col].get('n', '?'))
            else:
                # Try to map common treatment values to names
                if col == "0.0":
                    trt_name = "Placebo"
                elif col == "54.0":
                    trt_name = "Xanomeline Low Dose"
                elif col == "81.0":
                    trt_name = "Xanomeline High Dose"
                    
                # For N count, look at actual data
                col_data = table_data[col]
                n_values = []
                for val in col_data:
                    if pd.notna(val) and str(val).strip():
                        # Extract N from strings like "86" in first row
                        try:
                            if str(val).isdigit():
                                n_values.append(int(val))
                        except:
                            pass
                if n_values:
                    n_count = str(max(n_values))  # Use the largest N found
            
            header_rtf += (
                "\\pard \\ltrpar\\qc \\li0\\ri0\\sl220\\slmult0\\nowidctlpar\\intbl\\wrapdefault\\faauto\\rin0\\lin0 "
                f"{{\\rtlch\\fcs1 \\af0\\afs18 \\ltrch\\fcs0 \\fs18 {trt_name}\\par }}"
                "\\pard \\ltrpar\\qc \\li0\\ri0\\sa80\\sl220\\slmult0\\nowidctlpar\\intbl\\wrapdefault\\faauto\\rin0\\lin0 "
                f"{{\\rtlch\\fcs1 \\af0\\afs18 \\ltrch\\fcs0 \\fs18 (N={n_count})\\cell }}"
            )
        
        # P-value header
        header_rtf += (
            "\\pard \\ltrpar\\qc \\li0\\ri0\\sl220\\slmult0\\nowidctlpar\\intbl\\wrapdefault\\faauto\\rin0\\lin0 "
            "{\\rtlch\\fcs1 \\af0\\afs18 \\ltrch\\fcs0 \\fs18 p-Value\\cell }\\row "
        )
        
        # Data rows
        data_rtf = ""
        for idx, row in table_data.iterrows():
            # Row definition (without header borders)
            row_col_defs = col_def_str.replace("\\clbrdrt\\brdrs\\brdrw10", "\\clbrdrt\\brdrnone").replace("\\clbrdrb\\brdrs\\brdrw10", "\\clbrdrb\\brdrnone")
            
            data_rtf += f"\\trowd \\irow{idx+4}\\irowband{(idx+4) % 2}\\ltrrow\\ts11\\trqc\\trleft0\\trkeep\\trftsWidth1\\trftsWidthA3\\trwWidthA20\\tblind0\\tblindtype3 {row_col_defs}"
            
            # Parameter cell with proper indentation
            param_text = str(row[param_col])
            indent_level = 0
            
            # Detect indentation from leading spaces
            if param_text.startswith("  "):
                indent_level = 200 if param_text.startswith("    ") else 100
                
            data_rtf += (
                f"\\pard \\ltrpar\\ql \\li{indent_level}\\ri0\\sl220\\slmult0\\nowidctlpar\\intbl\\wrapdefault\\faauto\\rin0\\lin{indent_level} "
                f"{{\\rtlch\\fcs1 \\af0\\afs18 \\ltrch\\fcs0 \\fs18 {param_text.strip()}\\cell }}"
            )
            
            # Treatment data cells
            for col in treatment_cols:
                value = str(row[col]) if pd.notna(row[col]) else ""
                data_rtf += (
                    "\\pard \\ltrpar\\ql \\li0\\ri0\\sl220\\slmult0\\nowidctlpar\\intbl\\tqdec\\tx1100\\wrapdefault\\faauto\\rin0\\lin0 "
                    f"{{\\rtlch\\fcs1 \\af0\\afs18 \\ltrch\\fcs0 \\fs18 {value}\\cell }}"
                )
            
            # P-value cell
            param_key = str(row[param_col]).strip()
            pval = p_values.get(param_key, "")
            data_rtf += (
                "\\pard \\ltrpar\\ql \\li0\\ri0\\sl220\\slmult0\\nowidctlpar\\intbl\\tqdec\\tx680\\wrapdefault\\faauto\\rin0\\lin0 "
                f"{{\\rtlch\\fcs1 \\af0\\afs18 \\ltrch\\fcs0 \\fs18 {pval}\\cell }}\\row "
            )
        
        return header_rtf + data_rtf
    
    def _get_footnotes(self, footnotes: List[str]) -> str:
        """Get formatted footnotes section."""
        if not footnotes:
            return ""
        
        # Use single-cell structure like the reference RTF, not separated columns
        footnote_rtf = (
            "\\trowd \\irow26\\irowband26\\ltrrow\\ts11\\trqc\\trleft0\\trkeep\\trftsWidth1\\tblind0\\tblindtype3 "
            "\\clvertalt\\clbrdrt\\brdrnone \\clbrdrl\\brdrnone \\clbrdrb\\brdrnone \\clbrdrr\\brdrnone "
            "\\cltxlrtb\\clftsWidth3\\clwWidth9360\\clshdrawnil \\cellx9360"
            "\\pard \\ltrpar\\ql \\li0\\ri0\\sb520\\sl220\\slmult0\\nowidctlpar\\intbl\\brdrt\\brdrs\\brdrw15 \\wrapdefault\\faauto\\rin0\\lin0 "
            f"{{\\rtlch\\fcs1 \\af0\\afs18 \\ltrch\\fcs0 \\fs18 Note: {' '.join(footnotes)}\\cell }}\\row "
        )
        
        return footnote_rtf
    
    def _get_program_path(self) -> str:
        """Get program path footer like in reference."""
        return (
            "\\trowd \\irow28\\irowband28\\lastrow \\ltrrow\\ts11\\trqc\\trleft0\\trkeep\\trftsWidth1\\tblind0\\tblindtype3 "
            "\\clvertalt\\clbrdrt\\brdrnone \\clbrdrl\\brdrnone \\clbrdrb\\brdrnone \\clbrdrr\\brdrnone "
            "\\cltxlrtb\\clftsWidth3\\clwWidth9360\\clshdrawnil \\cellx9360"
            "\\pard \\ltrpar\\ql \\li0\\ri0\\sb80\\sl220\\slmult0\\nowidctlpar\\intbl\\wrapdefault\\faauto\\rin0\\lin0 "
            "{\\rtlch\\fcs1 \\af0\\afs18 \\ltrch\\fcs0 \\fs18 Generated by py4csr clinical reporting system\\cell }\\row "
            "\\pard \\ltrpar\\ql \\li0\\ri0\\nowidctlpar\\wrapdefault\\faauto\\rin0\\lin0\\itap0 "
        )
    
    def save_table(self, rtf_content: str, filename: str):
        """Save RTF content to file."""
        Path(filename).write_text(rtf_content, encoding='utf-8') 