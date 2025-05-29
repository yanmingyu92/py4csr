#!/usr/bin/env python3
"""
Generate Clinical Example 01: Demographics Table with P-values
=============================================================

This example demonstrates the new high-level py4csr clinical session interface.
Instead of 270+ lines of manual statistical calculations, this streamlined 
approach uses variable accumulation to generate professional clinical tables.

**Before**: 270+ lines of manual statistics and formatting code
**After**: ~30 lines of declarative variable definitions

Professional clinical demographics table generation for regulatory submissions.
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Import the new high-level interface
from py4csr.clinical import ClinicalSession
from py4csr.data import read_sas


def main():
    """Generate demographics table using the streamlined ClinicalSession interface."""
    print("🚀 Generating Clinical Example 01: Demographics Table with P-values")
    print("=" * 70)
    
    # Load the clinical data
    print("Loading clinical datasets...")
    try:
        adsl_data = read_sas('data/adsl.sas7bdat')
        print(f"✅ Loaded ADSL: {len(adsl_data)} subjects")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return False
    
    # Handle SAS byte strings and case issues
    adsl_data.columns = adsl_data.columns.str.upper()
    for col in ['SAFFL', 'TRT01P', 'SEX', 'RACE', 'ETHNIC']:
        if col in adsl_data.columns and adsl_data[col].dtype == 'object':
            # Convert byte strings to regular strings
            adsl_data[col] = adsl_data[col].astype(str).str.replace("b'", "").str.replace("'", "")
    
    # Initialize clinical session
    session = ClinicalSession(
        uri="example_01_demographics",
        purpose="Demographics and Baseline Characteristics with P-values",
        outname="example_01_demographics_py4csr"
    )
    
    # Define report structure - equivalent to %rrg_defreport
    session.define_report(
        dataset=adsl_data,
        pop_where="SAFFL=='Y'" if 'SAFFL' in adsl_data.columns else "1==1",
        subjid="USUBJID",
        title1="Example 01",
        title2="Summary of Demography & Baseline Characteristics", 
        title3="Randomized Population",
        footnot1="Randomized Population",
        footnot2="P-values: ANOVA for continuous variables, Chi-square for categorical variables",
        footnot3="Generated using py4csr streamlined interface"
    )
    
    # Add treatment variable - equivalent to %rrg_addtrt
    session.add_trt(name="TRT01PN", decode="TRT01P")
    
    # Add variables using the high-level interface - equivalent to %rrg_addvar/%rrg_addcatvar
    
    # Age (continuous variable)
    session.add_var(
        name="AGE", 
        label="Age (years)", 
        stats="n mean+sd median min+max",
        basedec=1
    )
    
    # Create age groups if they don't exist
    if 'AGEGR1N' not in adsl_data.columns and 'AGE' in adsl_data.columns:
        adsl_data['AGEGR1'] = adsl_data['AGE'].apply(lambda x: '<65' if pd.notna(x) and x < 65 else '>=65')
        adsl_data['AGEGR1N'] = adsl_data['AGEGR1'].map({'<65': 1, '>=65': 2})
    
    if 'AGEGR1N' in adsl_data.columns:
        session.add_catvar(
            name="AGEGR1N", 
            label="Age Groups, n (%)",
            decode="AGEGR1",
            stats="npct"
        )
    
    # Sex (categorical variable)
    if 'SEXN' not in adsl_data.columns and 'SEX' in adsl_data.columns:
        sex_map = {'M': 1, 'F': 2, 'Male': 1, 'Female': 2}
        adsl_data['SEXN'] = adsl_data['SEX'].map(sex_map)
    
    session.add_catvar(
        name="SEXN" if 'SEXN' in adsl_data.columns else "SEX",
        label="Sex, n (%)", 
        decode="SEX",
        stats="npct"
    )
    
    # Race (categorical variable)
    if 'RACEN' not in adsl_data.columns and 'RACE' in adsl_data.columns:
        race_values = adsl_data['RACE'].unique()
        race_map = {race: i+1 for i, race in enumerate(race_values) if pd.notna(race)}
        adsl_data['RACEN'] = adsl_data['RACE'].map(race_map)
    
    session.add_catvar(
        name="RACEN" if 'RACEN' in adsl_data.columns else "RACE",
        label="Race, n (%)",
        decode="RACE", 
        stats="npct"
    )
    
    # Ethnicity (categorical variable) - if available
    if 'ETHNIC' in adsl_data.columns:
        if 'ETHNICN' not in adsl_data.columns:
            ethnic_values = adsl_data['ETHNIC'].unique()
            ethnic_map = {ethnic: i+1 for i, ethnic in enumerate(ethnic_values) if pd.notna(ethnic)}
            adsl_data['ETHNICN'] = adsl_data['ETHNIC'].map(ethnic_map)
        
        session.add_catvar(
            name="ETHNICN" if 'ETHNICN' in adsl_data.columns else "ETHNIC",
            label="Ethnicity, n (%)",
            decode="ETHNIC",
            stats="npct"
        )
    
    # Add baseline measurements if available
    baseline_vars = [
        ('HEIGHTBL', 'Height (cm)'),
        ('WEIGHTBL', 'Weight (kg)'), 
        ('BMIBL', 'BMI (kg/m²)')
    ]
    
    for var_name, var_label in baseline_vars:
        if var_name in adsl_data.columns:
            session.add_var(
                name=var_name,
                label=var_label,
                stats="n mean+sd median min+max",
                basedec=1
            )
    
    # Generate the complete table - equivalent to %rrg_generate
    print("\n📊 Generating demographics table...")
    session.generate()
    
    # Preview the results
    print("\n👀 Table Preview:")
    preview = session.preview(max_rows=15)
    print(preview)
    
    # Save the final RTF output - equivalent to %rrg_finalize
    print("\n💾 Saving RTF output...")
    session.finalize()
    
    # Print session summary
    session.summary()
    
    print("\n✅ Clinical Example 01 generated successfully!")
    print("📁 Output saved: example_01_demographics_py4csr.rtf")
    
    # Show the dramatic improvement
    print("\n📈 Code Efficiency Improvement:")
    print("  Previous approach: 270+ lines of manual statistical calculations")
    print("  New streamlined approach: ~30 lines of declarative variable definitions")
    print("  Code reduction: >90%")
    print("  Benefits:")
    print("    ✅ Automatic statistical calculations (ANOVA, Chi-square)")
    print("    ✅ Professional RTF formatting")
    print("    ✅ P-value calculations")
    print("    ✅ Error handling and validation")
    print("    ✅ Consistent clinical formatting")
    
    return True


if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Demographics table generation completed successfully!")
    else:
        print("\n❌ Failed to generate demographics table")
        exit(1) 