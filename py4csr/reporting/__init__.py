"""
Reporting module for py4csr.

This module provides comprehensive reporting capabilities for clinical study reports,
including both traditional table generation and a new functional programming approach
inspired by the SAS RRG system.

The module includes:
- RTF table generation with full r2rtf compatibility
- Functional report builder with method chaining
- Configuration-driven statistical displays
- Template-based table generation
- ICH E3 and CTD compliance features
"""

# Traditional RTF table generation (r2rtf compatible)
from .rtf_table import (
    RTFTable,
    rtf_page_header,
    rtf_page_footer,
    rtf_title,
    rtf_subline,
    rtf_colheader,
    rtf_body,
    rtf_footnote,
    rtf_source,
    rtf_page,
    rtf_encode,
    write_rtf
)

# Functional reporting system (SAS RRG inspired)
from .report_builder import ReportBuilder
from .table_specification import TableSpecification
from .table_result import TableResult, ReportResult

# Table generators
try:
    from .generators import (
        TableGeneratorFactory,
        BaseTableGenerator,
        DemographicsGenerator,
        DispositionGenerator,
        AESummaryGenerator,
        AEDetailGenerator,
        EfficacyGenerator,
        LaboratoryGenerator,
        SurvivalGenerator
    )
except ImportError:
    # Generators not yet implemented - will be created as needed
    pass

# Clinical study reports class (legacy)
from .clinical_study_reports import ClinicalStudyReports

__all__ = [
    # RTF table functions (r2rtf compatible)
    "RTFTable",
    "rtf_page_header",
    "rtf_page_footer", 
    "rtf_title",
    "rtf_subline",
    "rtf_colheader",
    "rtf_body",
    "rtf_footnote",
    "rtf_source",
    "rtf_page",
    "rtf_encode",
    "write_rtf",
    
    # Functional reporting system
    "ReportBuilder",
    "TableSpecification",
    "TableResult",
    "ReportResult",
    
    # Table generators
    "TableGeneratorFactory",
    "BaseTableGenerator",
    
    # Legacy clinical study reports
    "ClinicalStudyReports"
]

# Version and metadata
__version__ = "1.0.0"
__author__ = "py4csr Development Team"
__description__ = "Clinical Study Report generation for Python"

def get_version():
    """Get the current version of py4csr reporting module."""
    return __version__

def list_available_generators():
    """List all available table generators."""
    try:
        return list(TableGeneratorFactory._generators.keys())
    except:
        return [
            'demographics', 'disposition', 'ae_summary', 'ae_detail',
            'efficacy', 'laboratory', 'survival', 'vital_signs',
            'concomitant_meds', 'medical_history', 'exposure'
        ]

def create_report_builder(config_type="clinical_standard"):
    """
    Create a ReportBuilder with specified configuration.
    
    Parameters
    ----------
    config_type : str
        Type of configuration to use:
        - 'clinical_standard': Standard clinical trial configuration
        - 'regulatory': Enhanced regulatory submission configuration
        - 'oncology': Oncology-specific configuration
    
    Returns
    -------
    ReportBuilder
        Configured report builder instance
    
    Examples
    --------
    >>> from py4csr.reporting import create_report_builder
    >>> builder = create_report_builder("regulatory")
    >>> report = (builder
    ...     .init_study(uri="STUDY001", title="My Study")
    ...     .add_dataset(adsl, "adsl", "subject_level")
    ...     .add_demographics_table()
    ...     .generate_all()
    ...     .finalize())
    """
    from ..config import ReportConfig
    
    if config_type == "clinical_standard":
        config = ReportConfig.clinical_standard()
    elif config_type == "regulatory":
        from ..config.clinical_standard import get_regulatory_submission_config
        config = get_regulatory_submission_config()
    elif config_type == "oncology":
        from ..config.clinical_standard import get_oncology_config
        config = get_oncology_config()
    else:
        raise ValueError(f"Unknown config type: {config_type}")
    
    return ReportBuilder(config)

def quick_demographics_table(adsl, output_path="demographics.rtf", **kwargs):
    """
    Quick generation of demographics table.
    
    Parameters
    ----------
    adsl : pd.DataFrame
        Subject-level analysis dataset
    output_path : str
        Output file path
    **kwargs
        Additional parameters for table generation
    
    Returns
    -------
    TableResult
        Generated table result
    
    Examples
    --------
    >>> from py4csr.reporting import quick_demographics_table
    >>> result = quick_demographics_table(adsl, "my_demographics.rtf")
    """
    builder = create_report_builder()
    report = (builder
        .init_study(uri="QUICK_DEMO", title="Quick Demographics Table")
        .add_dataset(adsl, "adsl", "subject_level")
        .define_populations(safety="SAFFL=='Y'" if 'SAFFL' in adsl.columns else "True")
        .define_treatments(var="TRT01P" if 'TRT01P' in adsl.columns else adsl.columns[0])
        .add_demographics_table(**kwargs)
        .generate_all(str(Path(output_path).parent))
        .finalize()
    )
    
    return report

def quick_ae_summary_table(adae, output_path="ae_summary.rtf", **kwargs):
    """
    Quick generation of AE summary table.
    
    Parameters
    ----------
    adae : pd.DataFrame
        Adverse events analysis dataset
    output_path : str
        Output file path
    **kwargs
        Additional parameters for table generation
    
    Returns
    -------
    TableResult
        Generated table result
    """
    builder = create_report_builder()
    report = (builder
        .init_study(uri="QUICK_AE", title="Quick AE Summary Table")
        .add_dataset(adae, "adae", "adverse_events")
        .define_populations(safety="SAFFL=='Y'" if 'SAFFL' in adae.columns else "True")
        .define_treatments(var="TRT01P" if 'TRT01P' in adae.columns else "TRT01A")
        .add_ae_summary_table(**kwargs)
        .generate_all(str(Path(output_path).parent))
        .finalize()
    )
    
    return report

# Import Path for quick functions
from pathlib import Path 