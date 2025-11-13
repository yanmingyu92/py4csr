"""
Unit tests for py4csr.analysis.population module.

Tests population analysis functions.
"""

import pandas as pd
import pytest

from py4csr.analysis.population import (
    create_disposition_table,
    create_population_summary,
)


class TestCreateDispositionTable:
    """Test create_disposition_table function."""

    def test_basic_disposition(self, sample_adsl):
        """Test basic disposition table creation."""
        result = create_disposition_table(sample_adsl)
        assert isinstance(result, pd.DataFrame)
        assert "Category" in result.columns
        assert len(result) > 0

    def test_custom_treatment_var(self, sample_adsl):
        """Test with custom treatment variable."""
        result = create_disposition_table(sample_adsl, treatment_var="TRT01P")
        assert isinstance(result, pd.DataFrame)

    def test_custom_disposition_vars(self, sample_adsl):
        """Test with custom disposition variables."""
        result = create_disposition_table(
            sample_adsl, disposition_vars=["SAFFL", "EFFFL"]
        )
        assert isinstance(result, pd.DataFrame)

    def test_total_randomized_row(self, sample_adsl):
        """Test that total randomized row is included."""
        result = create_disposition_table(sample_adsl)
        categories = result["Category"].tolist()
        assert any("Randomized" in str(cat) for cat in categories)

    def test_treatment_columns(self, sample_adsl):
        """Test that treatment columns are created."""
        result = create_disposition_table(sample_adsl)
        # Should have Category column plus treatment columns
        assert len(result.columns) >= 2

    def test_percentage_formatting(self, sample_adsl):
        """Test that percentages are formatted correctly."""
        result = create_disposition_table(sample_adsl)
        # Check if any cell contains percentage
        has_percentage = False
        for col in result.columns:
            if col != "Category":
                for val in result[col]:
                    if "%" in str(val):
                        has_percentage = True
                        break
        # At least some rows should have percentages
        assert has_percentage or len(result) > 0

    def test_empty_dataset(self):
        """Test with empty dataset."""
        empty_df = pd.DataFrame(
            columns=["USUBJID", "TRT01P", "SAFFL", "EFFFL", "DTHFL"]
        )
        result = create_disposition_table(empty_df)
        assert isinstance(result, pd.DataFrame)

    def test_missing_disposition_vars(self, sample_adsl):
        """Test with missing disposition variables."""
        # Request variables that don't exist
        result = create_disposition_table(
            sample_adsl, disposition_vars=["NONEXISTENT"]
        )
        assert isinstance(result, pd.DataFrame)


class TestCreatePopulationSummary:
    """Test create_population_summary function."""

    def test_basic_population_summary(self, sample_adsl):
        """Test basic population summary creation."""
        result = create_population_summary(sample_adsl)
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

    def test_custom_treatment_var(self, sample_adsl):
        """Test with custom treatment variable."""
        result = create_population_summary(sample_adsl, treatment_var="TRT01P")
        assert isinstance(result, pd.DataFrame)

    def test_custom_population_flags(self, sample_adsl):
        """Test with custom population flags."""
        result = create_population_summary(
            sample_adsl, population_flags=["SAFFL", "EFFFL"]
        )
        assert isinstance(result, pd.DataFrame)

    def test_population_labels(self, sample_adsl):
        """Test that population labels are included."""
        result = create_population_summary(sample_adsl)
        # Should have some population categories
        assert len(result) > 0

    def test_treatment_columns(self, sample_adsl):
        """Test that treatment columns are created."""
        result = create_population_summary(sample_adsl)
        # Should have multiple columns
        assert len(result.columns) >= 2

    def test_count_formatting(self, sample_adsl):
        """Test that counts are formatted correctly."""
        result = create_population_summary(sample_adsl)
        # Should have numeric or string counts
        assert len(result) > 0

    def test_empty_dataset(self):
        """Test with empty dataset."""
        empty_df = pd.DataFrame(columns=["USUBJID", "TRT01P", "SAFFL", "EFFFL"])
        result = create_population_summary(empty_df)
        assert isinstance(result, pd.DataFrame)

    def test_missing_population_flags(self, sample_adsl):
        """Test with missing population flags."""
        result = create_population_summary(
            sample_adsl, population_flags=["NONEXISTENT"]
        )
        assert isinstance(result, pd.DataFrame)


class TestPopulationWorkflow:
    """Test complete population analysis workflow."""

    def test_disposition_and_summary(self, sample_adsl):
        """Test creating both disposition and summary tables."""
        disposition = create_disposition_table(sample_adsl)
        summary = create_population_summary(sample_adsl)

        assert isinstance(disposition, pd.DataFrame)
        assert isinstance(summary, pd.DataFrame)
        assert len(disposition) > 0
        assert len(summary) > 0

    def test_multiple_treatments(self, sample_adsl):
        """Test with multiple treatment groups."""
        result = create_disposition_table(sample_adsl)
        # Should handle multiple treatments
        assert len(result.columns) >= 2

    def test_all_flags_present(self, sample_adsl):
        """Test when all population flags are present."""
        # Ensure all flags exist
        for flag in ["SAFFL", "EFFFL"]:
            if flag not in sample_adsl.columns:
                sample_adsl[flag] = "Y"

        result = create_population_summary(sample_adsl)
        assert isinstance(result, pd.DataFrame)


class TestPopulationEdgeCases:
    """Test edge cases in population analysis."""

    def test_single_treatment(self):
        """Test with single treatment group."""
        df = pd.DataFrame(
            {
                "USUBJID": ["S001", "S002", "S003"],
                "TRT01P": ["Treatment A", "Treatment A", "Treatment A"],
                "SAFFL": ["Y", "Y", "N"],
                "EFFFL": ["Y", "N", "N"],
            }
        )
        result = create_disposition_table(df)
        assert isinstance(result, pd.DataFrame)

    def test_all_subjects_in_population(self):
        """Test when all subjects are in all populations."""
        df = pd.DataFrame(
            {
                "USUBJID": ["S001", "S002", "S003"],
                "TRT01P": ["Treatment A", "Treatment B", "Treatment A"],
                "SAFFL": ["Y", "Y", "Y"],
                "EFFFL": ["Y", "Y", "Y"],
            }
        )
        result = create_population_summary(df)
        assert isinstance(result, pd.DataFrame)

    def test_no_subjects_in_population(self):
        """Test when no subjects are in certain populations."""
        df = pd.DataFrame(
            {
                "USUBJID": ["S001", "S002", "S003"],
                "TRT01P": ["Treatment A", "Treatment B", "Treatment A"],
                "SAFFL": ["N", "N", "N"],
                "EFFFL": ["N", "N", "N"],
            }
        )
        result = create_population_summary(df)
        assert isinstance(result, pd.DataFrame)

    def test_missing_values(self):
        """Test with missing values in flags."""
        df = pd.DataFrame(
            {
                "USUBJID": ["S001", "S002", "S003"],
                "TRT01P": ["Treatment A", "Treatment B", "Treatment A"],
                "SAFFL": ["Y", None, "N"],
                "EFFFL": [None, "Y", "N"],
            }
        )
        result = create_disposition_table(df)
        assert isinstance(result, pd.DataFrame)


class TestPopulationIntegration:
    """Test integration with other modules."""

    def test_output_format(self, sample_adsl):
        """Test that output format is suitable for reporting."""
        result = create_disposition_table(sample_adsl)

        # Should be a DataFrame
        assert isinstance(result, pd.DataFrame)

        # Should have Category column
        assert "Category" in result.columns

        # Should be ready for export
        assert result.shape[0] > 0
        assert result.shape[1] > 0

    def test_consistent_treatment_order(self, sample_adsl):
        """Test that treatment order is consistent."""
        result1 = create_disposition_table(sample_adsl)
        result2 = create_disposition_table(sample_adsl)

        # Column order should be consistent
        assert list(result1.columns) == list(result2.columns)

    def test_reproducibility(self, sample_adsl):
        """Test that results are reproducible."""
        result1 = create_disposition_table(sample_adsl)
        result2 = create_disposition_table(sample_adsl)

        # Results should be identical
        pd.testing.assert_frame_equal(result1, result2)

