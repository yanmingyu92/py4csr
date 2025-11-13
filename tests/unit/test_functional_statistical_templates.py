"""
Tests for functional/statistical_templates.py module.
"""

import numpy as np
import pandas as pd
import pytest

from py4csr.functional.config import FunctionalConfig, StatisticDefinition
from py4csr.functional.statistical_templates import StatisticalTemplates


@pytest.fixture
def sample_config():
    """Create sample functional configuration."""
    return FunctionalConfig.clinical_standard()


@pytest.fixture
def sample_continuous_data():
    """Create sample continuous data."""
    return pd.DataFrame({
        "AGE": [25, 30, 35, 40, 45, 50, 55, 60, 65, 70],
        "TRT": [1, 1, 1, 1, 1, 2, 2, 2, 2, 2],
        "WEIGHT": [60.5, 65.2, 70.1, 75.3, 80.0, 62.1, 68.5, 72.0, 78.5, 85.2]
    })


@pytest.fixture
def sample_categorical_data():
    """Create sample categorical data."""
    return pd.DataFrame({
        "SEX": ["M", "F", "M", "F", "M", "F", "M", "F", "M", "F"],
        "TRT": [1, 1, 1, 1, 1, 2, 2, 2, 2, 2],
        "RACE": ["White", "White", "Black", "Asian", "White", "Black", "White", "Asian", "Black", "White"]
    })


class TestStatisticalTemplatesInit:
    """Test StatisticalTemplates initialization."""

    def test_init_with_config(self, sample_config):
        """Test initialization with configuration."""
        templates = StatisticalTemplates(sample_config)
        
        assert templates.config == sample_config
        assert hasattr(templates, "_format_functions")
        assert isinstance(templates._format_functions, dict)


class TestContinuousStatistics:
    """Test continuous variable statistics calculation."""

    def test_calculate_continuous_basic(self, sample_config, sample_continuous_data):
        """Test basic continuous statistics calculation."""
        templates = StatisticalTemplates(sample_config)
        
        result = templates.calculate_continuous_statistics(
            sample_continuous_data,
            "AGE",
            "TRT",
            statistics=["n", "mean", "std"]
        )
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert "TREATMENT" in result.columns
        assert "VARIABLE" in result.columns
        assert "STATISTIC" in result.columns
        assert "VALUE" in result.columns
        assert "FORMATTED_VALUE" in result.columns

    def test_calculate_continuous_all_statistics(self, sample_config, sample_continuous_data):
        """Test continuous statistics with all stat types."""
        templates = StatisticalTemplates(sample_config)
        
        result = templates.calculate_continuous_statistics(
            sample_continuous_data,
            "AGE",
            "TRT",
            statistics=["n", "mean", "std", "median", "min", "max", "q1", "q3"]
        )
        
        assert len(result) > 0
        # Should have results for each treatment + Total
        treatments = result["TREATMENT"].unique()
        assert len(treatments) >= 2  # At least 2 treatments

    def test_calculate_continuous_combined_stats(self, sample_config, sample_continuous_data):
        """Test continuous statistics with combined statistics."""
        templates = StatisticalTemplates(sample_config)
        
        result = templates.calculate_continuous_statistics(
            sample_continuous_data,
            "AGE",
            "TRT",
            statistics=["mean_sd", "min_max", "q1_q3"]
        )
        
        assert len(result) > 0
        # Check that combined statistics return tuples
        for _, row in result.iterrows():
            if row["STATISTIC"] in ["Mean (SD)", "Min, Max", "Q1, Q3"]:
                assert isinstance(row["VALUE"], tuple) or isinstance(row["VALUE"], str)

    def test_calculate_continuous_missing_variable(self, sample_config, sample_continuous_data):
        """Test continuous statistics with missing variable."""
        templates = StatisticalTemplates(sample_config)
        
        with pytest.raises(ValueError, match="Variable 'MISSING' not found"):
            templates.calculate_continuous_statistics(
                sample_continuous_data,
                "MISSING",
                "TRT"
            )

    def test_calculate_continuous_missing_treatment(self, sample_config, sample_continuous_data):
        """Test continuous statistics with missing treatment variable."""
        templates = StatisticalTemplates(sample_config)
        
        with pytest.raises(ValueError, match="Treatment variable 'MISSING' not found"):
            templates.calculate_continuous_statistics(
                sample_continuous_data,
                "AGE",
                "MISSING"
            )

    def test_calculate_continuous_default_statistics(self, sample_config, sample_continuous_data):
        """Test continuous statistics with default statistics."""
        templates = StatisticalTemplates(sample_config)
        
        result = templates.calculate_continuous_statistics(
            sample_continuous_data,
            "AGE",
            "TRT"
        )
        
        assert len(result) > 0
        # Should use default statistics from config

    def test_calculate_continuous_with_missing_data(self, sample_config):
        """Test continuous statistics with missing data."""
        templates = StatisticalTemplates(sample_config)
        
        data = pd.DataFrame({
            "AGE": [25, 30, np.nan, 40, 45],
            "TRT": [1, 1, 1, 2, 2]
        })
        
        result = templates.calculate_continuous_statistics(
            data,
            "AGE",
            "TRT",
            statistics=["n", "mean"]
        )
        
        assert len(result) > 0
        # Missing values should be excluded


class TestCategoricalStatistics:
    """Test categorical variable statistics calculation."""

    def test_calculate_categorical_basic(self, sample_config, sample_categorical_data):
        """Test basic categorical statistics calculation."""
        templates = StatisticalTemplates(sample_config)
        
        result = templates.calculate_categorical_statistics(
            sample_categorical_data,
            "SEX",
            "TRT",
            statistics=["n", "pct"]
        )
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert "TREATMENT" in result.columns
        assert "VARIABLE" in result.columns
        assert "CATEGORY" in result.columns or "STATISTIC" in result.columns

    def test_calculate_categorical_missing_variable(self, sample_config, sample_categorical_data):
        """Test categorical statistics with missing variable."""
        templates = StatisticalTemplates(sample_config)
        
        with pytest.raises(ValueError, match="Variable 'MISSING' not found"):
            templates.calculate_categorical_statistics(
                sample_categorical_data,
                "MISSING",
                "TRT"
            )

    def test_calculate_categorical_missing_treatment(self, sample_config, sample_categorical_data):
        """Test categorical statistics with missing treatment variable."""
        templates = StatisticalTemplates(sample_config)
        
        with pytest.raises(ValueError, match="Treatment variable 'MISSING' not found"):
            templates.calculate_categorical_statistics(
                sample_categorical_data,
                "SEX",
                "MISSING"
            )

    def test_calculate_categorical_default_statistics(self, sample_config, sample_categorical_data):
        """Test categorical statistics with default statistics."""
        templates = StatisticalTemplates(sample_config)
        
        result = templates.calculate_categorical_statistics(
            sample_categorical_data,
            "SEX",
            "TRT"
        )
        
        assert len(result) > 0
        # Should use default statistics from config

    def test_calculate_categorical_with_missing_data(self, sample_config):
        """Test categorical statistics with missing data."""
        templates = StatisticalTemplates(sample_config)
        
        data = pd.DataFrame({
            "SEX": ["M", "F", np.nan, "M", "F"],
            "TRT": [1, 1, 1, 2, 2]
        })
        
        result = templates.calculate_categorical_statistics(
            data,
            "SEX",
            "TRT",
            statistics=["n"]
        )
        
        assert len(result) > 0
        # Missing values should be excluded


class TestFormatStatistic:
    """Test statistic formatting."""

    def test_format_simple_statistic(self, sample_config):
        """Test formatting simple statistic."""
        templates = StatisticalTemplates(sample_config)

        stat_def = sample_config.get_statistic("n")

        result = templates._format_statistic(10, stat_def)

        assert isinstance(result, str)
        assert "10" in result

    def test_format_decimal_statistic(self, sample_config):
        """Test formatting decimal statistic."""
        templates = StatisticalTemplates(sample_config)

        stat_def = sample_config.get_statistic("mean")

        result = templates._format_statistic(45.678, stat_def)

        assert isinstance(result, str)
        # Should contain formatted value

    def test_format_combined_statistic(self, sample_config):
        """Test formatting combined statistic."""
        templates = StatisticalTemplates(sample_config)

        stat_def = sample_config.get_statistic("mean_sd")

        result = templates._format_statistic((45.5, 10.2), stat_def)

        assert isinstance(result, str)
        # Should contain both values


class TestRegisterFormatFunctions:
    """Test format function registration."""

    def test_register_format_functions(self, sample_config):
        """Test that format functions are registered."""
        templates = StatisticalTemplates(sample_config)
        
        assert hasattr(templates, "_format_functions")
        assert isinstance(templates._format_functions, dict)
        # Should have at least some default format functions

