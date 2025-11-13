"""
py4csr Clinical Plotting Engine - Streamlined Version
=====================================================

Comprehensive clinical plotting engine optimized for professional clinical use.
All functionality consolidated into a single, efficient module.

Features:
- Complete professional clinical plot implementations
- Full SAS GPROC macro compatibility
- Professional regulatory-quality outputs (PNG, RTF, HTML)
- Complete RTF generation with embedded plots
- Advanced statistical computations
- Streamlined, overlap-free architecture

Author: py4csr Development Team
"""

# Version and metadata
__version__ = "4.0.0"
__author__ = "py4csr Development Team"
__description__ = "Consolidated Clinical Plotting Engine - No Overlaps"

# Import all functionality from the main comprehensive engine
from .comprehensive_clinical_plots import (  # Main interfaces; Quick functions for LLM agents; Legacy compatibility functions; Utility functions; Basic plot functions; SAS compatibility functions; FDA-compliant parameter classes; Dual output functions
    EnhancedPlotConfig,
    FDACompliantPlotParameters,
    OutputFormat,
    PlotConfig,
    PlotOutput,
    PlotType,
    SASDataSkin,
    SASLegendPosition,
    SASMacroType,
    _create_clinical_boxplot,
    _create_clinical_lineplot,
    apply_clinical_style,
    apply_fda_clinical_style,
    calculate_fda_statistics,
    calculate_statistics,
    clinical_boxplot,
    clinical_forest_plot,
    clinical_km_plot,
    clinical_lineplot,
    create_clinical_plot,
    create_clinical_plot_dual,
    create_enhanced_html,
    create_fda_dual_output_boxplot,
    create_fda_dual_output_lineplot,
    create_fda_dual_output_waterfall,
    gbox2_python,
    get_clinical_colors,
    get_fda_clinical_colors,
    gline2_python,
    gwaterfall2_python,
    quick_boxplot,
    quick_boxplot_dual,
    quick_forest_plot,
    quick_km_plot,
    quick_lineplot,
    quick_lineplot_dual,
    save_dual_outputs,
    validate_data,
)

# Import plot result handling
from .plot_result import PlotCollection, PlotResult

# Export main functions
__all__ = [
    # Main interfaces
    "create_clinical_plot",
    "create_clinical_plot_dual",
    "PlotConfig",
    "EnhancedPlotConfig",
    "PlotType",
    "OutputFormat",
    "PlotOutput",
    # Quick functions for LLM agents
    "quick_boxplot",
    "quick_lineplot",
    "quick_boxplot_dual",
    "quick_lineplot_dual",
    "quick_km_plot",
    "quick_forest_plot",
    # Legacy compatibility
    "_create_clinical_lineplot",
    "_create_clinical_boxplot",
    # Utility functions
    "validate_data",
    "get_clinical_colors",
    "get_fda_clinical_colors",
    "apply_clinical_style",
    "apply_fda_clinical_style",
    "calculate_statistics",
    "calculate_fda_statistics",
    # Basic plot functions
    "clinical_boxplot",
    "clinical_lineplot",
    "clinical_km_plot",
    "clinical_forest_plot",
    # SAS compatibility
    "gbox2_python",
    "gline2_python",
    "gwaterfall2_python",
    # FDA compliance
    "FDACompliantPlotParameters",
    "SASMacroType",
    "SASDataSkin",
    "SASLegendPosition",
    # Dual output
    "create_fda_dual_output_boxplot",
    "create_fda_dual_output_lineplot",
    "create_fda_dual_output_waterfall",
    "save_dual_outputs",
    "create_enhanced_html",
    # Result handling
    "PlotResult",
    "PlotCollection",
]


# Status information
def get_system_status():
    """Get comprehensive system status"""
    status = {
        "version": __version__,
        "description": __description__,
        "architecture": "Consolidated Single-Module",
        "core_plotting": True,
        "rtf_generator": True,
        "html_interactive": True,
        "overlap_free": True,
        "features": [
            "Consolidated Architecture (No Overlaps)",
            "Kaplan-Meier Survival Analysis",
            "Forest Plot Subgroup Analysis",
            "Enhanced Clinical Boxplots",
            "Interactive HTML Output",
            "Professional RTF Documents",
            "Complete SAS Compatibility",
            "FDA-Compliant Parameters",
            "Dual Output Strategy",
            "Streamlined API",
        ],
    }
    return status


def print_system_status():
    """Print formatted system status"""
    status = get_system_status()

    print(f"py4csr Clinical Plotting Engine v{status['version']}")
    print(f"{status['description']}")
    print(f"Architecture: {status['architecture']}")
    print("-" * 60)

    print("✅ Features Available:")
    for feature in status["features"]:
        print(f"  • {feature}")

    print(f"\n🎯 Overlap-Free: {status['overlap_free']}")
    print("📦 Single Module: comprehensive_clinical_plots.py")
