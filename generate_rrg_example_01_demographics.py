#!/usr/bin/env python3
r"""
Generate Clinical Example 01: Demographics Table with P-values
=============================================================

This script generates a demographics table following professional clinical 
reporting standards, using the py4csr system with real clinical data.

Professional clinical demographics table generation for regulatory submissions.
"""

import pandas as pd
import numpy as np
from scipy import stats
import os
import sys
from datetime import datetime

# Import py4csr functions
from py4csr.tables import create_sasshiato_table, save_sasshiato_rtf
from py4csr.data import read_sas

def load_clinical_data():
    """Load the clinical datasets."""
    print("Loading clinical datasets...")
    
    try:
        # Load ADSL (Subject-Level Analysis Dataset)
        adsl = read_sas('data/adsl.sas7bdat')
        print(f"✅ Loaded ADSL: {len(adsl)} subjects")
        
        return adsl
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None

def calculate_demographics_statistics(adsl):
    """Calculate demographics statistics following professional clinical format."""
    print("Calculating demographics statistics...")
    
    # Filter to safety population if available
    if 'SAFFL' in adsl.columns:
        safety_pop = adsl[adsl['SAFFL'] == 'Y'].copy()
        print(f"Safety population: {len(safety_pop)} subjects")
    else:
        safety_pop = adsl.copy()
        print(f"Using all subjects: {len(safety_pop)} subjects")
    
    # Check available treatment groups
    if 'TRT01P' in safety_pop.columns:
        treatments = safety_pop['TRT01P'].unique()
        print(f"Treatment groups: {treatments}")
    else:
        print("❌ TRT01P variable not found")
        return None
    
    # Initialize results list
    results = []
    
    # Age statistics
    if 'AGE' in safety_pop.columns:
        print("Processing Age statistics...")
        
        age_stats = []
        treatment_groups = []
        
        for trt in sorted(safety_pop['TRT01P'].unique()):
            trt_data = safety_pop[safety_pop['TRT01P'] == trt]['AGE'].dropna()
            treatment_groups.append(trt_data.values)
            
            n = len(trt_data)
            mean_val = trt_data.mean()
            std_val = trt_data.std()
            median_val = trt_data.median()
            min_val = trt_data.min()
            max_val = trt_data.max()
            
            age_stats.append({
                'Treatment': trt,
                'N': n,
                'Mean_SD': f"{mean_val:.1f} ({std_val:.2f})",
                'Median': f"{median_val:.1f}",
                'Min_Max': f"{min_val:.0f} : {max_val:.0f}"
            })
        
        # Calculate p-value using ANOVA
        if len(treatment_groups) >= 2:
            try:
                f_stat, p_value = stats.f_oneway(*treatment_groups)
                p_val_str = f"{p_value:.4f}" if p_value >= 0.0001 else "<0.0001"
            except:
                p_val_str = "N/A"
        else:
            p_val_str = "N/A"
        
        # Add Age rows
        results.append(['Age(Year)', '', '', '', ''])
        results.append(['  n'] + [str(stat['N']) for stat in age_stats] + [str(sum(stat['N'] for stat in age_stats))] + [p_val_str])
        results.append(['  Mean (SD)'] + [stat['Mean_SD'] for stat in age_stats] + [f"{safety_pop['AGE'].mean():.1f} ({safety_pop['AGE'].std():.2f})"] + [''])
        results.append(['  Median'] + [stat['Median'] for stat in age_stats] + [f"{safety_pop['AGE'].median():.1f}"] + [''])
        results.append(['  Min : Max'] + [stat['Min_Max'] for stat in age_stats] + [f"{safety_pop['AGE'].min():.0f} : {safety_pop['AGE'].max():.0f}"] + [''])
    
    # Sex statistics
    if 'SEX' in safety_pop.columns:
        print("Processing Sex statistics...")
        
        sex_stats = []
        sex_groups = []
        
        for trt in sorted(safety_pop['TRT01P'].unique()):
            trt_data = safety_pop[safety_pop['TRT01P'] == trt]
            sex_counts = trt_data['SEX'].value_counts()
            total_n = len(trt_data)
            
            sex_groups.append(trt_data['SEX'].values)
            
            sex_stats.append({
                'Treatment': trt,
                'Total_N': total_n,
                'Male_n': sex_counts.get('M', 0),
                'Female_n': sex_counts.get('F', 0),
                'Male_pct': (sex_counts.get('M', 0) / total_n * 100) if total_n > 0 else 0,
                'Female_pct': (sex_counts.get('F', 0) / total_n * 100) if total_n > 0 else 0
            })
        
        # Calculate p-value using Chi-square test
        if len(sex_groups) >= 2:
            try:
                # Create contingency table
                contingency = pd.crosstab(safety_pop['TRT01P'], safety_pop['SEX'])
                chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
                p_val_str = f"{p_value:.4f}" if p_value >= 0.0001 else "<0.0001"
            except:
                p_val_str = "N/A"
        else:
            p_val_str = "N/A"
        
        # Add Sex rows
        results.append(['Sex', '', '', '', ''])
        
        # Male
        male_total = safety_pop['SEX'].value_counts().get('M', 0)
        male_pct = (male_total / len(safety_pop) * 100) if len(safety_pop) > 0 else 0
        results.append(['  Male'] + [f"{stat['Male_n']} ({stat['Male_pct']:.1f}%)" for stat in sex_stats] + 
                      [f"{male_total} ({male_pct:.1f}%)"] + [p_val_str])
        
        # Female  
        female_total = safety_pop['SEX'].value_counts().get('F', 0)
        female_pct = (female_total / len(safety_pop) * 100) if len(safety_pop) > 0 else 0
        results.append(['  Female'] + [f"{stat['Female_n']} ({stat['Female_pct']:.1f}%)" for stat in sex_stats] + 
                      [f"{female_total} ({female_pct:.1f}%)"] + [''])
    
    # Race statistics (if available)
    if 'RACE' in safety_pop.columns:
        print("Processing Race statistics...")
        
        race_counts = safety_pop['RACE'].value_counts()
        race_groups = []
        
        for trt in sorted(safety_pop['TRT01P'].unique()):
            trt_data = safety_pop[safety_pop['TRT01P'] == trt]
            race_groups.append(trt_data['RACE'].values)
        
        # Calculate p-value using Chi-square test
        if len(race_groups) >= 2:
            try:
                contingency = pd.crosstab(safety_pop['TRT01P'], safety_pop['RACE'])
                chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
                p_val_str = f"{p_value:.4f}" if p_value >= 0.0001 else "<0.0001"
            except:
                p_val_str = "N/A"
        else:
            p_val_str = "N/A"
        
        results.append(['Race', '', '', '', ''])
        
        # Add each race category
        for race in sorted(race_counts.index):
            race_stats = []
            for trt in sorted(safety_pop['TRT01P'].unique()):
                trt_data = safety_pop[safety_pop['TRT01P'] == trt]
                race_n = len(trt_data[trt_data['RACE'] == race])
                race_pct = (race_n / len(trt_data) * 100) if len(trt_data) > 0 else 0
                race_stats.append(f"{race_n} ({race_pct:.1f}%)")
            
            total_race_n = race_counts[race]
            total_race_pct = (total_race_n / len(safety_pop) * 100) if len(safety_pop) > 0 else 0
            
            p_val_display = p_val_str if race == sorted(race_counts.index)[0] else ''
            results.append([f"  {race}"] + race_stats + [f"{total_race_n} ({total_race_pct:.1f}%)"] + [p_val_display])
    
    return results, sorted(safety_pop['TRT01P'].unique())

def create_demographics_table(results, treatments):
    """Create the demographics table DataFrame."""
    print("Creating demographics table...")
    
    # Create column headers following professional clinical format
    columns = ['Category']
    
    # Add treatment columns with N counts
    for trt in treatments:
        columns.append(f"{trt}")
    
    # Add combined total and p-value columns
    columns.extend(['Combined Total', 'p-Value'])
    
    # Create DataFrame
    df = pd.DataFrame(results, columns=columns)
    
    print(f"Created table with {len(df)} rows and {len(df.columns)} columns")
    return df

def generate_clinical_demographics_table():
    """Main function to generate Clinical Example 01 demographics table."""
    print("🚀 Generating Clinical Example 01: Demographics Table with P-values")
    print("=" * 70)
    
    # Load data
    adsl = load_clinical_data()
    if adsl is None:
        return False
    
    # Calculate statistics
    results, treatments = calculate_demographics_statistics(adsl)
    if not results:
        print("❌ Failed to calculate statistics")
        return False
    
    # Create table
    demo_table = create_demographics_table(results, treatments)
    
    # Generate RTF content following professional clinical format
    title = "Example 01\nSummary of Demography & Baseline Characteristics"
    subtitle = "Randomized Population"
    
    footnotes = [
        "Randomized Population",
        f"Generated on {datetime.now().strftime('%d%b%Y %H:%M')} using py4csr",
        "P-values: ANOVA for continuous variables, Chi-square for categorical variables"
    ]
    
    print("Generating RTF content...")
    rtf_content = create_sasshiato_table(
        df=demo_table,
        title=title,
        footnotes=footnotes
    )
    
    # Save to file
    output_filename = "example_01_demographics_py4csr.rtf"
    save_sasshiato_rtf(rtf_content, output_filename)
    
    print(f"✅ Successfully generated: {output_filename}")
    print(f"📊 Table dimensions: {demo_table.shape}")
    print(f"📝 RTF content length: {len(rtf_content)} characters")
    
    # Display summary
    print("\n📋 Table Summary:")
    print(demo_table.to_string(index=False))
    
    return True

if __name__ == "__main__":
    success = generate_clinical_demographics_table()
    if success:
        print("\n🎉 Clinical Example 01 generated successfully!")
    else:
        print("\n❌ Failed to generate Clinical Example 01")
        sys.exit(1) 