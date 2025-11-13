"""
Data processing utilities for clinical trial datasets.

This module provides functions for reading, validating, and preprocessing
CDISC ADaM datasets commonly used in clinical study reports.
"""

from .adam_utils import (
    apply_cdisc_formats,
    create_analysis_dataset,
    create_frequency_table,
    create_summary_statistics,
    derive_analysis_flags,
    derive_demographic_categories,
    derive_disposition_variables,
    derive_treatment_variables,
    format_ae_data,
    format_lab_data,
    merge_adam_datasets,
    validate_adam_structure,
)
from .io import load_adam_data, load_dataset, read_sas, read_xpt
from .preprocessing import (
    apply_formats,
    clean_data,
    derive_variables,
    handle_missing_data,
)
from .validation import validate_adae, validate_adlb, validate_adsl

__all__ = [
    # I/O functions
    "read_sas",
    "read_xpt",
    "load_dataset",
    "load_adam_data",
    # Validation functions
    "validate_adsl",
    "validate_adae",
    "validate_adlb",
    "validate_adam_structure",
    # Preprocessing functions
    "apply_formats",
    "handle_missing_data",
    "derive_variables",
    "clean_data",
    "apply_cdisc_formats",
    # ADaM-specific utilities
    "derive_treatment_variables",
    "derive_analysis_flags",
    "derive_disposition_variables",
    "derive_demographic_categories",
    "merge_adam_datasets",
    "create_analysis_dataset",
    "format_ae_data",
    "format_lab_data",
    "create_summary_statistics",
    "create_frequency_table",
]
