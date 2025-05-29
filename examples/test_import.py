#!/usr/bin/env python3
"""Test script to check py4csr imports"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

print("Testing py4csr imports...")

try:
    import py4csr
    print(f"✓ py4csr imported successfully, version: {py4csr.__version__}")
except Exception as e:
    print(f"✗ Error importing py4csr: {e}")

try:
    from py4csr.tables import ClinicalRTFFormatter
    print("✓ ClinicalRTFFormatter imported successfully")
except Exception as e:
    print(f"✗ Error importing ClinicalRTFFormatter: {e}")

try:
    from py4csr.tables import create_clinical_rtf_table
    print("✓ create_clinical_rtf_table imported successfully")
except Exception as e:
    print(f"✗ Error importing create_clinical_rtf_table: {e}")

try:
    from py4csr import create_rtf_table
    print("✓ create_rtf_table convenience function imported successfully")
except Exception as e:
    print(f"✗ Error importing create_rtf_table: {e}")

print("\nTesting RTF functionality...")
try:
    import pandas as pd
    
    # Create sample data
    data = pd.DataFrame({
        'Treatment': ['Placebo', 'Active'],
        'N': [50, 50],
        'Age': ['65.2 (8.1)', '64.8 (7.9)']
    })
    
    # Test RTF formatter
    formatter = ClinicalRTFFormatter()
    rtf_content = formatter.format_table_to_rtf(
        df=data,
        title="Test Table",
        subtitle="Test Subtitle"
    )
    print("✓ RTF formatting test successful")
    print(f"RTF content length: {len(rtf_content)} characters")
    
except Exception as e:
    print(f"✗ Error testing RTF functionality: {e}")

print("\nImport test complete!") 