"""
RTF Document Class for Clinical Reports
====================================

Provides a high-level interface for creating RTF documents
with clinical report formatting.
"""

import os
from typing import List, Optional, Union, Dict, Any
import base64


class RTFDocument:
    """RTF document class with clinical report formatting."""
    
    def __init__(self, orientation: str = 'portrait', margins: List[float] = None):
        """
        Initialize RTF document.
        
        Parameters
        ----------
        orientation : str
            'portrait' or 'landscape'
        margins : List[float]
            List of margins [left, right, top, bottom] in inches
        """
        self.orientation = orientation
        self.margins = margins or [1.0, 1.0, 1.0, 1.0]
        self.content = []
        
        # Initialize document
        self._init_document()
        
    def _init_document(self):
        """Initialize RTF document with headers."""
        # RTF header
        self.content.append(r'{\rtf1\ansi\deff0')
        
        # Font table
        self.content.append(r'{\fonttbl{\f0\froman\fcharset0 Times New Roman;}}')
        
        # Color table
        self.content.append(r'{\colortbl;\red0\green0\blue0;}')
        
        # Page setup
        if self.orientation == 'landscape':
            self.content.append(r'\landscape\paperw15840\paperh12240')  # Letter size
        else:
            self.content.append(r'\paperw12240\paperh15840')  # Letter size
            
        # Margins (convert inches to twips: 1 inch = 1440 twips)
        left, right, top, bottom = self.margins
        self.content.append(f"\\margl{int(left*1440)}\\margr{int(right*1440)}")
        self.content.append(f"\\margt{int(top*1440)}\\margb{int(bottom*1440)}")
        
    def add_header(self, text: str):
        """Add header to document."""
        self.content.append(r'{\header\pard\qr\f0\fs20')
        self.content.append(text)
        self.content.append(r'\par}')
        
    def add_paragraph(self, text: str, alignment: str = 'left',
                     font_size: int = 10, bold: bool = False,
                     italic: bool = False):
        """Add paragraph with formatting."""
        # Alignment
        align = {
            'left': r'\ql',
            'center': r'\qc',
            'right': r'\qr',
            'justify': r'\qj'
        }.get(alignment, r'\ql')
        
        # Font formatting
        format_str = f"\\f0\\fs{font_size*2}"  # RTF uses half-points
        if bold:
            format_str += r'\b'
        if italic:
            format_str += r'\i'
            
        # Add paragraph
        self.content.append(f"\\pard{align}{format_str}")
        self.content.append(text)
        
        # Reset formatting
        if bold:
            self.content.append(r'\b0')
        if italic:
            self.content.append(r'\i0')
            
        self.content.append(r'\par')
        
    def add_image(self, image_path: str, width: float = 6.5, height: float = 4.5):
        """
        Add image to document.
        
        Parameters
        ----------
        image_path : str
            Path to image file
        width : float
            Width in inches
        height : float
            Height in inches
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
            
        # Read image file
        with open(image_path, 'rb') as f:
            image_data = f.read()
            
        # Convert to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Calculate dimensions in twips (1 inch = 1440 twips)
        width_twips = int(width * 1440)
        height_twips = int(height * 1440)
        
        # Add image
        self.content.append(r'{\pict\pngblip')
        self.content.append(f"\\picw{width_twips}\\pich{height_twips}")
        self.content.append(image_base64)
        self.content.append(r'}')
        
    def add_page_number(self):
        """Add page number to footer."""
        self.content.append(r'{\footer\pard\qc\f0\fs20')
        self.content.append(r'Page \chpgn')
        self.content.append(r'\par}')
        
    def save(self, output_path: str):
        """Save document to file."""
        # Close RTF document
        self.content.append(r'}')
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(''.join(self.content)) 