#!/usr/bin/env python3
"""
py4csr Complete Output Showcase

This script demonstrates the comprehensive range of clinical outputs that py4csr
can generate, showcasing all the sample outputs available in the sample_outputs directory.

FEATURED OUTPUTS:
================

📊 CLINICAL TABLES (7 Examples):
- Demographics & Baseline Characteristics
- Adverse Events Summary  
- Vital Signs Analysis
- Subject Disposition
- Drug Exposure Analysis
- Laboratory Chemistry
- Efficacy Response Analysis

📈 CLINICAL FIGURES (8 Examples):
- Kaplan-Meier Survival Plots (RTF + Interactive HTML)
- Forest Plot Analysis (RTF + Interactive HTML)
- Box Plot Distributions (RTF + Interactive HTML)
- Line Plot Trends (RTF + Interactive HTML)

📋 CLINICAL LISTINGS (1 Example):
- Adverse Event Deaths

All outputs demonstrate regulatory-submission quality formatting using synthetic data.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add py4csr to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def showcase_sample_outputs():
    """Display information about all available sample outputs."""
    
    print("🎯 py4csr Complete Output Showcase")
    print("=" * 60)
    print("Demonstrating comprehensive clinical reporting capabilities")
    print("All outputs generated from synthetic data - regulatory ready!")
    print()
    
    # Define sample outputs structure
    sample_outputs = {
        "📊 Clinical Tables": {
            "t_dem.rtf": "Demographics & Baseline Characteristics",
            "t_ae_sum.rtf": "Adverse Events Summary",
            "t_vs_sum.rtf": "Vital Signs Analysis", 
            "t_disp.rtf": "Subject Disposition",
            "t_exposure.rtf": "Drug Exposure Analysis",
            "t_lb_sum_chem.rtf": "Laboratory Chemistry",
            "t_eff_response.rtf": "Efficacy Response Analysis"
        },
        "📈 Clinical Figures (RTF)": {
            "km_enhanced_example.rtf": "Kaplan-Meier Survival Analysis",
            "forest_enhanced_example.rtf": "Forest Plot Analysis",
            "box_plot_clinical_example.rtf": "Box Plot Distributions",
            "line_plot_clinical_example.rtf": "Line Plot Trends"
        },
        "🌐 Interactive HTML Plots": {
            "km_enhanced_example.html": "Kaplan-Meier (Interactive)",
            "forest_enhanced_example.html": "Forest Plot (Interactive)",
            "box_plot_clinical_example.html": "Box Plot (Interactive)",
            "line_plot_clinical_example.html": "Line Plot (Interactive)"
        },
        "📋 Clinical Listings": {
            "l_ae_death.rtf": "Adverse Event Deaths"
        }
    }
    
    # Display each category
    for category, outputs in sample_outputs.items():
        print(f"{category}")
        print("-" * 40)
        
        for filename, description in outputs.items():
            # Determine the correct subdirectory
            if category == "📊 Clinical Tables":
                subdir = "tables"
            elif category in ["📈 Clinical Figures (RTF)", "🌐 Interactive HTML Plots"]:
                subdir = "figures"
            elif category == "📋 Clinical Listings":
                subdir = "listings"

            file_path = Path("examples/sample_outputs") / subdir / filename
            if file_path.exists():
                size_kb = file_path.stat().st_size / 1024
                status = f"✅ {size_kb:.1f}KB"
            else:
                status = "❌ Missing"
            
            print(f"  {filename:<30} | {description:<35} | {status}")
        print()
    
    # Summary statistics
    total_files = sum(len(outputs) for outputs in sample_outputs.values())
    print(f"📈 SHOWCASE SUMMARY")
    print("-" * 20)
    print(f"Total Sample Outputs: {total_files}")
    print(f"Clinical Tables: {len(sample_outputs['📊 Clinical Tables'])}")
    print(f"Clinical Figures (RTF): {len(sample_outputs['📈 Clinical Figures (RTF)'])}")
    print(f"Interactive HTML Plots: {len(sample_outputs['🌐 Interactive HTML Plots'])}")
    print(f"Clinical Listings: {len(sample_outputs['📋 Clinical Listings'])}")
    print()
    
    print("🌟 UNIQUE FEATURE - INTERACTIVE HTML PLOTS:")
    print("-" * 45)
    print("✅ Zoom and Pan - Explore data in detail")
    print("✅ Hover Tooltips - See exact values on mouse-over")
    print("✅ Legend Filtering - Click to show/hide treatment groups")
    print("✅ Responsive Design - Works on desktop, tablet, mobile")
    print("✅ Export Options - Save as PNG, PDF, or SVG")
    print()

    print("🔍 HOW TO EXPLORE:")
    print("-" * 20)
    print("1. Navigate to examples/sample_outputs/")
    print("2. Open .rtf files for regulatory-ready outputs")
    print("3. Open .html files for interactive exploration")
    print("4. Review README.md for detailed descriptions")
    print("5. Run examples to generate similar outputs with your data")
    print()
    
    print("🚀 GETTING STARTED:")
    print("-" * 20)
    print("```python")
    print("from py4csr.functional import ReportSession")
    print("")
    print("# Create professional clinical reports")
    print("session = (ReportSession()")
    print("    .init_study('YOUR-STUDY', 'Study Title')")
    print("    .load_datasets(your_data)")
    print("    .add_demographics_table()")
    print("    .add_ae_summary()")
    print("    .generate_all()")
    print(")")
    print("```")
    print()
    
    print("✨ REGULATORY COMPLIANCE:")
    print("-" * 25)
    print("✅ ICH E3 Guidelines")
    print("✅ FDA Submission Standards") 
    print("✅ CDISC Compliance")
    print("✅ Professional RTF Formatting")
    print("✅ Statistical Analysis Standards")
    print()
    
    print("🎉 py4csr - Professional Clinical Reporting Made Easy!")

def demonstrate_output_types():
    """Demonstrate the types of analyses py4csr can perform."""
    
    print("\n" + "=" * 60)
    print("🔬 CLINICAL ANALYSIS CAPABILITIES")
    print("=" * 60)
    
    analysis_types = {
        "Safety Analysis": [
            "Adverse Events by System Organ Class",
            "Serious Adverse Events",
            "Deaths and Discontinuations",
            "Laboratory Safety Analysis",
            "Vital Signs Safety Assessment"
        ],
        "Efficacy Analysis": [
            "Primary Endpoint Analysis",
            "Secondary Endpoint Analysis", 
            "Responder Analysis",
            "Time-to-Event Analysis",
            "Subgroup Analysis"
        ],
        "Descriptive Analysis": [
            "Demographics and Baseline",
            "Medical History",
            "Concomitant Medications",
            "Subject Disposition",
            "Protocol Deviations"
        ],
        "Statistical Visualizations": [
            "Kaplan-Meier Survival Curves",
            "Forest Plots for Subgroups",
            "Box Plots for Distributions",
            "Line Plots for Trends",
            "Scatter Plots for Correlations"
        ]
    }
    
    for analysis_type, capabilities in analysis_types.items():
        print(f"\n📊 {analysis_type}")
        print("-" * 30)
        for capability in capabilities:
            print(f"  ✅ {capability}")
    
    print(f"\n🎯 Total Capabilities: {sum(len(caps) for caps in analysis_types.values())} analysis types")

def main():
    """Main showcase function."""
    
    try:
        showcase_sample_outputs()
        demonstrate_output_types()
        
        print("\n" + "🌟" * 20)
        print("SUCCESS: py4csr Output Showcase Complete!")
        print("Explore examples/sample_outputs/ to see all professional outputs")
        print("🌟" * 20)
        
    except Exception as e:
        print(f"\n❌ Error during showcase: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
