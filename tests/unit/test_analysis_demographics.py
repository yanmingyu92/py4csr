"""
Unit tests for py4csr.analysis.demographics module.

Tests demographics and baseline characteristics analysis.
"""

import pandas as pd
import pytest
import numpy as np

from py4csr.analysis.demographics import (
    create_demographics_table,
    summarize_baseline,
)


@pytest.fixture
def sample_demographics_data():
    """Create sample demographics data for testing."""
    return pd.DataFrame({
        "USUBJID": ["001", "002", "003", "004", "005", "006"],
        "TRT01P": ["Placebo", "Placebo", "Drug A", "Drug A", "Drug B", "Drug B"],
        "AGE": [65, 70, 68, 72, 66, 69],
        "SEX": ["M", "F", "M", "F", "M", "F"],
        "RACE": ["White", "White", "Black", "White", "Asian", "White"],
        "WEIGHT": [70.5, 65.2, 80.1, 68.5, 75.0, 62.3],
    })


class TestCreateDemographicsTable:
    """Test create_demographics_table function."""

    def test_basic_categorical(self, sample_demographics_data):
        """Test basic categorical variable."""
        result = create_demographics_table(
            data=sample_demographics_data,
            treatment_var="TRT01P",
            variables=["SEX"],
            categorical_vars=["SEX"],
            include_total=False,
            test_statistics=False,
        )

        assert "Variable" in result.columns
        assert "Category" in result.columns
        assert "Drug A" in result.columns
        assert "Drug B" in result.columns
        assert "Placebo" in result.columns
        assert len(result) == 2  # M and F

    def test_basic_continuous(self, sample_demographics_data):
        """Test basic continuous variable."""
        result = create_demographics_table(
            data=sample_demographics_data,
            treatment_var="TRT01P",
            variables=["AGE"],
            continuous_vars=["AGE"],
            include_total=False,
            test_statistics=False,
        )

        assert "Variable" in result.columns
        assert "Category" in result.columns
        assert result["Category"].iloc[0] == "Mean (SD)"
        assert len(result) == 1

    def test_with_total_column(self, sample_demographics_data):
        """Test including total column."""
        result = create_demographics_table(
            data=sample_demographics_data,
            treatment_var="TRT01P",
            variables=["SEX"],
            categorical_vars=["SEX"],
            include_total=True,
            test_statistics=False,
        )

        assert "Total" in result.columns

    def test_with_test_statistics(self, sample_demographics_data):
        """Test including test statistics."""
        result = create_demographics_table(
            data=sample_demographics_data,
            treatment_var="TRT01P",
            variables=["SEX"],
            categorical_vars=["SEX"],
            include_total=False,
            test_statistics=True,
        )

        assert "P-value" in result.columns

    def test_multiple_variables(self, sample_demographics_data):
        """Test multiple variables."""
        result = create_demographics_table(
            data=sample_demographics_data,
            treatment_var="TRT01P",
            variables=["SEX", "AGE"],
            categorical_vars=["SEX"],
            continuous_vars=["AGE"],
            include_total=False,
            test_statistics=False,
        )

        assert len(result) == 3  # 2 for SEX (M, F) + 1 for AGE

    def test_categorical_percentages(self, sample_demographics_data):
        """Test categorical variable percentages."""
        result = create_demographics_table(
            data=sample_demographics_data,
            treatment_var="TRT01P",
            variables=["SEX"],
            categorical_vars=["SEX"],
            include_total=False,
            test_statistics=False,
        )

        # Check that percentages are formatted correctly
        assert "%" in result["Placebo"].iloc[0]

    def test_continuous_mean_sd(self, sample_demographics_data):
        """Test continuous variable mean and SD."""
        result = create_demographics_table(
            data=sample_demographics_data,
            treatment_var="TRT01P",
            variables=["AGE"],
            continuous_vars=["AGE"],
            include_total=False,
            test_statistics=False,
        )

        # Check that mean and SD are formatted correctly
        assert "(" in result["Placebo"].iloc[0]
        assert ")" in result["Placebo"].iloc[0]

    def test_empty_variables(self, sample_demographics_data):
        """Test with empty variables list."""
        result = create_demographics_table(
            data=sample_demographics_data,
            treatment_var="TRT01P",
            variables=[],
            include_total=False,
            test_statistics=False,
        )

        assert len(result) == 0

    def test_nonexistent_variable(self, sample_demographics_data):
        """Test with nonexistent variable."""
        result = create_demographics_table(
            data=sample_demographics_data,
            treatment_var="TRT01P",
            variables=["NONEXISTENT"],
            categorical_vars=["NONEXISTENT"],
            include_total=False,
            test_statistics=False,
        )

        # Should skip nonexistent variable
        assert len(result) == 0

    def test_missing_data_handling(self):
        """Test handling of missing data."""
        data = pd.DataFrame({
            "USUBJID": ["001", "002", "003", "004"],
            "TRT01P": ["Placebo", "Placebo", "Drug A", "Drug A"],
            "SEX": ["M", np.nan, "F", "M"],
        })

        result = create_demographics_table(
            data=data,
            treatment_var="TRT01P",
            variables=["SEX"],
            categorical_vars=["SEX"],
            include_total=False,
            test_statistics=False,
        )

        # Should handle missing data gracefully
        assert len(result) >= 1

    def test_all_options_enabled(self, sample_demographics_data):
        """Test with all options enabled."""
        result = create_demographics_table(
            data=sample_demographics_data,
            treatment_var="TRT01P",
            variables=["SEX", "AGE", "WEIGHT"],
            categorical_vars=["SEX"],
            continuous_vars=["AGE", "WEIGHT"],
            include_total=True,
            test_statistics=True,
        )

        assert "Total" in result.columns
        assert "P-value" in result.columns
        assert len(result) == 4  # 2 for SEX + 1 for AGE + 1 for WEIGHT


class TestSummarizeBaseline:
    """Test summarize_baseline function."""

    def test_basic_summary(self, sample_demographics_data):
        """Test basic baseline summary."""
        result = summarize_baseline(
            data=sample_demographics_data,
            variables=["AGE", "SEX"],
            categorical_vars=["SEX"],
            continuous_vars=["AGE"],
        )

        assert "AGE" in result
        assert "SEX" in result
        assert result["AGE"]["type"] == "continuous"
        assert result["SEX"]["type"] == "categorical"

    def test_continuous_statistics(self, sample_demographics_data):
        """Test continuous variable statistics."""
        result = summarize_baseline(
            data=sample_demographics_data,
            variables=["AGE"],
            continuous_vars=["AGE"],
        )

        assert "n" in result["AGE"]
        assert "mean" in result["AGE"]
        assert "std" in result["AGE"]
        assert "median" in result["AGE"]
        assert "min" in result["AGE"]
        assert "max" in result["AGE"]
        assert "missing" in result["AGE"]

    def test_categorical_statistics(self, sample_demographics_data):
        """Test categorical variable statistics."""
        result = summarize_baseline(
            data=sample_demographics_data,
            variables=["SEX"],
            categorical_vars=["SEX"],
        )

        assert "counts" in result["SEX"]
        assert "missing" in result["SEX"]
        assert isinstance(result["SEX"]["counts"], dict)

    def test_auto_detect_categorical(self, sample_demographics_data):
        """Test auto-detection of categorical variables."""
        result = summarize_baseline(
            data=sample_demographics_data,
            variables=["SEX"],
        )

        # SEX should be auto-detected as categorical
        assert result["SEX"]["type"] == "categorical"

    def test_auto_detect_continuous(self):
        """Test auto-detection of continuous variables."""
        # Create data with many unique values to trigger continuous detection
        data = pd.DataFrame({
            "USUBJID": [f"{i:03d}" for i in range(1, 21)],
            "HEIGHT": np.random.uniform(150, 190, 20),  # Many unique values
        })

        result = summarize_baseline(
            data=data,
            variables=["HEIGHT"],
        )

        # HEIGHT should be auto-detected as continuous (more than 10 unique values)
        assert result["HEIGHT"]["type"] == "continuous"

    def test_multiple_variables(self, sample_demographics_data):
        """Test multiple variables."""
        result = summarize_baseline(
            data=sample_demographics_data,
            variables=["AGE", "SEX", "WEIGHT"],
        )

        assert len(result) == 3
        assert "AGE" in result
        assert "SEX" in result
        assert "WEIGHT" in result

    def test_missing_data_count(self):
        """Test missing data counting."""
        data = pd.DataFrame({
            "USUBJID": ["001", "002", "003", "004"],
            "AGE": [65, np.nan, 70, 68],
            "SEX": ["M", "F", np.nan, "M"],
        })

        result = summarize_baseline(
            data=data,
            variables=["AGE", "SEX"],
        )

        assert result["AGE"]["missing"] == 1
        assert result["SEX"]["missing"] == 1

    def test_empty_variables(self, sample_demographics_data):
        """Test with empty variables list."""
        result = summarize_baseline(
            data=sample_demographics_data,
            variables=[],
        )

        assert len(result) == 0

    def test_categorical_value_counts(self, sample_demographics_data):
        """Test categorical value counts."""
        result = summarize_baseline(
            data=sample_demographics_data,
            variables=["SEX"],
            categorical_vars=["SEX"],
        )

        counts = result["SEX"]["counts"]
        assert "M" in counts
        assert "F" in counts
        assert counts["M"] == 3
        assert counts["F"] == 3

