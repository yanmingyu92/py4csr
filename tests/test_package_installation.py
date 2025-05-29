#!/usr/bin/env python3
"""
Test script to verify py4csr package installation and core functionality.
"""

import sys
import pandas as pd
import numpy as np

def test_basic_import():
    """Test basic package import."""
    try:
        import py4csr
        print(f"✅ py4csr imported successfully (version: {py4csr.__version__})")
        return True
    except ImportError as e:
        print(f"❌ Failed to import py4csr: {e}")
        return False

def test_functional_import():
    """Test functional module import."""
    try:
        from py4csr.functional import ReportSession, FunctionalConfig
        print("✅ Functional modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import functional modules: {e}")
        return False

def test_clinical_import():
    """Test clinical module import."""
    try:
        from py4csr.clinical import ClinicalSession
        print("✅ Clinical modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import clinical modules: {e}")
        return False

def test_tables_import():
    """Test tables module import."""
    try:
        from py4csr.tables import ClinicalRTFFormatter
        print("✅ Tables modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import tables modules: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality with sample data."""
    try:
        # Create sample clinical data
        np.random.seed(42)
        n_subjects = 100
        
        sample_data = pd.DataFrame({
            'USUBJID': [f'SUBJ-{i:03d}' for i in range(1, n_subjects + 1)],
            'TRT01P': np.random.choice(['Placebo', 'Treatment A', 'Treatment B'], n_subjects),
            'AGE': np.random.normal(65, 12, n_subjects).astype(int),
            'SEX': np.random.choice(['M', 'F'], n_subjects),
            'RACE': np.random.choice(['WHITE', 'BLACK', 'ASIAN', 'OTHER'], n_subjects),
            'SAFFL': 'Y'
        })
        
        # Test clinical session creation
        from py4csr.clinical import ClinicalSession
        
        session = ClinicalSession("TEST-001", "Package Installation Test")
        print("✅ Basic clinical session creation works")
        print(f"   Sample data: {sample_data.shape}")
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_data_loading():
    """Test data loading functionality."""
    try:
        from py4csr.data import apply_formats, handle_missing_data
        
        # Create sample data
        np.random.seed(42)
        sample_data = pd.DataFrame({
            'TRT01P': np.random.choice(['Placebo', 'Treatment'], 100),
            'AGE': np.random.normal(65, 12, 100),
            'SAFFL': 'Y'
        })
        
        # Test data processing functions
        cleaned_data = handle_missing_data(sample_data)
        
        print("✅ Data processing functionality works")
        print(f"   Processed data: {cleaned_data.shape}")
        return True
        
    except Exception as e:
        print(f"❌ Data processing test failed: {e}")
        return False

def test_simple_workflow():
    """Test simple clinical reporting workflow."""
    try:
        from py4csr.clinical import ClinicalSession
        print("✓ ClinicalSession imported successfully")
        
        # Create simple test session
        session = ClinicalSession("TEST-001", "Package Installation Test")
        print("✓ ClinicalSession created")
        
        return True
        
    except ImportError as e:
        print(f"✗ Failed to import clinical session: {e}")
        return False
    except Exception as e:
        print(f"✗ Simple workflow test failed: {e}")
        return False

def test_tables_integration():
    """Test tables subpackage integration with clinical functionality."""
    try:
        from py4csr.tables import ClinicalRTFFormatter
        print("✓ ClinicalRTFFormatter imported successfully")
        
        # Create simple test data
        import pandas as pd
        test_data = pd.DataFrame({
            'Parameter': ['Age (years)', 'Mean (SD)', 'Gender', 'Male'],
            'Placebo': ['86', '75.2 (8.6)', '', '43 (50.0%)'],
            'Treatment': ['84', '75.7 (8.3)', '', '41 (48.8%)']
        })
        
        formatter = ClinicalRTFFormatter()
        print("✓ ClinicalRTFFormatter created")
        
        return True
        
    except ImportError as e:
        print(f"✗ Failed to import table utilities: {e}")
        return False
    except Exception as e:
        print(f"✗ Table integration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing py4csr Package Installation")
    print("=" * 50)
    
    tests = [
        test_basic_import,
        test_functional_import,
        test_clinical_import,
        test_tables_import,
        test_basic_functionality,
        test_data_loading,
        test_simple_workflow,
        test_tables_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! py4csr is ready for use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the installation.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 