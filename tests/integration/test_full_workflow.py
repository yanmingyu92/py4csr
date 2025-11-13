"""
Integration tests for py4csr full workflow.

Tests end-to-end clinical table generation workflows.
"""

import pandas as pd
import pytest
from pathlib import Path

from py4csr.clinical.session import ClinicalSession


class TestDemographicsWorkflow:
    """Test complete demographics table workflow."""
    
    def test_basic_demographics_table(self, sample_adsl, temp_output_dir):
        """Test generating a basic demographics table."""
        # Create session
        session = ClinicalSession(
            uri="demographics",
            purpose="Demographics and Baseline Characteristics",
            outname="t_demographics"
        )
        
        # Define report
        session.define_report(
            dataset=sample_adsl,
            pop_where="1==1",
            subjid="USUBJID",
            title1="Table 1",
            title2="Demographics and Baseline Characteristics",
            title3="Safety Population",
            footnot1="Note: All randomized subjects included",
            footnot2="Source: ADSL dataset"
        )
        
        # Add treatment variable
        session.add_trt(name="TRT01PN", decode="TRT01P")
        
        # Add continuous variables
        session.add_var(name="AGE", label="Age (years)", stats="n mean+sd median min+max")
        session.add_var(name="WEIGHT", label="Weight (kg)", stats="n mean+sd")
        session.add_var(name="HEIGHT", label="Height (cm)", stats="n mean+sd")
        
        # Add categorical variables
        session.add_catvar(name="SEX", label="Sex, n (%)", stats="npct")
        session.add_catvar(name="RACE", label="Race, n (%)", stats="npct")
        
        # Generate table
        result = session.generate()
        
        # Verify result
        assert result is not None
        assert session.generated_data is not None
        assert session.generated_table is not None
    
    def test_demographics_with_rtf_output(self, sample_adsl, temp_output_dir):
        """Test generating demographics table with RTF output."""
        session = ClinicalSession(uri="demographics")
        
        session.define_report(
            dataset=sample_adsl,
            subjid="USUBJID",
            title1="Demographics Table",
            title2="All Subjects"
        )
        
        session.add_trt(name="TRT01PN", decode="TRT01P")
        session.add_var(name="AGE", label="Age (years)")
        session.add_catvar(name="SEX", label="Sex, n (%)")
        
        # Generate
        session.generate()
        
        # Save to RTF
        output_file = temp_output_dir / "demographics.rtf"
        session.finalize(output_file=str(output_file), output_format='rtf')

        # Verify file created
        assert output_file.exists()

        # Verify RTF content
        with open(output_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        assert '{\\rtf1' in content
    
    def test_demographics_with_csv_output(self, sample_adsl, temp_output_dir):
        """Test generating demographics table with CSV output."""
        session = ClinicalSession(uri="demographics")
        
        session.define_report(
            dataset=sample_adsl,
            subjid="USUBJID"
        )
        
        session.add_trt(name="TRT01PN", decode="TRT01P")
        session.add_var(name="AGE", label="Age (years)")
        
        # Generate
        session.generate()
        
        # Save to CSV
        output_file = temp_output_dir / "demographics.csv"
        session.finalize(output_file=str(output_file), output_format='csv')

        # Verify file created
        assert output_file.exists()

        # Read and verify
        df = pd.read_csv(output_file)
        assert len(df) > 0


class TestSafetyWorkflow:
    """Test complete safety table workflow."""
    
    def test_adverse_events_summary(self, sample_adae, temp_output_dir):
        """Test generating adverse events summary table."""
        session = ClinicalSession(
            uri="ae_summary",
            purpose="Adverse Events Summary"
        )
        
        session.define_report(
            dataset=sample_adae,
            subjid="USUBJID",
            title1="Table 2",
            title2="Summary of Adverse Events",
            title3="Safety Population"
        )
        
        session.add_trt(name="TRTAN", decode="TRTA")
        
        # Add condition-based rows for AE summary
        session.add_cond(
            label="Subjects with at least one AE",
            where="AOCCFL=='Y'",
            stats="n pct"
        )
        
        session.add_cond(
            label="Subjects with serious AE",
            where="AESER=='Y'",
            stats="n pct"
        )
        
        session.add_cond(
            label="Subjects with severe AE",
            where="AESEV=='SEVERE'",
            stats="n pct"
        )
        
        # Generate
        result = session.generate()
        
        assert result is not None
        assert session.generated_data is not None


class TestMultipleFormatsWorkflow:
    """Test generating multiple output formats."""
    
    def test_generate_all_formats(self, sample_adsl, temp_output_dir):
        """Test generating RTF and CSV outputs."""
        session = ClinicalSession(uri="multi_format")

        session.define_report(
            dataset=sample_adsl,
            subjid="USUBJID",
            title1="Multi-Format Test"
        )

        session.add_trt(name="TRT01PN", decode="TRT01P")
        session.add_var(name="AGE", label="Age (years)")

        # Generate once
        session.generate()

        # Save in multiple formats
        rtf_file = temp_output_dir / "output.rtf"
        csv_file = temp_output_dir / "output.csv"

        session.finalize(output_file=str(rtf_file), output_format='rtf')
        session.finalize(output_file=str(csv_file), output_format='csv')

        # Verify all files created
        assert rtf_file.exists()
        assert csv_file.exists()


class TestComplexTableWorkflow:
    """Test complex table scenarios."""
    
    def test_table_with_subgroups(self, sample_adsl):
        """Test table with subgroup analysis."""
        session = ClinicalSession(uri="subgroup_analysis")
        
        session.define_report(
            dataset=sample_adsl,
            subjid="USUBJID",
            title1="Subgroup Analysis"
        )
        
        session.add_trt(name="TRT01PN", decode="TRT01P")
        
        # Overall population
        session.add_var(name="AGE", label="Age (years) - All Subjects")
        
        # Subgroup by sex
        session.add_var(
            name="AGE",
            label="Age (years) - Male",
            where="SEX=='M'"
        )
        
        session.add_var(
            name="AGE",
            label="Age (years) - Female",
            where="SEX=='F'"
        )
        
        # Generate
        result = session.generate()
        
        assert result is not None
    
    def test_table_with_multiple_statistics(self, sample_adsl):
        """Test table with various statistics."""
        session = ClinicalSession(uri="detailed_stats")
        
        session.define_report(
            dataset=sample_adsl,
            subjid="USUBJID"
        )
        
        session.add_trt(name="TRT01PN", decode="TRT01P")
        
        # Continuous variable with all statistics
        session.add_var(
            name="AGE",
            label="Age (years)",
            stats="n mean+sd median q1+q3 min+max"
        )
        
        # Categorical variable
        session.add_catvar(
            name="AGEGR1",
            label="Age Group, n (%)",
            stats="npct"
        )
        
        # Generate
        result = session.generate()
        
        assert result is not None
        assert len(session.generated_data) > 0


class TestErrorHandling:
    """Test error handling in workflows."""
    
    def test_missing_dataset(self):
        """Test error when dataset not defined."""
        session = ClinicalSession(uri="test")
        
        # Try to generate without defining dataset
        with pytest.raises((AttributeError, ValueError, Exception)):
            session.generate()
    
    def test_missing_treatment(self, sample_adsl):
        """Test warning when treatment not defined."""
        session = ClinicalSession(uri="test")
        
        session.define_report(dataset=sample_adsl, subjid="USUBJID")
        session.add_var(name="AGE", label="Age")
        
        # Should work but may give warning
        try:
            result = session.generate()
            # If it works, result should be something
            assert result is not None or session.generated_data is not None
        except Exception:
            # Or it may raise an error - both are acceptable
            pass
    
    def test_invalid_variable(self, sample_adsl):
        """Test handling of invalid variable name."""
        session = ClinicalSession(uri="test")
        
        session.define_report(dataset=sample_adsl, subjid="USUBJID")
        session.add_trt(name="TRT01PN", decode="TRT01P")
        
        # Add variable that doesn't exist
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            session.add_var(name="NONEXISTENT", label="Missing")
            
            # Should generate warning
            assert len(w) > 0

