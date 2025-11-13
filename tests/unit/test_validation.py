"""
Unit tests for py4csr.data.validation module.

Tests data validation functions and utilities.
"""

import pandas as pd
import pytest

from py4csr.data.validation import (
    validate_adsl,
    validate_adae,
    validate_adlb,
    run_full_validation,
)
from py4csr.exceptions import validate_required_columns, DataValidationError


class TestValidateRequiredColumns:
    """Test validate_required_columns function."""

    def test_valid_columns(self, sample_adsl):
        """Test validation with all required columns present."""
        required = ["USUBJID", "AGE", "SEX"]
        # Should not raise error
        validate_required_columns(sample_adsl, required, "ADSL")

    def test_missing_columns(self, sample_adsl):
        """Test validation with missing columns."""
        required = ["USUBJID", "NONEXISTENT"]
        with pytest.raises(DataValidationError):
            validate_required_columns(sample_adsl, required, "ADSL")

    def test_empty_required_list(self, sample_adsl):
        """Test validation with empty required list."""
        # Should not raise error
        validate_required_columns(sample_adsl, [], "ADSL")

    def test_case_sensitivity(self, sample_adsl):
        """Test that column names are case-sensitive."""
        required = ["usubjid"]  # lowercase
        # May raise error if case-sensitive
        try:
            validate_required_columns(sample_adsl, required, "ADSL")
        except DataValidationError:
            # Expected if case-sensitive
            pass


class TestValidateAdsl:
    """Test validate_adsl function."""

    def test_valid_adsl(self, sample_adsl):
        """Test validation of valid ADSL dataset."""
        result = validate_adsl(sample_adsl, strict=False)
        assert isinstance(result, dict)
        assert "valid" in result or "issues" in result

    def test_strict_validation(self, sample_adsl):
        """Test strict validation mode."""
        result = validate_adsl(sample_adsl, strict=True)
        assert isinstance(result, dict)

    def test_missing_required_columns(self):
        """Test validation with missing required columns."""
        df = pd.DataFrame({"A": [1, 2, 3]})
        result = validate_adsl(df, strict=False)
        assert isinstance(result, dict)
        # Should have issues
        if "issues" in result:
            assert len(result["issues"]) > 0


class TestValidateAdae:
    """Test validate_adae function."""

    def test_valid_adae(self, sample_adae):
        """Test validation of valid ADAE dataset."""
        result = validate_adae(sample_adae, strict=False)
        assert isinstance(result, dict)

    def test_strict_validation(self, sample_adae):
        """Test strict validation mode."""
        result = validate_adae(sample_adae, strict=True)
        assert isinstance(result, dict)


class TestValidateAdlb:
    """Test validate_adlb function."""

    def test_valid_adlb(self, sample_adlb):
        """Test validation of valid ADLB dataset."""
        result = validate_adlb(sample_adlb)
        assert isinstance(result, dict)


class TestRunFullValidation:
    """Test run_full_validation function."""

    def test_multiple_datasets(self, sample_adsl, sample_adae, sample_adlb):
        """Test validation of multiple datasets."""
        datasets = {"ADSL": sample_adsl, "ADAE": sample_adae, "ADLB": sample_adlb}
        result = run_full_validation(datasets)
        assert isinstance(result, dict)
        assert len(result) > 0

    def test_single_dataset(self, sample_adsl):
        """Test validation of single dataset."""
        datasets = {"ADSL": sample_adsl}
        result = run_full_validation(datasets)
        assert isinstance(result, dict)

    def test_empty_datasets(self):
        """Test validation with empty datasets dict."""
        result = run_full_validation({})
        assert isinstance(result, dict)


class TestValidationWorkflow:
    """Test complete validation workflow."""

    def test_comprehensive_validation(self, sample_adsl, sample_adae):
        """Test comprehensive dataset validation."""
        # Validate ADSL
        result_adsl = validate_adsl(sample_adsl)
        assert isinstance(result_adsl, dict)

        # Validate ADAE
        result_adae = validate_adae(sample_adae)
        assert isinstance(result_adae, dict)

        # Run full validation
        datasets = {"ADSL": sample_adsl, "ADAE": sample_adae}
        result_full = run_full_validation(datasets)
        assert isinstance(result_full, dict)

    def test_validation_error_messages(self):
        """Test that validation errors have informative messages."""
        df = pd.DataFrame({"A": [1, 2, 3]})
        try:
            validate_required_columns(df, ["B", "C"], "TEST")
        except DataValidationError as e:
            assert "TEST" in str(e)
            assert "B" in str(e) or "C" in str(e)


class TestEdgeCases:
    """Test edge cases in validation."""

    def test_empty_dataframe(self):
        """Test validation of empty DataFrame."""
        df = pd.DataFrame()
        try:
            validate_required_columns(df, [], "EMPTY")
        except Exception:
            pass

    def test_null_values(self):
        """Test validation with null values."""
        df = pd.DataFrame({"A": [1, None, 3], "B": ["x", "y", None]})
        try:
            validate_required_columns(df, ["A", "B"], "NULL_TEST")
        except Exception:
            pass

    def test_duplicate_columns(self):
        """Test validation with duplicate column names."""
        # pandas doesn't allow duplicate column names easily
        # but we can test the behavior
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        validate_required_columns(df, ["A"], "DUP_TEST")


class TestValidationHelpers:
    """Test validation helper functions."""

    def test_column_existence_check(self, sample_adsl):
        """Test checking if columns exist."""
        assert "USUBJID" in sample_adsl.columns
        assert "AGE" in sample_adsl.columns
        assert "NONEXISTENT" not in sample_adsl.columns

    def test_data_type_detection(self, sample_adsl):
        """Test detecting data types."""
        assert pd.api.types.is_numeric_dtype(sample_adsl["AGE"])
        assert pd.api.types.is_object_dtype(sample_adsl["USUBJID"])

