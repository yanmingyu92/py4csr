#!/usr/bin/env python3
"""
RTF Formatting Example for py4csr

This example demonstrates how to create professional RTF tables
for clinical reporting using py4csr's RTF formatting capabilities.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os

# Add py4csr to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from py4csr.tables import ClinicalRTFFormatter, create_clinical_rtf_table


def create_sample_demographics():
    """Create sample demographics data for demonstration."""
    np.random.seed(42)
    
    treatments = ['Placebo', 'Xanomeline Low Dose', 'Xanomeline High Dose']
    n_subjects = [86, 84, 84]
    
    demographics = pd.DataFrame({
        'Treatment': treatments,
        'N': n_subjects,
        'Age (years)': [
            '75.2 (8.59)',
            '75.7 (8.29)', 
            '74.4 (7.89)'
        ],
        'Female n (%)': [
            '44 (51.2)',
            '46 (54.8)',
            '50 (59.5)'
        ],
        'Race - White n (%)': [
            '78 (90.7)',
            '76 (90.5)',
            '76 (90.5)'
        ],
        'Weight (kg)': [
            '65.8 (11.07)',
            '67.3 (15.58)',
            '65.1 (14.13)'
        ]
    })
    
    return demographics


def create_sample_adverse_events():
    """Create sample adverse events data for demonstration."""
    treatments = ['Placebo', 'Xanomeline Low Dose', 'Xanomeline High Dose']
    
    ae_data = pd.DataFrame({
        'System Organ Class': [
            'Any adverse event',
            'General disorders and administration site conditions',
            'Skin and subcutaneous tissue disorders',
            'Nervous system disorders',
            'Gastrointestinal disorders',
            'Infections and infestations'
        ],
        'Placebo (N=86)': [
            '69 (80.2)',
            '21 (24.4)',
            '20 (23.3)',
            '7 (8.1)',
            '6 (7.0)',
            '5 (5.8)'
        ],
        'Xanomeline Low Dose (N=84)': [
            '77 (91.7)',
            '21 (25.0)',
            '19 (22.6)',
            '7 (8.3)',
            '8 (9.5)',
            '4 (4.8)'
        ],
        'Xanomeline High Dose (N=84)': [
            '79 (94.0)',
            '20 (23.8)',
            '20 (23.8)',
            '7 (8.3)',
            '7 (8.3)',
            '6 (7.1)'
        ]
    })
    
    return ae_data


def create_sample_laboratory():
    """Create sample laboratory data for demonstration."""
    lab_data = pd.DataFrame({
        'Parameter': [
            'Hemoglobin (g/dL)',
            'Hematocrit (%)',
            'White Blood Cell Count (10^9/L)',
            'Platelet Count (10^9/L)',
            'Glucose (mg/dL)',
            'Creatinine (mg/dL)'
        ],
        'Placebo (N=86)': [
            '13.2 (1.45)',
            '39.8 (4.12)',
            '6.8 (2.14)',
            '268.5 (78.9)',
            '98.7 (15.2)',
            '0.89 (0.21)'
        ],
        'Xanomeline Low Dose (N=84)': [
            '13.1 (1.38)',
            '39.5 (3.98)',
            '6.9 (2.08)',
            '271.2 (82.1)',
            '99.1 (16.8)',
            '0.91 (0.19)'
        ],
        'Xanomeline High Dose (N=84)': [
            '13.0 (1.42)',
            '39.2 (4.05)',
            '7.1 (2.21)',
            '265.8 (79.4)',
            '97.8 (14.9)',
            '0.88 (0.20)'
        ]
    })
    
    return lab_data


def main():
    """Main function to demonstrate RTF formatting capabilities."""
    print("py4csr RTF Formatting Example")
    print("=" * 50)
    
    # Create output directory
    output_dir = Path("rtf_examples_output")
    output_dir.mkdir(exist_ok=True)
    
    # Initialize RTF formatter
    formatter = ClinicalRTFFormatter()
    
    # Example 1: Demographics Table
    print("\n1. Creating Demographics Table...")
    demographics = create_sample_demographics()
    
    demographics_rtf = formatter.format_clinical_table(
        df=demographics,
        table_number="14.1.1",
        table_title="Demographics and Baseline Characteristics",
        population="Safety Analysis Population",
        study_info="CDISCPILOT01",
        footnotes=[
            "Age and weight presented as mean (standard deviation)",
            "Percentages based on treatment group N",
            "Race categories based on investigator assessment"
        ],
        output_file=output_dir / "demographics_table.rtf"
    )
    
    print(f"   ✓ Demographics table saved to {output_dir}/demographics_table.rtf")
    
    # Example 2: Adverse Events Table
    print("\n2. Creating Adverse Events Table...")
    ae_data = create_sample_adverse_events()
    
    ae_rtf = formatter.format_clinical_table(
        df=ae_data,
        table_number="14.3.1",
        table_title="Overview of Adverse Events by System Organ Class",
        population="Safety Analysis Population", 
        study_info="CDISCPILOT01",
        footnotes=[
            "AE = Adverse Event",
            "System Organ Class based on MedDRA version 24.1",
            "Subjects counted once per system organ class",
            "Percentages based on number of subjects in treatment group"
        ],
        output_file=output_dir / "adverse_events_table.rtf"
    )
    
    print(f"   ✓ Adverse events table saved to {output_dir}/adverse_events_table.rtf")
    
    # Example 3: Laboratory Table
    print("\n3. Creating Laboratory Table...")
    lab_data = create_sample_laboratory()
    
    lab_rtf = formatter.format_clinical_table(
        df=lab_data,
        table_number="14.2.1",
        table_title="Laboratory Parameters - Summary Statistics",
        population="Safety Analysis Population",
        study_info="CDISCPILOT01",
        footnotes=[
            "Values presented as mean (standard deviation)",
            "Laboratory values at baseline visit",
            "Normal ranges: Hemoglobin 12.0-15.5 g/dL, Hematocrit 36-46%",
            "Missing values excluded from calculations"
        ],
        output_file=output_dir / "laboratory_table.rtf"
    )
    
    print(f"   ✓ Laboratory table saved to {output_dir}/laboratory_table.rtf")
    
    # Example 4: Using convenience function
    print("\n4. Creating table using convenience function...")
    
    # Create simple efficacy data
    efficacy_data = pd.DataFrame({
        'Endpoint': ['Primary Efficacy', 'Secondary Efficacy 1', 'Secondary Efficacy 2'],
        'Placebo': ['12.3 (4.5)', '8.7 (3.2)', '15.6 (6.1)'],
        'Xanomeline Low': ['14.8 (5.1)', '10.2 (3.8)', '18.3 (6.9)'],
        'Xanomeline High': ['16.2 (4.9)', '11.5 (4.1)', '19.7 (7.2)'],
        'P-value': ['0.0234', '0.0456', '0.0123']
    })
    
    success = create_clinical_rtf_table(
        df=efficacy_data,
        table_number="14.4.1",
        table_title="Efficacy Endpoints - Change from Baseline",
        output_file=output_dir / "efficacy_table.rtf",
        population="Efficacy Analysis Population",
        study_info="CDISCPILOT01",
        footnotes=[
            "Values presented as least squares mean (standard error)",
            "P-values from ANCOVA model with treatment and baseline as covariates",
            "Significant results (p<0.05) highlighted"
        ]
    )
    
    if success:
        print(f"   ✓ Efficacy table saved to {output_dir}/efficacy_table.rtf")
    else:
        print("   ✗ Error creating efficacy table")
    
    # Example 5: Custom formatting options
    print("\n5. Creating table with custom formatting...")
    
    # Create a simple summary table
    summary_data = pd.DataFrame({
        'Category': ['Subjects enrolled', 'Subjects completed', 'Subjects discontinued'],
        'Count': [254, 238, 16],
        'Percentage': ['100.0%', '93.7%', '6.3%']
    })
    
    # Use basic RTF formatting
    custom_rtf = formatter.format_table_to_rtf(
        df=summary_data,
        title="Table 14.0.1",
        subtitle="Subject Disposition\nSafety Analysis Population\nStudy CDISCPILOT01",
        footnotes=[
            "Disposition based on last known status",
            "Percentages based on enrolled population"
        ],
        output_file=output_dir / "disposition_table.rtf"
    )
    
    print(f"   ✓ Disposition table saved to {output_dir}/disposition_table.rtf")
    
    # Summary
    print(f"\n" + "=" * 50)
    print("RTF Formatting Example Complete!")
    print(f"Generated {len(list(output_dir.glob('*.rtf')))} RTF tables in {output_dir}/")
    print("\nFiles created:")
    for rtf_file in sorted(output_dir.glob('*.rtf')):
        print(f"  - {rtf_file.name}")
    
    print(f"\nTo view the RTF files, open them in:")
    print("  - Microsoft Word")
    print("  - LibreOffice Writer") 
    print("  - Any RTF-compatible word processor")
    
    print(f"\nExample RTF content preview:")
    print("-" * 30)
    print(demographics_rtf[:500] + "...")


if __name__ == "__main__":
    main() 