"""
Basic usage example for py4csr package.

This script demonstrates how to use the py4csr package to create
clinical study report tables similar to the R r4csr package.
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Import py4csr functions
import sys
sys.path.append('..')

from py4csr.reporting.rtf_table import RTFTable
from py4csr.analysis.utils import format_mean_sd, format_pvalue
from py4csr.analysis.demographics import create_demographics_table


def create_sample_data():
    """Create sample clinical data for demonstration."""
    
    np.random.seed(42)
    n_subjects = 200
    
    # Create ADSL-like dataset
    adsl = pd.DataFrame({
        'USUBJID': [f"SUB-{i:03d}" for i in range(1, n_subjects + 1)],
        'TRT01P': np.random.choice(['Placebo', 'Treatment A', 'Treatment B'], n_subjects),
        'AGE': np.random.normal(65, 12, n_subjects).round().astype(int),
        'SEX': np.random.choice(['M', 'F'], n_subjects),
        'RACE': np.random.choice(['White', 'Black or African American', 'Asian'], 
                                n_subjects, p=[0.7, 0.2, 0.1]),
        'EFFFL': np.random.choice(['Y', 'N'], n_subjects, p=[0.9, 0.1])
    })
    
    # Ensure age is within reasonable bounds
    adsl['AGE'] = np.clip(adsl['AGE'], 18, 90)
    
    return adsl


def example_rtf_table():
    """Demonstrate RTF table creation."""
    
    print("Creating RTF table example...")
    
    # Create sample adverse events data
    ae_data = pd.DataFrame({
        'Adverse Event': ['Headache', 'Nausea', 'Fatigue', 'Dizziness'],
        'Placebo': ['5 (12.5%)', '3 (7.5%)', '8 (20.0%)', '2 (5.0%)'],
        'Treatment A': ['8 (18.2%)', '6 (13.6%)', '12 (27.3%)', '4 (9.1%)'],
        'Treatment B': ['6 (15.0%)', '4 (10.0%)', '10 (25.0%)', '3 (7.5%)']
    })
    
    # Create RTF table
    rtf_table = (RTFTable(ae_data)
                 .rtf_title("Adverse Events Summary", 
                           "(Safety Population)")
                 .rtf_colheader("Adverse Event | Placebo (N=40) | Treatment A (N=44) | Treatment B (N=40)",
                               col_rel_width=[3, 2, 2, 2])
                 .rtf_body(col_rel_width=[3, 2, 2, 2],
                          text_justification=['l', 'c', 'c', 'c'])
                 .rtf_footnote("Percentages are based on the number of subjects in each treatment group.")
                 .rtf_source("ADAE dataset"))
    
    # Ensure output directory exists
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Write RTF file
    rtf_table.write_rtf("output/ae_summary.rtf")
    print("RTF table saved to: output/ae_summary.rtf")


def example_demographics_table():
    """Demonstrate demographics table creation."""
    
    print("\nCreating demographics table example...")
    
    # Create sample data
    adsl = create_sample_data()
    
    try:
        # Create demographics table
        demographics = create_demographics_table(
            data=adsl,
            treatment_var="TRT01P",
            variables=["AGE", "SEX", "RACE"],
            categorical_vars=["SEX", "RACE"],
            continuous_vars=["AGE"]
        )
        
        print("\nDemographics table created:")
        print(demographics.to_string(index=False))
        
        # Convert to RTF
        rtf_table = (RTFTable(demographics)
                     .rtf_title("Baseline Characteristics of Participants",
                               "(All Participants Randomized)")
                     .rtf_colheader(" | | Placebo | Treatment A | Treatment B | P-value",
                                   col_rel_width=[2.5, 1, 1, 1, 1, 1])
                     .rtf_body(col_rel_width=[2.5, 1, 1, 1, 1, 1],
                              text_justification=['l', 'l', 'c', 'c', 'c', 'c'])
                     .rtf_footnote("P-values from chi-square test for categorical variables and ANOVA for continuous variables."))
        
        # Ensure output directory exists
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        rtf_table.write_rtf("output/demographics.rtf")
        print("Demographics RTF table saved to: output/demographics.rtf")
        
    except Exception as e:
        print(f"Error creating demographics table: {e}")
        print("Creating a simpler example instead...")
        
        # Create a simpler manual table
        simple_demographics = pd.DataFrame({
            'Variable': ['Age', '', 'Sex', 'Male', 'Female', 'Race', 'White', 'Black or African American', 'Asian'],
            'Category': ['', 'Mean (SD)', '', 'n (%)', 'n (%)', '', 'n (%)', 'n (%)', 'n (%)'],
            'Placebo': ['', '64.2 (11.8)', '', '32 (48.5%)', '34 (51.5%)', '', '45 (68.2%)', '15 (22.7%)', '6 (9.1%)'],
            'Treatment A': ['', '65.8 (12.1)', '', '38 (52.8%)', '34 (47.2%)', '', '51 (70.8%)', '14 (19.4%)', '7 (9.7%)'],
            'Treatment B': ['', '63.9 (11.5)', '', '35 (55.6%)', '28 (44.4%)', '', '42 (66.7%)', '14 (22.2%)', '7 (11.1%)']
        })
        
        rtf_table = (RTFTable(simple_demographics)
                     .rtf_title("Baseline Characteristics of Participants",
                               "(All Participants Randomized)")
                     .rtf_colheader("Variable | Category | Placebo (N=66) | Treatment A (N=72) | Treatment B (N=63)",
                                   col_rel_width=[2.5, 1.5, 1.5, 1.5, 1.5])
                     .rtf_body(col_rel_width=[2.5, 1.5, 1.5, 1.5, 1.5],
                              text_justification=['l', 'l', 'c', 'c', 'c'])
                     .rtf_footnote("Values are presented as mean (standard deviation) for continuous variables and n (%) for categorical variables."))
        
        rtf_table.write_rtf("output/demographics_simple.rtf")
        print("Simple demographics RTF table saved to: output/demographics_simple.rtf")


def example_utility_functions():
    """Demonstrate utility functions."""
    
    print("\nDemonstrating utility functions:")
    
    # Format mean and SD
    mean_sd = format_mean_sd(12.5, 3.24)
    print(f"Mean (SD): {mean_sd}")
    
    # Format p-value
    p_val = format_pvalue(0.0234)
    print(f"P-value: {p_val}")
    
    p_val_small = format_pvalue(0.0001)
    print(f"Small P-value: {p_val_small}")


def main():
    """Run all examples."""
    
    print("=" * 60)
    print("PY4CSR - Python for Clinical Study Reports")
    print("Basic Usage Examples")
    print("=" * 60)
    
    # Run examples
    example_utility_functions()
    example_rtf_table()
    example_demographics_table()
    
    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("Check the 'output' directory for generated RTF files.")
    print("=" * 60)


if __name__ == "__main__":
    main() 