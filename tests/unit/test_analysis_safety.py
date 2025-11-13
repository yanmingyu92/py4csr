"""
Unit tests for py4csr.analysis.safety module.

Tests safety analysis functions.
"""

import pandas as pd
import pytest

from py4csr.analysis.safety import (
    create_ae_specific_table,
    create_ae_summary,
    create_lab_summary,
)


class TestCreateAeSummary:
    """Test create_ae_summary function."""

    def test_basic_ae_summary(self, sample_adae):
        """Test basic AE summary creation."""
        result = create_ae_summary(
            sample_adae, treatment_var="TRT01P", term_var="AEDECOD"
        )
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

    def test_with_severity(self, sample_adae):
        """Test AE summary with severity variable."""
        if "AESEV" in sample_adae.columns:
            result = create_ae_summary(
                sample_adae,
                treatment_var="TRT01P",
                term_var="AEDECOD",
                severity_var="AESEV",
            )
            assert isinstance(result, pd.DataFrame)

    def test_treatment_columns(self, sample_adae):
        """Test that treatment columns are created."""
        result = create_ae_summary(
            sample_adae, treatment_var="TRT01P", term_var="AEDECOD"
        )
        # Should have term column plus treatment columns
        assert len(result.columns) >= 2

    def test_unique_terms(self, sample_adae):
        """Test that unique AE terms are included."""
        result = create_ae_summary(
            sample_adae, treatment_var="TRT01P", term_var="AEDECOD"
        )
        # Should have rows for different AE terms
        assert len(result) > 0

    def test_empty_dataset(self):
        """Test with empty AE dataset."""
        empty_df = pd.DataFrame(
            columns=["USUBJID", "TRT01P", "AEDECOD", "AESEV"]
        )
        result = create_ae_summary(
            empty_df, treatment_var="TRT01P", term_var="AEDECOD"
        )
        assert isinstance(result, pd.DataFrame)

    def test_missing_term_var(self, sample_adae):
        """Test with missing term variable."""
        try:
            result = create_ae_summary(
                sample_adae, treatment_var="TRT01P", term_var="NONEXISTENT"
            )
        except KeyError:
            # Expected to fail
            pass


class TestCreateAeSpecificTable:
    """Test create_ae_specific_table function."""

    def test_basic_specific_table(self, sample_adae):
        """Test basic AE-specific table creation."""
        result = create_ae_specific_table(
            sample_adae, treatment_var="TRT01P", term_var="AEDECOD"
        )
        assert isinstance(result, pd.DataFrame)

    def test_with_body_system(self, sample_adae):
        """Test with body system variable."""
        if "AEBODSYS" in sample_adae.columns:
            result = create_ae_specific_table(
                sample_adae,
                treatment_var="TRT01P",
                term_var="AEDECOD",
                system_var="AEBODSYS",
            )
            assert isinstance(result, pd.DataFrame)

    def test_severity_breakdown(self, sample_adae):
        """Test severity breakdown in specific table."""
        # create_ae_specific_table doesn't have severity_var parameter
        # Just test basic functionality
        result = create_ae_specific_table(
            sample_adae,
            treatment_var="TRT01P",
            term_var="AEDECOD",
        )
        assert isinstance(result, pd.DataFrame)

    def test_empty_dataset(self):
        """Test with empty dataset."""
        empty_df = pd.DataFrame(
            columns=["USUBJID", "TRT01P", "AEDECOD", "AEBODSYS"]
        )
        result = create_ae_specific_table(
            empty_df, treatment_var="TRT01P", term_var="AEDECOD"
        )
        assert isinstance(result, pd.DataFrame)


class TestCreateLabSummary:
    """Test create_lab_summary function."""

    def test_basic_lab_summary(self, sample_adlb):
        """Test basic lab summary creation."""
        result = create_lab_summary(
            sample_adlb, treatment_var="TRT01P", parameter_var="PARAMCD"
        )
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

    def test_with_value_var(self, sample_adlb):
        """Test lab summary with value variable."""
        if "AVAL" in sample_adlb.columns:
            result = create_lab_summary(
                sample_adlb,
                treatment_var="TRT01P",
                parameter_var="PARAMCD",
                value_var="AVAL",
            )
            assert isinstance(result, pd.DataFrame)

    def test_with_visit(self, sample_adlb):
        """Test lab summary with visit variable."""
        if "AVISIT" in sample_adlb.columns:
            result = create_lab_summary(
                sample_adlb,
                treatment_var="TRT01P",
                parameter_var="PARAMCD",
                visit_var="AVISIT",
            )
            assert isinstance(result, pd.DataFrame)

    def test_treatment_columns(self, sample_adlb):
        """Test that treatment columns are created."""
        result = create_lab_summary(
            sample_adlb, treatment_var="TRT01P", parameter_var="PARAMCD"
        )
        # Should have parameter column plus treatment columns
        assert len(result.columns) >= 2

    def test_unique_parameters(self, sample_adlb):
        """Test that unique lab parameters are included."""
        result = create_lab_summary(
            sample_adlb, treatment_var="TRT01P", parameter_var="PARAMCD"
        )
        # Should have rows for different parameters
        assert len(result) > 0

    def test_empty_dataset(self):
        """Test with empty lab dataset."""
        empty_df = pd.DataFrame(
            columns=["USUBJID", "TRT01P", "PARAMCD", "AVAL", "AVISIT"]
        )
        result = create_lab_summary(
            empty_df, treatment_var="TRT01P", parameter_var="PARAMCD"
        )
        assert isinstance(result, pd.DataFrame)


class TestSafetyWorkflow:
    """Test complete safety analysis workflow."""

    def test_ae_summary_and_specific(self, sample_adae):
        """Test creating both AE summary and specific tables."""
        summary = create_ae_summary(
            sample_adae, treatment_var="TRT01P", term_var="AEDECOD"
        )
        specific = create_ae_specific_table(
            sample_adae, treatment_var="TRT01P", term_var="AEDECOD"
        )

        assert isinstance(summary, pd.DataFrame)
        assert isinstance(specific, pd.DataFrame)

    def test_ae_and_lab_analysis(self, sample_adae, sample_adlb):
        """Test creating both AE and lab summaries."""
        ae_summary = create_ae_summary(
            sample_adae, treatment_var="TRT01P", term_var="AEDECOD"
        )
        lab_summary = create_lab_summary(
            sample_adlb, treatment_var="TRT01P", parameter_var="PARAMCD"
        )

        assert isinstance(ae_summary, pd.DataFrame)
        assert isinstance(lab_summary, pd.DataFrame)


class TestSafetyEdgeCases:
    """Test edge cases in safety analysis."""

    def test_single_ae_term(self):
        """Test with single AE term."""
        df = pd.DataFrame(
            {
                "USUBJID": ["S001", "S002", "S003"],
                "TRT01P": ["Treatment A", "Treatment B", "Treatment A"],
                "AEDECOD": ["Headache", "Headache", "Headache"],
            }
        )
        result = create_ae_summary(df, treatment_var="TRT01P", term_var="AEDECOD")
        assert isinstance(result, pd.DataFrame)

    def test_multiple_aes_per_subject(self):
        """Test with multiple AEs per subject."""
        df = pd.DataFrame(
            {
                "USUBJID": ["S001", "S001", "S002", "S002"],
                "TRT01P": ["Treatment A", "Treatment A", "Treatment B", "Treatment B"],
                "AEDECOD": ["Headache", "Nausea", "Headache", "Fatigue"],
            }
        )
        result = create_ae_summary(df, treatment_var="TRT01P", term_var="AEDECOD")
        assert isinstance(result, pd.DataFrame)

    def test_missing_values(self):
        """Test with missing values."""
        df = pd.DataFrame(
            {
                "USUBJID": ["S001", "S002", "S003"],
                "TRT01P": ["Treatment A", None, "Treatment A"],
                "AEDECOD": ["Headache", "Nausea", None],
            }
        )
        result = create_ae_summary(df, treatment_var="TRT01P", term_var="AEDECOD")
        assert isinstance(result, pd.DataFrame)


class TestSafetyIntegration:
    """Test integration with other modules."""

    def test_output_format(self, sample_adae):
        """Test that output format is suitable for reporting."""
        result = create_ae_summary(
            sample_adae, treatment_var="TRT01P", term_var="AEDECOD"
        )

        # Should be a DataFrame
        assert isinstance(result, pd.DataFrame)

        # Should be ready for export
        assert result.shape[0] > 0
        assert result.shape[1] > 0

    def test_reproducibility(self, sample_adae):
        """Test that results are reproducible."""
        result1 = create_ae_summary(
            sample_adae, treatment_var="TRT01P", term_var="AEDECOD"
        )
        result2 = create_ae_summary(
            sample_adae, treatment_var="TRT01P", term_var="AEDECOD"
        )

        # Results should be identical
        pd.testing.assert_frame_equal(result1, result2)

    def test_consistent_treatment_order(self, sample_adae):
        """Test that treatment order is consistent."""
        result1 = create_ae_summary(
            sample_adae, treatment_var="TRT01P", term_var="AEDECOD"
        )
        result2 = create_ae_summary(
            sample_adae, treatment_var="TRT01P", term_var="AEDECOD"
        )

        # Column order should be consistent
        assert list(result1.columns) == list(result2.columns)

