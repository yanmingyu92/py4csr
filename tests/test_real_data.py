"""
Simple Test with Real Clinical Trial Data

This test uses the actual SAS datasets from the data directory to validate
the existing functional reporting system with real clinical trial data.
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Add the py4csr package to the path
sys.path.insert(0, str(Path(__file__).parent / 'py4csr'))

try:
    import pyreadstat
    SAS_READER_AVAILABLE = True
    print("✓ pyreadstat available for reading SAS files")
except ImportError:
    try:
        from sas7bdat import SAS7BDAT
        SAS_READER_AVAILABLE = True
        print("✓ sas7bdat available for reading SAS files")
    except ImportError:
        SAS_READER_AVAILABLE = False
        print("✗ No SAS reader available")


def load_real_sas_data():
    """Load real SAS datasets from the data directory."""
    print("\n" + "="*60)
    print("LOADING REAL SAS CLINICAL TRIAL DATASETS")
    print("="*60)
    
    if not SAS_READER_AVAILABLE:
        print("Warning: No SAS reader available. Install pyreadstat or sas7bdat.")
        return None
    
    data_dir = Path(__file__).parent / 'data'
    if not data_dir.exists():
        print(f"Data directory not found: {data_dir}")
        return None
    
    datasets = {}
    sas_files = list(data_dir.glob('*.sas7bdat'))
    
    if not sas_files:
        print("No SAS files found in data directory")
        return None
    
    print(f"Found {len(sas_files)} SAS files:")
    for file in sas_files:
        print(f"  - {file.name} ({file.stat().st_size / 1024 / 1024:.1f} MB)")
    
    # Load each SAS file
    for sas_file in sas_files:
        try:
            dataset_name = sas_file.stem.upper()
            print(f"\nLoading {dataset_name}...")
            
            # Try pyreadstat first
            if 'pyreadstat' in sys.modules:
                df, meta = pyreadstat.read_sas7bdat(str(sas_file))
                print(f"  ✓ Loaded with pyreadstat: {len(df)} rows, {len(df.columns)} columns")
            else:
                # Fallback to sas7bdat
                with SAS7BDAT(str(sas_file), skip_header=False) as reader:
                    df = reader.to_data_frame()
                print(f"  ✓ Loaded with sas7bdat: {len(df)} rows, {len(df.columns)} columns")
            
            # Basic data info
            print(f"  Columns: {list(df.columns[:10])}{'...' if len(df.columns) > 10 else ''}")
            
            # Check for key clinical variables
            key_vars = ['USUBJID', 'STUDYID', 'TRT01P', 'TRT01PN', 'SAFFL', 'ITTFL']
            present_vars = [var for var in key_vars if var in df.columns]
            if present_vars:
                print(f"  Key variables present: {present_vars}")
            
            datasets[dataset_name] = df
            
        except Exception as e:
            print(f"  ✗ Error loading {sas_file.name}: {e}")
            continue
    
    print(f"\n✓ Successfully loaded {len(datasets)} datasets")
    return datasets


def analyze_real_data_structure(datasets):
    """Analyze the structure of real clinical trial data."""
    print("\n" + "="*60)
    print("REAL DATA STRUCTURE ANALYSIS")
    print("="*60)
    
    for name, df in datasets.items():
        print(f"\n{name} Dataset:")
        print(f"  Shape: {df.shape}")
        print(f"  Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB")
        
        # Show data types
        print("  Data types:")
        dtype_counts = df.dtypes.value_counts()
        for dtype, count in dtype_counts.items():
            print(f"    {dtype}: {count} columns")
        
        # Show sample of key columns
        key_columns = []
        for col in ['USUBJID', 'STUDYID', 'TRT01P', 'PARAM', 'AVAL', 'AVALC', 'VISIT']:
            if col in df.columns:
                key_columns.append(col)
        
        if key_columns:
            print(f"  Sample data ({', '.join(key_columns)}):")
            sample_df = df[key_columns].head(3)
            for _, row in sample_df.iterrows():
                values = {k: str(v)[:20] + '...' if len(str(v)) > 20 else v 
                         for k, v in row.items()}
                print(f"    {values}")
        
        # Check for missing data
        missing_pct = (df.isnull().sum() / len(df) * 100).round(1)
        high_missing = missing_pct[missing_pct > 10]
        if len(high_missing) > 0:
            print(f"  High missing data (>10%): {dict(high_missing)}")
        
        # Show unique values for key categorical variables
        categorical_vars = ['TRT01P', 'SEX', 'RACE', 'AEBODSYS', 'AESEV']
        for var in categorical_vars:
            if var in df.columns:
                unique_vals = df[var].unique()
                if len(unique_vals) <= 10:
                    print(f"  {var} values: {list(unique_vals)}")
                else:
                    print(f"  {var}: {len(unique_vals)} unique values")


def test_basic_data_analysis():
    """Test basic data analysis with real data without using functional module."""
    print("\n" + "="*60)
    print("BASIC DATA ANALYSIS WITH REAL DATA")
    print("="*60)
    
    datasets = load_real_sas_data()
    if not datasets:
        print("No real data available - cannot run test")
        return
    
    # Test with ADSL if available
    if 'ADSL' in datasets:
        adsl = datasets['ADSL']
        print(f"\nAnalyzing ADSL dataset ({len(adsl)} subjects)")
        
        # Basic demographics analysis
        if 'AGE' in adsl.columns:
            age_stats = adsl['AGE'].describe()
            print(f"  Age statistics:")
            print(f"    Mean: {age_stats['mean']:.1f}")
            print(f"    Median: {age_stats['50%']:.1f}")
            print(f"    Range: {age_stats['min']:.0f} - {age_stats['max']:.0f}")
        
        # Treatment distribution
        if 'TRT01P' in adsl.columns:
            trt_counts = adsl['TRT01P'].value_counts()
            print(f"  Treatment distribution:")
            for trt, count in trt_counts.items():
                pct = count / len(adsl) * 100
                print(f"    {trt}: {count} ({pct:.1f}%)")
        
        # Gender distribution
        if 'SEX' in adsl.columns:
            sex_counts = adsl['SEX'].value_counts()
            print(f"  Gender distribution:")
            for sex, count in sex_counts.items():
                pct = count / len(adsl) * 100
                print(f"    {sex}: {count} ({pct:.1f}%)")
        
        # Race distribution
        if 'RACE' in adsl.columns:
            race_counts = adsl['RACE'].value_counts()
            print(f"  Race distribution:")
            for race, count in race_counts.head().items():
                pct = count / len(adsl) * 100
                print(f"    {race}: {count} ({pct:.1f}%)")
    
    # Test with ADAE if available
    if 'ADAE' in datasets:
        adae = datasets['ADAE']
        print(f"\nAnalyzing ADAE dataset ({len(adae)} adverse events)")
        
        # AE frequency by system organ class
        if 'AEBODSYS' in adae.columns:
            soc_counts = adae['AEBODSYS'].value_counts()
            print(f"  Top 5 System Organ Classes:")
            for soc, count in soc_counts.head().items():
                pct = count / len(adae) * 100
                print(f"    {soc}: {count} ({pct:.1f}%)")
        
        # AE severity distribution
        if 'AESEV' in adae.columns:
            sev_counts = adae['AESEV'].value_counts()
            print(f"  Severity distribution:")
            for sev, count in sev_counts.items():
                pct = count / len(adae) * 100
                print(f"    {sev}: {count} ({pct:.1f}%)")
        
        # Serious AE rate
        if 'AESER' in adae.columns:
            ser_counts = adae['AESER'].value_counts()
            print(f"  Serious AE distribution:")
            for ser, count in ser_counts.items():
                pct = count / len(adae) * 100
                print(f"    {ser}: {count} ({pct:.1f}%)")


def test_data_quality_checks():
    """Perform data quality checks on real clinical data."""
    print("\n" + "="*60)
    print("DATA QUALITY CHECKS ON REAL DATA")
    print("="*60)
    
    datasets = load_real_sas_data()
    if not datasets:
        return
    
    for name, df in datasets.items():
        print(f"\n{name} Data Quality:")
        
        # Check for duplicate subjects
        if 'USUBJID' in df.columns:
            n_subjects = df['USUBJID'].nunique()
            n_records = len(df)
            print(f"  Subjects: {n_subjects}, Records: {n_records}")
            
            if n_records > n_subjects:
                print(f"  Multiple records per subject (expected for {name})")
            
            # Check for missing subject IDs
            missing_usubjid = df['USUBJID'].isnull().sum()
            if missing_usubjid > 0:
                print(f"  ⚠ Missing USUBJID: {missing_usubjid} records")
        
        # Check treatment variable
        if 'TRT01P' in df.columns:
            treatments = df['TRT01P'].value_counts()
            print(f"  Treatment distribution:")
            for trt, count in treatments.items():
                print(f"    {trt}: {count}")
        
        # Check key dates
        date_vars = [col for col in df.columns if 'DT' in col or 'DATE' in col]
        if date_vars:
            print(f"  Date variables: {date_vars[:5]}{'...' if len(date_vars) > 5 else ''}")
        
        # Check for completely empty columns
        empty_cols = df.columns[df.isnull().all()].tolist()
        if empty_cols:
            print(f"  ⚠ Completely empty columns: {empty_cols}")
        
        # Check data ranges for numeric variables
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            print(f"  Numeric variables: {len(numeric_cols)}")
            for col in numeric_cols[:3]:  # Show first 3
                if not df[col].isnull().all():
                    min_val, max_val = df[col].min(), df[col].max()
                    print(f"    {col}: {min_val:.2f} to {max_val:.2f}")


def create_simple_summary_tables():
    """Create simple summary tables from real data."""
    print("\n" + "="*60)
    print("CREATING SIMPLE SUMMARY TABLES")
    print("="*60)
    
    datasets = load_real_sas_data()
    if not datasets:
        return
    
    output_dir = Path("test_output_real_data_simple")
    output_dir.mkdir(exist_ok=True)
    
    # Demographics table from ADSL
    if 'ADSL' in datasets:
        adsl = datasets['ADSL']
        print(f"\nCreating demographics table from ADSL...")
        
        demo_summary = {}
        
        # Age statistics
        if 'AGE' in adsl.columns:
            age_stats = adsl['AGE'].describe()
            demo_summary['Age'] = {
                'N': int(age_stats['count']),
                'Mean (SD)': f"{age_stats['mean']:.1f} ({age_stats['std']:.1f})",
                'Median': f"{age_stats['50%']:.1f}",
                'Min, Max': f"{age_stats['min']:.0f}, {age_stats['max']:.0f}"
            }
        
        # Gender
        if 'SEX' in adsl.columns:
            sex_counts = adsl['SEX'].value_counts()
            demo_summary['Gender'] = {}
            for sex, count in sex_counts.items():
                pct = count / len(adsl) * 100
                demo_summary['Gender'][sex] = f"{count} ({pct:.1f}%)"
        
        # Race
        if 'RACE' in adsl.columns:
            race_counts = adsl['RACE'].value_counts()
            demo_summary['Race'] = {}
            for race, count in race_counts.items():
                pct = count / len(adsl) * 100
                demo_summary['Race'][race] = f"{count} ({pct:.1f}%)"
        
        # Save to CSV
        demo_df = pd.DataFrame(demo_summary).T
        demo_df.to_csv(output_dir / "demographics_summary.csv")
        print(f"  ✓ Demographics summary saved to {output_dir / 'demographics_summary.csv'}")
    
    # AE summary from ADAE
    if 'ADAE' in datasets:
        adae = datasets['ADAE']
        print(f"\nCreating AE summary from ADAE...")
        
        ae_summary = {}
        
        # Overall AE counts
        if 'USUBJID' in adae.columns:
            n_subjects_with_ae = adae['USUBJID'].nunique()
            n_total_aes = len(adae)
            ae_summary['Overall'] = {
                'Subjects with AEs': n_subjects_with_ae,
                'Total AE records': n_total_aes
            }
        
        # By severity
        if 'AESEV' in adae.columns:
            sev_counts = adae['AESEV'].value_counts()
            ae_summary['By Severity'] = {}
            for sev, count in sev_counts.items():
                pct = count / len(adae) * 100
                ae_summary['By Severity'][sev] = f"{count} ({pct:.1f}%)"
        
        # By system organ class (top 10)
        if 'AEBODSYS' in adae.columns:
            soc_counts = adae['AEBODSYS'].value_counts().head(10)
            ae_summary['Top 10 SOCs'] = {}
            for soc, count in soc_counts.items():
                pct = count / len(adae) * 100
                ae_summary['Top 10 SOCs'][soc] = f"{count} ({pct:.1f}%)"
        
        # Save to CSV
        ae_df = pd.DataFrame(ae_summary).T
        ae_df.to_csv(output_dir / "ae_summary.csv")
        print(f"  ✓ AE summary saved to {output_dir / 'ae_summary.csv'}")


def main():
    """Run comprehensive tests with real clinical trial data."""
    print("REAL CLINICAL DATA TESTING - SIMPLE VERSION")
    print("=" * 80)
    
    if not SAS_READER_AVAILABLE:
        print("ERROR: SAS reader not available. Please install:")
        print("  pip install pyreadstat")
        print("  or")
        print("  pip install sas7bdat")
        return
    
    # Load and analyze real data structure
    datasets = load_real_sas_data()
    if not datasets:
        print("No real data available - cannot run tests")
        return
    
    analyze_real_data_structure(datasets)
    test_data_quality_checks()
    test_basic_data_analysis()
    create_simple_summary_tables()
    
    print("\n" + "="*80)
    print("REAL DATA TESTING COMPLETED")
    print("="*80)
    print("Check the 'test_output_real_data_simple' directory for generated outputs")


if __name__ == "__main__":
    main() 