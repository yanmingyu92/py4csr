"""
PDF formatter for clinical tables matching RRG output standards.

This formatter creates PDF output that matches the format and structure
of RRG clinical tables, using reportlab for PDF generation.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.lib.pagesizes import A4, landscape, letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        Frame,
        PageBreak,
        PageTemplate,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class ClinicalPDFFormatter:
    """
    PDF formatter for clinical tables with professional layout.

    Features:
    - Proper header with title, company, date, page numbers
    - Professional treatment column headers with N counts
    - P-value column integration
    - Proper indentation and spacing
    - Clinical table formatting standards
    - Footnotes with statistical methods
    """

    def __init__(
        self,
        company_name: str = "py4csr Clinical Reporting",
        website: str = "www.py4csr.com",
        page_size=None,
        orientation: str = "portrait",
    ):
        """
        Initialize the PDF formatter.

        Parameters
        ----------
        company_name : str
            Company/system name for header
        website : str
            Website for header
        page_size : tuple
            Page size (default: letter)
        orientation : str
            'portrait' or 'landscape'
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError(
                "reportlab is required for PDF generation. "
                "Install it with: pip install reportlab"
            )

        self.company_name = company_name
        self.website = website

        # Set page size
        if page_size is None:
            page_size = letter

        if orientation == "landscape":
            self.page_size = landscape(page_size)
        else:
            self.page_size = page_size

        # Setup styles
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles for clinical tables."""
        # Title style
        self.styles.add(
            ParagraphStyle(
                name="ClinicalTitle",
                parent=self.styles["Heading1"],
                fontSize=12,
                alignment=TA_CENTER,
                spaceAfter=6,
                spaceBefore=6,
            )
        )

        # Subtitle style
        self.styles.add(
            ParagraphStyle(
                name="ClinicalSubtitle",
                parent=self.styles["Normal"],
                fontSize=10,
                alignment=TA_CENTER,
                spaceAfter=4,
            )
        )

        # Header style
        self.styles.add(
            ParagraphStyle(
                name="HeaderLeft",
                parent=self.styles["Normal"],
                fontSize=9,
                alignment=TA_LEFT,
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="HeaderCenter",
                parent=self.styles["Normal"],
                fontSize=9,
                alignment=TA_CENTER,
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="HeaderRight",
                parent=self.styles["Normal"],
                fontSize=9,
                alignment=TA_RIGHT,
            )
        )

        # Footnote style
        self.styles.add(
            ParagraphStyle(
                name="Footnote",
                parent=self.styles["Normal"],
                fontSize=8,
                alignment=TA_LEFT,
                leftIndent=0,
            )
        )

    def create_professional_table(
        self,
        table_data: pd.DataFrame,
        output_file: str,
        title1: str = "",
        title2: str = "",
        title3: str = "",
        footnotes: List[str] = None,
        treatment_info: Dict[str, Any] = None,
        p_values: Dict[str, str] = None,
        orientation: str = None,
    ):
        """
        Create a professional clinical table in PDF format.

        Parameters
        ----------
        table_data : DataFrame
            The table data to format
        output_file : str
            Output PDF file path
        title1, title2, title3 : str
            Table titles
        footnotes : List[str]
            Table footnotes
        treatment_info : Dict
            Information about treatments and N counts
        p_values : Dict
            P-values for each row/variable
        orientation : str
            Override orientation for this table ('portrait' or 'landscape')
        """
        footnotes = footnotes or []
        treatment_info = treatment_info or {}
        p_values = p_values or {}

        # Determine page size for this table
        if orientation == "landscape":
            page_size = landscape(letter)
        elif orientation == "portrait":
            page_size = letter
        else:
            page_size = self.page_size

        # Create PDF document
        doc = SimpleDocTemplate(
            output_file,
            pagesize=page_size,
            rightMargin=0.5 * inch,
            leftMargin=0.5 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
        )

        # Build story (content)
        story = []

        # Add titles
        if title1:
            story.append(Paragraph(title1, self.styles["ClinicalTitle"]))
        if title2:
            story.append(Paragraph(title2, self.styles["ClinicalSubtitle"]))
        if title3:
            story.append(Paragraph(title3, self.styles["ClinicalSubtitle"]))

        story.append(Spacer(1, 0.2 * inch))

        # Create table
        table_obj = self._create_table(table_data, treatment_info, p_values)
        story.append(table_obj)

        # Add footnotes
        if footnotes:
            story.append(Spacer(1, 0.2 * inch))
            footnote_text = "Note: " + " ".join(footnotes)
            story.append(Paragraph(footnote_text, self.styles["Footnote"]))

        # Add program path
        story.append(Spacer(1, 0.1 * inch))
        story.append(
            Paragraph(
                "Generated by py4csr clinical reporting system", self.styles["Footnote"]
            )
        )

        # Build PDF with custom header/footer
        doc.build(
            story,
            onFirstPage=self._add_header_footer,
            onLaterPages=self._add_header_footer,
        )

    def _add_header_footer(self, canvas, doc):
        """Add header and footer to each page."""
        canvas.saveState()

        # Header
        date_str = datetime.now().strftime("%d%b%Y %H:%M").upper()

        # Left: Company name
        canvas.setFont("Times-Roman", 9)
        canvas.drawString(0.5 * inch, doc.height + 1.25 * inch, self.company_name)

        # Center: Website
        canvas.drawCentredString(
            doc.width / 2 + 0.5 * inch, doc.height + 1.25 * inch, self.website
        )

        # Right: Date and page number
        canvas.drawRightString(
            doc.width + 0.5 * inch, doc.height + 1.25 * inch, date_str
        )
        canvas.drawRightString(
            doc.width + 0.5 * inch,
            doc.height + 1.1 * inch,
            f"Page {canvas.getPageNumber()}",
        )

        canvas.restoreState()

    def _create_table(
        self,
        table_data: pd.DataFrame,
        treatment_info: Dict[str, Any],
        p_values: Dict[str, str],
    ):
        """Create reportlab Table object from DataFrame."""
        # Prepare data for table
        data = []

        # Header row
        header = list(table_data.columns)
        data.append(header)

        # Data rows
        for idx, row in table_data.iterrows():
            data.append([str(val) if pd.notna(val) else "" for val in row])

        # Create table
        table = Table(data)

        # Apply table style
        style = TableStyle(
            [
                # Header row
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 0), (-1, 0), 8),
                # Data rows
                ("FONTNAME", (0, 1), (-1, -1), "Times-Roman"),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),  # Center all except first column
                ("ALIGN", (0, 1), (0, -1), "LEFT"),  # Left align first column
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                # Grid
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("LINEBELOW", (0, 0), (-1, 0), 1, colors.black),
                # Padding
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 1), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
            ]
        )

        table.setStyle(style)

        return table


def convert_rtf_to_pdf(rtf_file: str, pdf_file: str):
    """
    Convert RTF file to PDF.

    Note: This is a placeholder. Full RTF to PDF conversion requires
    additional libraries like pypandoc or unoconv.

    Parameters
    ----------
    rtf_file : str
        Input RTF file path
    pdf_file : str
        Output PDF file path
    """
    raise NotImplementedError(
        "RTF to PDF conversion requires additional libraries. "
        "Use ClinicalPDFFormatter.create_professional_table() instead "
        "to generate PDF directly from DataFrame."
    )
