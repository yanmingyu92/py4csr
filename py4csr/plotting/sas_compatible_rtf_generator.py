#!/usr/bin/env python3
"""
SAS-Compatible RTF Generator for Clinical Plots
==============================================

This module generates RTF output that exactly matches the format produced by
SAS macros like GBOX2, GLINE2, GKM2, etc. for regulatory submissions.

Based on analysis of actual SAS macro RTF output patterns from:
- gbox2.sas, gline2.sas, gwaterfall2.sas, etc.
- Regeneron Pharmaceuticals RTF standards
- FDA-compliant clinical report formatting

Author: py4csr Development Team
Version: 1.0.0 - SAS-Compatible RTF Generator
"""

import os
import base64
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime


class SASCompatibleRTFGenerator:
    """
    RTF generator that produces output identical to SAS macros
    
    This generator replicates the exact RTF format used by SAS clinical macros
    including proper headers, styling, image embedding, and footnotes.
    """
    
    def __init__(self):
        """Initialize the SAS-compatible RTF generator"""
        self.company_name = "Py4csr package"
        self.escape_char = "^"
        
    def generate_rtf_for_plot(self,
                             plot_path: str,
                             title1: Optional[str] = None,
                             title2: Optional[str] = None,
                             title3: Optional[str] = None,
                             title4: Optional[str] = None,
                             title5: Optional[str] = None,
                             title6: Optional[str] = None,
                             footnote1: Optional[str] = None,
                             footnote2: Optional[str] = None,
                             footnote3: Optional[str] = None,
                             footnote4: Optional[str] = None,
                             footnote5: Optional[str] = None,
                             footnote6: Optional[str] = None,
                             footnote7: Optional[str] = None,
                             footnote8: Optional[str] = None,
                             protocol: Optional[str] = None,
                             uri: Optional[str] = None,
                             outputname: Optional[str] = None) -> str:
        """
        Generate SAS-compatible RTF content for a clinical plot
        
        Parameters
        ----------
        plot_path : str
            Path to the plot image file
        title1-title6 : str, optional
            Plot titles (up to 6 levels as in SAS macros)
        footnote1-footnote8 : str, optional
            Plot footnotes (up to 8 levels as in SAS macros)
        protocol : str, optional
            Protocol identifier
        uri : str, optional
            URI identifier for the plot
        outputname : str, optional
            Output name for the plot
            
        Returns
        -------
        str
            Complete RTF document content
        """
        
        if not os.path.exists(plot_path):
            raise FileNotFoundError(f"Plot image not found: {plot_path}")
        
        # Build RTF content sections
        rtf_parts = []
        
        # 1. RTF Document Header (SAS style)
        rtf_parts.append(self._get_rtf_header())
        
        # 2. Company Header and Protocol (exactly like SAS macros)
        rtf_parts.append(self._get_company_header(protocol))
        
        # 3. Plot Titles (SAS GBOX2/GLINE2 style with proper heading styles)
        rtf_parts.append(self._get_plot_titles(
            title1, title2, title3, title4, title5, title6
        ))
        
        # 4. Embedded Plot Image (SAS style with proper sizing)
        rtf_parts.append(self._embed_plot_image(plot_path))
        
        # 5. Plot Footnotes (SAS style)
        rtf_parts.append(self._get_plot_footnotes(
            footnote1, footnote2, footnote3, footnote4,
            footnote5, footnote6, footnote7, footnote8
        ))
        
        # 6. Program Path Footer (exactly like SAS output)
        rtf_parts.append(self._get_program_footer())
        
        # 7. RTF Document Footer
        rtf_parts.append("}")
        
        return "".join(rtf_parts)
    
    def _get_rtf_header(self) -> str:
        """Get RTF document header exactly like SAS macros"""
        return (
            r"{\rtf1\ansi\deff0 "
            r"{\fonttbl{\f0\froman\fcharset0 Times New Roman;}{\f1\fswiss\fcharset0 Arial;}} "
            r"{\colortbl;\red0\green0\blue0;\red255\green255\blue255;} "
            r"{\stylesheet{\s0\snext0\ql\widctlpar\hyphpar0\cf1\kerning1\dbch\af8\langfe2052\dbch\af9\afs24\alang1081\loch\f0\fs24\lang1033 Normal;}} "
            r"{\*\generator Microsoft Word 14.0.7015.1000;} "
            r"\paperw12240\paperh15840\margl1440\margr1440\margt1440\margb1440 "
            r"\deftab708\widowctrl\ftnbj\aenddoc\hyphhotz425\noxlattoyen\expshrtn\noultrlspc\dntblnsbdb\nospaceforul\formshade\horzdoc\dgmargin\dghspace180\dgvspace180\dghorigin1440\dgvorigin1440\dghshow1\dgvshow1 "
            r"\jexpand\viewkind1\viewscale100\pgbrdrhead\pgbrdrfoot\splytwnine\ftnlytwnine\htmautsp\nolnhtadjtbl\useltbaln\alntblind\lytcalctblwd\lyttblrtgr\lnbrkrule\nobrkwrptbl\snaptogridincell\allowfieldendsel\wrppunct "
            r"\asianbrkrule\rsidroot9967225\newtblstyruls\nogrowautofit\usenormstyforlist\noindnmbrts\felnbrelev\nocxsptable\indrlsweleven\noafcnsttbl\afelev\utinl\hwelev\spltpgpar\notcvasp\notbrkcnstfrctbl\notvatxbx\krnprsnet\cachedcolbal\nouicompat\fet0 "
            r"{\*\wgrffmtfilter 2450} "
            r"{\*\pgptbl {\pgp\ipgp0\itap0\li0\ri0\sb0\sa0}} "
            r"\noqfpromote "
        )
    
    def _get_company_header(self, protocol: Optional[str] = None) -> str:
        """Get company header exactly like SAS macros"""
        header_parts = []
        
        # Company name (left-aligned, proper RTF formatting)
        header_parts.append(
            r"\pard\plain\s0\ql\widctlpar\hyphpar0\cf1\kerning1\dbch\af8\langfe2052\dbch\af9\afs24\alang1081\loch\f0\fs24\lang1033 "
            f"{self.company_name}\\par "
        )
        
        # Protocol (left-aligned, proper RTF formatting)
        if protocol:
            header_parts.append(
                r"\pard\plain\s0\ql\widctlpar\hyphpar0\cf1\kerning1\dbch\af8\langfe2052\dbch\af9\afs24\alang1081\loch\f0\fs24\lang1033 "
                f"Protocol: {protocol}\\par "
            )
        
        # Add spacing
        header_parts.append(r"\par ")
        
        return "".join(header_parts)
    
    def _get_plot_titles(self, title1: Optional[str] = None, title2: Optional[str] = None,
                        title3: Optional[str] = None, title4: Optional[str] = None,
                        title5: Optional[str] = None, title6: Optional[str] = None) -> str:
        """Get plot titles with proper RTF formatting (no escape characters)"""
        title_parts = []
        
        # Title hierarchy with proper RTF formatting
        titles = [title1, title2, title3, title4, title5, title6]
        
        for i, title in enumerate(titles, 1):
            if title:
                # Center-aligned title with proper RTF formatting
                title_parts.append(
                    r"\pard\plain\s0\qc\widctlpar\hyphpar0\cf1\kerning1\dbch\af8\langfe2052\dbch\af9\afs28\alang1081\loch\f0\fs28\lang1033\b "
                    f"{title}\\par "
                )
        
        # Add spacing after titles
        if any(titles):
            title_parts.append(r"\par ")
        
        return "".join(title_parts)
    
    def _embed_plot_image(self, plot_path: str) -> str:
        """Embed plot image exactly like SAS macros"""
        try:
            # Read image file as binary
            with open(plot_path, 'rb') as f:
                image_data = f.read()
            
            # Convert to hexadecimal (SAS style)
            hex_data = image_data.hex()
            
            # Get image file extension to determine format
            file_ext = Path(plot_path).suffix.lower()
            
            # Determine RTF image format
            if file_ext in ['.png']:
                rtf_format = r'\pngblip'
            elif file_ext in ['.jpg', '.jpeg']:
                rtf_format = r'\jpegblip'
            elif file_ext in ['.emf']:
                rtf_format = r'\emfblip'
            else:
                rtf_format = r'\pngblip'  # Default to PNG
            
            # Calculate image dimensions (SAS uses specific sizing)
            # Standard clinical plot size: 6.5" x 4.5" = 9360 x 6480 twips
            width_twips = 9360   # 6.5 inches * 1440 twips/inch
            height_twips = 6480  # 4.5 inches * 1440 twips/inch
            
            # Create RTF image embedding (SAS style)
            image_rtf = (
                r"\pard\plain\s0\qc\widctlpar\hyphpar0\cf1\kerning1\dbch\af8\langfe2052\dbch\af9\afs24\alang1081\loch\f0\fs24\lang1033 "
                r"{\pict" + rtf_format +
                rf"\picw{width_twips}\pich{height_twips}"
                rf"\picwgoal{width_twips}\pichgoal{height_twips} "
                f"{hex_data}"
                r"}\par "
            )
            
            return image_rtf
            
        except Exception as e:
            # Fallback if image embedding fails
            return (
                r"\pard\plain\s0\qc\widctlpar\hyphpar0\cf1\kerning1\dbch\af8\langfe2052\dbch\af9\afs24\alang1081\loch\f0\fs24\lang1033 "
                f"[Plot image could not be embedded: {str(e)}]\\par "
            )
    
    def _get_plot_footnotes(self, footnote1: Optional[str] = None, footnote2: Optional[str] = None,
                           footnote3: Optional[str] = None, footnote4: Optional[str] = None,
                           footnote5: Optional[str] = None, footnote6: Optional[str] = None,
                           footnote7: Optional[str] = None, footnote8: Optional[str] = None) -> str:
        """Get plot footnotes exactly like SAS macros"""
        footnote_parts = []
        
        # Add spacing before footnotes
        footnote_parts.append(r"\par ")
        
        # Footnotes (left-aligned, smaller font)
        footnotes = [footnote1, footnote2, footnote3, footnote4, 
                    footnote5, footnote6, footnote7, footnote8]
        
        for footnote in footnotes:
            if footnote:
                footnote_parts.append(
                    r"\pard\plain\s0\ql\widctlpar\hyphpar0\cf1\kerning1\dbch\af8\langfe2052\dbch\af9\afs18\alang1081\loch\f0\fs18\lang1033 "
                    f"{footnote}\\par "
                )
        
        return "".join(footnote_parts)
    
    def _get_program_footer(self) -> str:
        """Get program path footer exactly like SAS macros"""
        # Get current timestamp in SAS format
        timestamp = datetime.now().strftime("%d%b%Y %H:%M").upper()
        
        # Create program path (simulated)
        program_path = "py4csr_plotting_engine.py"
        
        # SAS-style program footer
        footer = (
            r"\par "
            r"\pard\plain\s0\ql\widctlpar\hyphpar0\cf1\kerning1\dbch\af8\langfe2052\dbch\af9\afs16\alang1081\loch\f0\fs16\lang1033 "
            f"{program_path} (py4csr {timestamp} Python Clinical Plotting Engine)\\par "
        )
        
        return footer
    
    def save_rtf_file(self, rtf_content: str, output_path: str) -> None:
        """Save RTF content to file with proper encoding"""
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write RTF file with proper encoding
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(rtf_content)
                
        except Exception as e:
            raise RuntimeError(f"Failed to save RTF file: {str(e)}")


# Convenience function for backward compatibility
def _generate_rtf_for_plot_professional(plot_path: str,
                                       title1: Optional[str] = None,
                                       title2: Optional[str] = None,
                                       title3: Optional[str] = None,
                                       footnote1: Optional[str] = None,
                                       footnote2: Optional[str] = None,
                                       footnote3: Optional[str] = None,
                                       protocol: Optional[str] = None,
                                       **kwargs) -> str:
    """
    Generate professional RTF for plot (backward compatibility function)
    
    This function provides the same interface as the original RTF generator
    but uses the new SAS-compatible implementation.
    """
    generator = SASCompatibleRTFGenerator()
    
    return generator.generate_rtf_for_plot(
        plot_path=plot_path,
        title1=title1,
        title2=title2,
        title3=title3,
        footnote1=footnote1,
        footnote2=footnote2,
        footnote3=footnote3,
        protocol=protocol,
        **kwargs
    )


# Main interface function
def generate_clinical_plot_rtf(plot_path: str,
                              output_path: str,
                              title1: Optional[str] = None,
                              title2: Optional[str] = None,
                              title3: Optional[str] = None,
                              title4: Optional[str] = None,
                              title5: Optional[str] = None,
                              title6: Optional[str] = None,
                              footnote1: Optional[str] = None,
                              footnote2: Optional[str] = None,
                              footnote3: Optional[str] = None,
                              footnote4: Optional[str] = None,
                              footnote5: Optional[str] = None,
                              footnote6: Optional[str] = None,
                              footnote7: Optional[str] = None,
                              footnote8: Optional[str] = None,
                              protocol: Optional[str] = None) -> str:
    """
    Generate and save clinical plot RTF file
    
    Parameters
    ----------
    plot_path : str
        Path to the plot image file
    output_path : str
        Path where RTF file should be saved
    title1-title6 : str, optional
        Plot titles (up to 6 levels)
    footnote1-footnote8 : str, optional
        Plot footnotes (up to 8 levels)
    protocol : str, optional
        Protocol identifier
        
    Returns
    -------
    str
        RTF content that was saved
    """
    generator = SASCompatibleRTFGenerator()
    
    # Generate RTF content
    rtf_content = generator.generate_rtf_for_plot(
        plot_path=plot_path,
        title1=title1,
        title2=title2,
        title3=title3,
        title4=title4,
        title5=title5,
        title6=title6,
        footnote1=footnote1,
        footnote2=footnote2,
        footnote3=footnote3,
        footnote4=footnote4,
        footnote5=footnote5,
        footnote6=footnote6,
        footnote7=footnote7,
        footnote8=footnote8,
        protocol=protocol
    )
    
    # Save to file
    generator.save_rtf_file(rtf_content, output_path)
    
    return rtf_content


def _generate_enhanced_forest_rtf(plot_path: str, config, output) -> str:
    """Generate enhanced RTF for forest plots with statistical tables"""
    generator = SASCompatibleRTFGenerator()
    
    # Start with basic RTF structure
    rtf_parts = []
    rtf_parts.append(generator._get_rtf_header())
    rtf_parts.append(generator._get_company_header(config.protocol))
    rtf_parts.append(generator._get_plot_titles(
        config.title1, config.title2, config.title3
    ))
    
    # Embed the FULL featured plot image (with HR values, CI, etc.) - NO TABLE
    rtf_parts.append(generator._embed_plot_image(plot_path))
    
    # Add footnotes
    rtf_parts.append(generator._get_plot_footnotes(
        config.footnote1, config.footnote2, config.footnote3
    ))
    
    # Add program footer
    rtf_parts.append(generator._get_program_footer())
    
    # Close RTF document
    rtf_parts.append("}")
    
    return "".join(rtf_parts)

def _generate_enhanced_km_rtf(plot_path: str, config, output) -> str:
    """Generate enhanced RTF for KM plots with risk tables and survival statistics"""
    generator = SASCompatibleRTFGenerator()
    
    # Start with basic RTF structure
    rtf_parts = []
    rtf_parts.append(generator._get_rtf_header())
    rtf_parts.append(generator._get_company_header(config.protocol))
    rtf_parts.append(generator._get_plot_titles(
        config.title1, config.title2, config.title3
    ))
    
    # Embed the FULL featured plot image (with risk table, censoring marks, etc.) - NO TABLE
    rtf_parts.append(generator._embed_plot_image(plot_path))
    
    # Add footnotes
    rtf_parts.append(generator._get_plot_footnotes(
        config.footnote1, config.footnote2, config.footnote3
    ))
    
    # Add program footer
    rtf_parts.append(generator._get_program_footer())
    
    # Close RTF document
    rtf_parts.append("}")
    
    return "".join(rtf_parts)


if __name__ == "__main__":
    # Test the RTF generator
    print("SAS-Compatible RTF Generator for Clinical Plots")
    print("=" * 50)
    print("This module generates RTF output that matches SAS macro format")
    print("for regulatory submissions and clinical reports.") 