"""
Unit tests for py4csr.functional.advanced_utilities module.

Tests advanced utility functions for string manipulation, date processing,
and numeric formatting.
"""

import pandas as pd
import pytest
import numpy as np
from datetime import datetime, timedelta

from py4csr.functional.advanced_utilities import (
    AdvancedUtilities,
    manipulate_strings,
    process_dates,
    format_numbers,
)


@pytest.fixture
def sample_string_data():
    """Create sample data for string manipulation tests."""
    return pd.DataFrame({
        "NAME": ["  john doe  ", "JANE SMITH", "bob jones"],
        "CITY": ["new york", "LOS ANGELES", "chicago"],
        "CODE": ["ABC-123", "DEF-456", "GHI-789"],
        "NOTES": ["Test  note  1", "Test note 2", "Test note 3"],
    })


@pytest.fixture
def sample_date_data():
    """Create sample data for date processing tests."""
    return pd.DataFrame({
        "BIRTH_DATE": pd.to_datetime(["1980-01-15", "1975-06-20", "1990-12-10"]),
        "ENROLL_DATE": pd.to_datetime(["2020-01-01", "2020-02-15", "2020-03-20"]),
        "END_DATE": pd.to_datetime(["2020-12-31", "2021-02-15", "2021-03-20"]),
        "USUBJID": ["001", "002", "003"],
    })


@pytest.fixture
def sample_numeric_data():
    """Create sample data for numeric formatting tests."""
    return pd.DataFrame({
        "AGE": [45.678, 50.123, 35.456],
        "WEIGHT": [75.5, 82.3, 68.9],
        "BMI": [25.678, 28.123, 22.456],
        "PVALUE": [0.0123, 0.0456, 0.0789],
    })


class TestAdvancedStringManipulation:
    """Test advanced_string_manipulation method."""

    def test_standardize_case_upper(self, sample_string_data):
        """Test standardizing case to upper."""
        operations = [
            {"column": "NAME", "operation": "standardize_case", "case": "upper"}
        ]

        result = AdvancedUtilities.advanced_string_manipulation(
            sample_string_data, operations
        )

        assert result["NAME"].iloc[0] == "  JOHN DOE  "
        assert result["NAME"].iloc[1] == "JANE SMITH"

    def test_standardize_case_lower(self, sample_string_data):
        """Test standardizing case to lower."""
        operations = [
            {"column": "CITY", "operation": "standardize_case", "case": "lower"}
        ]

        result = AdvancedUtilities.advanced_string_manipulation(
            sample_string_data, operations
        )

        assert result["CITY"].iloc[0] == "new york"
        assert result["CITY"].iloc[1] == "los angeles"

    def test_standardize_case_title(self, sample_string_data):
        """Test standardizing case to title."""
        operations = [
            {"column": "NAME", "operation": "standardize_case", "case": "title"}
        ]

        result = AdvancedUtilities.advanced_string_manipulation(
            sample_string_data, operations
        )

        assert "John Doe" in result["NAME"].iloc[0]

    def test_clean_whitespace(self, sample_string_data):
        """Test cleaning whitespace."""
        operations = [
            {"column": "NAME", "operation": "clean_whitespace"}
        ]

        result = AdvancedUtilities.advanced_string_manipulation(
            sample_string_data, operations
        )

        assert result["NAME"].iloc[0] == "john doe"
        assert "  " not in result["NAME"].iloc[0]

    def test_extract_pattern(self, sample_string_data):
        """Test extracting pattern."""
        operations = [
            {
                "column": "CODE",
                "operation": "extract_pattern",
                "pattern": r"([A-Z]+)",
                "new_column": "LETTERS",
            }
        ]

        result = AdvancedUtilities.advanced_string_manipulation(
            sample_string_data, operations
        )

        assert "LETTERS" in result.columns
        assert result["LETTERS"].iloc[0] == "ABC"

    def test_concatenate(self, sample_string_data):
        """Test concatenating columns."""
        operations = [
            {
                "column": "NAME",
                "operation": "concatenate",
                "other_columns": ["CITY"],
                "separator": " - ",
                "new_column": "NAME_CITY",
            }
        ]

        result = AdvancedUtilities.advanced_string_manipulation(
            sample_string_data, operations
        )

        assert "NAME_CITY" in result.columns
        assert " - " in result["NAME_CITY"].iloc[0]

    def test_multiple_operations(self, sample_string_data):
        """Test multiple operations in sequence."""
        operations = [
            {"column": "NAME", "operation": "clean_whitespace"},
            {"column": "NAME", "operation": "standardize_case", "case": "upper"},
        ]

        result = AdvancedUtilities.advanced_string_manipulation(
            sample_string_data, operations
        )

        assert result["NAME"].iloc[0] == "JOHN DOE"

    def test_nonexistent_column(self, sample_string_data):
        """Test operation on nonexistent column."""
        operations = [
            {"column": "NONEXISTENT", "operation": "standardize_case", "case": "upper"}
        ]

        result = AdvancedUtilities.advanced_string_manipulation(
            sample_string_data, operations
        )

        # Should not crash, just skip the operation
        assert "NONEXISTENT" not in result.columns


class TestAdvancedDateProcessing:
    """Test advanced_date_processing method."""

    def test_extract_components(self, sample_date_data):
        """Test extracting date components."""
        operations = [
            {"column": "BIRTH_DATE", "operation": "extract_components"}
        ]

        result = AdvancedUtilities.advanced_date_processing(
            sample_date_data, operations
        )

        assert "BIRTH_DATE_year" in result.columns
        assert "BIRTH_DATE_month" in result.columns
        assert "BIRTH_DATE_day" in result.columns
        assert "BIRTH_DATE_weekday" in result.columns
        assert result["BIRTH_DATE_year"].iloc[0] == 1980
        assert result["BIRTH_DATE_month"].iloc[0] == 1
        assert result["BIRTH_DATE_day"].iloc[0] == 15

    def test_calculate_age(self, sample_date_data):
        """Test calculating age."""
        reference_date = datetime(2020, 1, 1)
        operations = [
            {
                "column": "BIRTH_DATE",
                "operation": "calculate_age",
                "reference_date": reference_date,
                "age_column": "AGE",
            }
        ]

        result = AdvancedUtilities.advanced_date_processing(
            sample_date_data, operations
        )

        assert "AGE" in result.columns
        assert result["AGE"].iloc[0] > 39  # Born 1980, reference 2020
        assert result["AGE"].iloc[0] < 41

    def test_calculate_age_string_reference(self, sample_date_data):
        """Test calculating age with string reference date."""
        operations = [
            {
                "column": "BIRTH_DATE",
                "operation": "calculate_age",
                "reference_date": "2020-01-01",
                "age_column": "AGE",
            }
        ]

        result = AdvancedUtilities.advanced_date_processing(
            sample_date_data, operations
        )

        assert "AGE" in result.columns
        assert result["AGE"].iloc[0] > 39

    def test_calculate_duration_days(self, sample_date_data):
        """Test calculating duration in days."""
        operations = [
            {
                "column": "ENROLL_DATE",
                "operation": "calculate_duration",
                "end_column": "END_DATE",
                "duration_column": "DURATION_DAYS",
                "unit": "days",
            }
        ]

        result = AdvancedUtilities.advanced_date_processing(
            sample_date_data, operations
        )

        assert "DURATION_DAYS" in result.columns
        assert result["DURATION_DAYS"].iloc[0] > 360  # About 1 year

    def test_calculate_duration_weeks(self, sample_date_data):
        """Test calculating duration in weeks."""
        operations = [
            {
                "column": "ENROLL_DATE",
                "operation": "calculate_duration",
                "end_column": "END_DATE",
                "duration_column": "DURATION_WEEKS",
                "unit": "weeks",
            }
        ]

        result = AdvancedUtilities.advanced_date_processing(
            sample_date_data, operations
        )

        assert "DURATION_WEEKS" in result.columns
        assert result["DURATION_WEEKS"].iloc[0] > 50  # About 52 weeks

    def test_calculate_duration_months(self, sample_date_data):
        """Test calculating duration in months."""
        operations = [
            {
                "column": "ENROLL_DATE",
                "operation": "calculate_duration",
                "end_column": "END_DATE",
                "duration_column": "DURATION_MONTHS",
                "unit": "months",
            }
        ]

        result = AdvancedUtilities.advanced_date_processing(
            sample_date_data, operations
        )

        assert "DURATION_MONTHS" in result.columns
        assert result["DURATION_MONTHS"].iloc[0] > 11  # About 12 months

    def test_calculate_duration_years(self, sample_date_data):
        """Test calculating duration in years."""
        operations = [
            {
                "column": "ENROLL_DATE",
                "operation": "calculate_duration",
                "end_column": "END_DATE",
                "duration_column": "DURATION_YEARS",
                "unit": "years",
            }
        ]

        result = AdvancedUtilities.advanced_date_processing(
            sample_date_data, operations
        )

        assert "DURATION_YEARS" in result.columns
        assert result["DURATION_YEARS"].iloc[0] > 0.9  # About 1 year

    def test_nonexistent_column(self, sample_date_data):
        """Test operation on nonexistent column."""
        operations = [
            {"column": "NONEXISTENT", "operation": "extract_components"}
        ]

        result = AdvancedUtilities.advanced_date_processing(
            sample_date_data, operations
        )

        # Should not crash, just skip the operation
        assert "NONEXISTENT_year" not in result.columns


class TestAdvancedNumericFormatting:
    """Test advanced_numeric_formatting method."""

    def test_standard_formatting(self, sample_numeric_data):
        """Test standard numeric formatting."""
        rules = {
            "AGE": {"decimal_places": 1, "format_type": "standard"}
        }

        result = AdvancedUtilities.advanced_numeric_formatting(
            sample_numeric_data, rules
        )

        assert result["AGE"].iloc[0] == 45.7
        assert result["AGE"].iloc[1] == 50.1

    def test_percentage_formatting(self, sample_numeric_data):
        """Test percentage formatting."""
        rules = {
            "PVALUE": {"decimal_places": 2, "format_type": "percentage"}
        }

        result = AdvancedUtilities.advanced_numeric_formatting(
            sample_numeric_data, rules
        )

        assert "%" in result["PVALUE"].iloc[0]
        assert "1.23%" == result["PVALUE"].iloc[0]

    def test_scientific_formatting(self, sample_numeric_data):
        """Test scientific notation formatting."""
        rules = {
            "PVALUE": {"decimal_places": 3, "format_type": "scientific"}
        }

        result = AdvancedUtilities.advanced_numeric_formatting(
            sample_numeric_data, rules
        )

        assert "e" in result["PVALUE"].iloc[0]

    def test_clinical_range_mean_std(self, sample_numeric_data):
        """Test clinical range formatting with mean ± std."""
        rules = {
            "AGE": {
                "decimal_places": 1,
                "format_type": "clinical_range",
                "summary_type": "mean_std",
            }
        }

        result = AdvancedUtilities.advanced_numeric_formatting(
            sample_numeric_data, rules
        )

        assert "AGE_formatted" in result.columns
        assert "±" in result["AGE_formatted"].iloc[0]

    def test_clinical_range_median_iqr(self, sample_numeric_data):
        """Test clinical range formatting with median (Q1, Q3)."""
        rules = {
            "AGE": {
                "decimal_places": 1,
                "format_type": "clinical_range",
                "summary_type": "median_iqr",
            }
        }

        result = AdvancedUtilities.advanced_numeric_formatting(
            sample_numeric_data, rules
        )

        assert "AGE_formatted" in result.columns
        assert "(" in result["AGE_formatted"].iloc[0]
        assert ")" in result["AGE_formatted"].iloc[0]

    def test_multiple_columns(self, sample_numeric_data):
        """Test formatting multiple columns."""
        rules = {
            "AGE": {"decimal_places": 0, "format_type": "standard"},
            "WEIGHT": {"decimal_places": 1, "format_type": "standard"},
        }

        result = AdvancedUtilities.advanced_numeric_formatting(
            sample_numeric_data, rules
        )

        assert result["AGE"].iloc[0] == 46.0
        assert result["WEIGHT"].iloc[0] == 75.5

    def test_nonexistent_column(self, sample_numeric_data):
        """Test formatting nonexistent column."""
        rules = {
            "NONEXISTENT": {"decimal_places": 2, "format_type": "standard"}
        }

        result = AdvancedUtilities.advanced_numeric_formatting(
            sample_numeric_data, rules
        )

        # Should not crash, just skip the operation
        assert "NONEXISTENT" not in result.columns


class TestFunctionalInterfaces:
    """Test functional interface functions."""

    def test_manipulate_strings(self, sample_string_data):
        """Test manipulate_strings function."""
        operations = [
            {"column": "NAME", "operation": "clean_whitespace"}
        ]

        result = manipulate_strings(sample_string_data, operations)

        assert result["NAME"].iloc[0] == "john doe"

    def test_process_dates(self, sample_date_data):
        """Test process_dates function."""
        operations = [
            {"column": "BIRTH_DATE", "operation": "extract_components"}
        ]

        result = process_dates(sample_date_data, operations)

        assert "BIRTH_DATE_year" in result.columns

    def test_format_numbers(self, sample_numeric_data):
        """Test format_numbers function."""
        rules = {
            "AGE": {"decimal_places": 1, "format_type": "standard"}
        }

        result = format_numbers(sample_numeric_data, rules)

        assert result["AGE"].iloc[0] == 45.7


class TestEdgeCases:
    """Test edge cases."""

    def test_empty_operations(self, sample_string_data):
        """Test with empty operations list."""
        result = AdvancedUtilities.advanced_string_manipulation(
            sample_string_data, []
        )

        assert result.equals(sample_string_data)

    def test_empty_rules(self, sample_numeric_data):
        """Test with empty formatting rules."""
        result = AdvancedUtilities.advanced_numeric_formatting(
            sample_numeric_data, {}
        )

        assert result.equals(sample_numeric_data)

    def test_string_dates_conversion(self):
        """Test automatic conversion of string dates."""
        data = pd.DataFrame({
            "DATE_STR": ["2020-01-01", "2020-02-15", "2020-03-20"],
        })

        operations = [
            {"column": "DATE_STR", "operation": "extract_components"}
        ]

        result = AdvancedUtilities.advanced_date_processing(data, operations)

        assert "DATE_STR_year" in result.columns
        assert result["DATE_STR_year"].iloc[0] == 2020

    def test_null_values_in_numeric_formatting(self):
        """Test handling null values in numeric formatting."""
        data = pd.DataFrame({
            "VALUE": [1.234, np.nan, 3.456],
        })

        rules = {
            "VALUE": {"decimal_places": 2, "format_type": "scientific"}
        }

        result = AdvancedUtilities.advanced_numeric_formatting(data, rules)

        assert result["VALUE"].iloc[1] == ""  # NaN should be empty string

