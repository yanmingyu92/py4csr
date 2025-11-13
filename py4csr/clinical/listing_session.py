"""
Clinical listing session for generating patient-level data listings.

This module provides functionality for creating clinical data listings
that match RRG's %rrg_deflist and related macros.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from .enhanced_rtf_formatter import EnhancedClinicalRTFFormatter
from .pdf_formatter import REPORTLAB_AVAILABLE, ClinicalPDFFormatter


class ClinicalListingSession:
    """
    Session for creating clinical data listings.

    This class provides functionality similar to RRG's %rrg_deflist macro,
    allowing creation of patient-level data listings with proper formatting.

    Examples
    --------
    >>> session = ClinicalListingSession(uri="l_aeinf")
    >>> session.deflist(
    ...     dataset=ae_data,
    ...     title1="Listing 14.3.2.9.1",
    ...     title2="Infusion Reactions",
    ...     orderby=['trt01pn', 'subjid', 'aestdtc']
    ... )
    >>> session.def_col(name='SUBJID', label='Patient ID', group=True, width='LWH')
    >>> session.def_col(name='ASR', label='Age/Sex', group=True, width='LWH')
    >>> session.def_col(name='aename', label='AE Term', width='1.8in')
    >>> session.genlist()
    >>> session.finalize(output_format='rtf')
    """

    def __init__(self, uri: str = "listing"):
        """
        Initialize a clinical listing session.

        Parameters
        ----------
        uri : str
            Unique identifier for this listing
        """
        self.uri = uri
        self.outname = uri

        # Listing configuration
        self.dataset = None
        self.config = {
            "titles": [],
            "footnotes": [],
            "orderby": [],
            "nodatamsg": "No data available",
            "bookmark_pdf": "",
            "bookmark_rtf": "",
            "savercd": "N",
            "splitchars": "//",
        }

        # Column definitions
        self.columns = []  # List of column definitions

        # Generated listing
        self.generated_listing = None

    def deflist(
        self,
        dataset: pd.DataFrame,
        title1: str = "",
        title2: str = "",
        title3: str = "",
        title4: str = "",
        title5: str = "",
        title6: str = "",
        footnot1: str = "",
        footnot2: str = "",
        footnot3: str = "",
        footnot4: str = "",
        footnot5: str = "",
        footnot6: str = "",
        footnot7: str = "",
        footnot8: str = "",
        orderby: List[str] = None,
        nodatamsg: str = "No data available",
        bookmark_pdf: str = "",
        bookmark_rtf: str = "",
        savercd: str = "N",
        splitchars: str = "//",
    ):
        """
        Define listing parameters (equivalent to RRG's %rrg_deflist).

        Parameters
        ----------
        dataset : DataFrame
            Input dataset for the listing
        title1-title6 : str
            Listing titles
        footnot1-footnot8 : str
            Listing footnotes
        orderby : List[str]
            Variables to sort by
        nodatamsg : str
            Message to display when no data
        bookmark_pdf : str
            PDF bookmark configuration
        bookmark_rtf : str
            RTF bookmark configuration
        savercd : str
            Whether to save record count ('Y' or 'N')
        splitchars : str
            Characters used to split multi-line cell content

        Returns
        -------
        self
            For method chaining
        """
        self.dataset = dataset.copy()

        # Store titles
        titles = [title1, title2, title3, title4, title5, title6]
        self.config["titles"] = [t for t in titles if t]

        # Store footnotes
        footnotes = [
            footnot1,
            footnot2,
            footnot3,
            footnot4,
            footnot5,
            footnot6,
            footnot7,
            footnot8,
        ]
        self.config["footnotes"] = [f for f in footnotes if f]

        # Store other config
        self.config["orderby"] = orderby or []
        self.config["nodatamsg"] = nodatamsg
        self.config["bookmark_pdf"] = bookmark_pdf
        self.config["bookmark_rtf"] = bookmark_rtf
        self.config["savercd"] = savercd
        self.config["splitchars"] = splitchars

        return self

    def def_col(
        self,
        name: str,
        label: str = "",
        group: bool = False,
        page: bool = False,
        width: str = "",
        skipline: bool = False,
        id: str = "",
    ):
        """
        Define a column for the listing (equivalent to RRG's %rrg_defcol).

        Parameters
        ----------
        name : str
            Variable name in dataset
        label : str
            Column label/header
        group : bool
            Whether this is a grouping variable
        page : bool
            Whether to page-by this variable
        width : str
            Column width (e.g., '1.8in', 'LWH')
        skipline : bool
            Whether to skip a line after this group
        id : str
            Column identifier

        Returns
        -------
        self
            For method chaining
        """
        col_def = {
            "name": name,
            "label": label or name,
            "group": group,
            "page": page,
            "width": width,
            "skipline": skipline,
            "id": id,
        }

        self.columns.append(col_def)
        return self

    def genlist(self):
        """
        Generate the listing (equivalent to RRG's %rrg_genlist).

        Returns
        -------
        self
            For method chaining
        """
        if self.dataset is None:
            raise ValueError("No dataset defined. Call deflist() first.")

        if not self.columns:
            raise ValueError("No columns defined. Call def_col() for each column.")

        # Sort data if orderby specified
        if self.config["orderby"]:
            # Filter orderby to only include columns that exist
            valid_orderby = [
                col for col in self.config["orderby"] if col in self.dataset.columns
            ]
            if valid_orderby:
                self.dataset = self.dataset.sort_values(valid_orderby)

        # Select and order columns based on column definitions
        col_names = [col["name"] for col in self.columns]

        # Filter to only include columns that exist in dataset
        valid_cols = [col for col in col_names if col in self.dataset.columns]

        if not valid_cols:
            raise ValueError(
                f"None of the defined columns exist in dataset. "
                f"Defined: {col_names}, Available: {list(self.dataset.columns)}"
            )

        # Create listing with selected columns
        self.generated_listing = self.dataset[valid_cols].copy()

        # Rename columns to use labels
        col_mapping = {}
        for col_def in self.columns:
            if col_def["name"] in valid_cols:
                col_mapping[col_def["name"]] = col_def["label"]

        self.generated_listing = self.generated_listing.rename(columns=col_mapping)

        # Handle split characters (// for multi-line cells)
        splitchars = self.config["splitchars"]
        if splitchars:
            for col in self.generated_listing.columns:
                self.generated_listing[col] = (
                    self.generated_listing[col]
                    .astype(str)
                    .str.replace(splitchars, "\n", regex=False)
                )

        print(f"[CHECK_MARK] Listing generated: {len(self.generated_listing)} rows")
        return self

    def finalize(self, output_file: str = None, output_format: str = "rtf"):
        """
        Finalize and save the generated listing.

        Parameters
        ----------
        output_file : str, optional
            Output filename. If None, uses session outname.
        output_format : str
            Output format ('rtf', 'pdf', 'csv')

        Returns
        -------
        self
            For method chaining
        """
        if self.generated_listing is None:
            raise ValueError("No listing generated. Call genlist() first.")

        if output_file is None:
            output_file = f"{self.outname}.{output_format}"

        if output_format.lower() == "rtf":
            self._save_listing_rtf(output_file)
        elif output_format.lower() == "pdf":
            self._save_listing_pdf(output_file)
        elif output_format.lower() == "csv":
            self._save_listing_csv(output_file)
        else:
            raise NotImplementedError(
                f"Output format '{output_format}' not yet implemented"
            )

        print(f"[CHECK_MARK] Listing finalized: {output_file}")
        return self

    def _save_listing_rtf(self, output_file: str):
        """Save listing as RTF."""
        formatter = EnhancedClinicalRTFFormatter()

        titles = self.config["titles"]
        footnotes = self.config["footnotes"]

        # Extract titles for formatter
        title1 = titles[0] if len(titles) > 0 else "Clinical Data Listing"
        title2 = titles[1] if len(titles) > 1 else ""
        title3 = titles[2] if len(titles) > 2 else ""

        # Create RTF output
        rtf_content = formatter.create_professional_table(
            self.generated_listing,
            title1=title1,
            title2=title2,
            title3=title3,
            footnotes=footnotes,
            treatment_info={},
            p_values={},
        )

        # Save to file
        Path(output_file).write_text(rtf_content, encoding="utf-8")

    def _save_listing_pdf(self, output_file: str):
        """Save listing as PDF."""
        if not REPORTLAB_AVAILABLE:
            raise ImportError(
                "reportlab is required for PDF generation. "
                "Install it with: pip install reportlab"
            )

        formatter = ClinicalPDFFormatter()

        titles = self.config["titles"]
        footnotes = self.config["footnotes"]

        # Extract titles for formatter
        title1 = titles[0] if len(titles) > 0 else "Clinical Data Listing"
        title2 = titles[1] if len(titles) > 1 else ""
        title3 = titles[2] if len(titles) > 2 else ""

        # Determine orientation based on number of columns
        num_cols = len(self.generated_listing.columns)
        orientation = "landscape" if num_cols > 6 else "portrait"

        # Create PDF output
        formatter.create_professional_table(
            self.generated_listing,
            output_file=output_file,
            title1=title1,
            title2=title2,
            title3=title3,
            footnotes=footnotes,
            treatment_info={},
            p_values={},
            orientation=orientation,
        )

    def _save_listing_csv(self, output_file: str):
        """Save listing as CSV."""
        self.generated_listing.to_csv(output_file, index=False, encoding="utf-8")
