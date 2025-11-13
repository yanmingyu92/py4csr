"""
Unit tests for py4csr.analysis.utils module.

Tests utility functions for statistical formatting and calculations.
"""

import numpy as np
import pytest

from py4csr.analysis.utils import (
    format_ci,
    format_mean_sd,
    format_pvalue,
)


class TestFormatMeanSd:
    """Test format_mean_sd function."""

    def test_basic_formatting(self):
        """Test basic mean and SD formatting."""
        result = format_mean_sd(12.5, 3.24)
        assert result == "12.5 (3.24)"

    def test_custom_digits(self):
        """Test custom decimal places."""
        result = format_mean_sd(12.567, 3.2456, mean_digits=2, sd_digits=3)
        assert result == "12.57 (3.246)"

    def test_zero_values(self):
        """Test formatting with zero values."""
        result = format_mean_sd(0.0, 0.0)
        assert "0.0" in result

    def test_nan_values(self):
        """Test handling of NaN values."""
        result = format_mean_sd(np.nan, 3.24)
        assert result == "N/A"

        result = format_mean_sd(12.5, np.nan)
        assert result == "N/A"

    def test_large_values(self):
        """Test formatting large values."""
        result = format_mean_sd(1234.5, 567.89)
        assert "1234.5" in result
        assert "567.89" in result


class TestFormatCi:
    """Test format_ci function."""

    def test_basic_formatting(self):
        """Test basic CI formatting."""
        result = format_ci(1.5, 1.2, 1.8)
        assert "1.50" in result
        assert "1.20" in result
        assert "1.80" in result

    def test_custom_digits(self):
        """Test custom decimal places."""
        result = format_ci(1.567, 1.234, 1.890, digits=3)
        assert "1.567" in result
        assert "1.234" in result
        assert "1.890" in result

    def test_negative_values(self):
        """Test formatting with negative values."""
        result = format_ci(-0.5, -1.2, 0.2)
        assert "-0.50" in result
        assert "-1.20" in result
        assert "0.20" in result

    def test_nan_values(self):
        """Test handling of NaN values."""
        result = format_ci(np.nan, 1.2, 1.8)
        assert result == "N/A"

    def test_wide_interval(self):
        """Test formatting wide confidence interval."""
        result = format_ci(50.0, 10.0, 90.0)
        assert "50.00" in result
        assert "10.00" in result
        assert "90.00" in result


class TestFormatPvalue:
    """Test format_pvalue function."""

    def test_large_pvalue(self):
        """Test formatting large p-value."""
        result = format_pvalue(0.5)
        assert "0.5" in result

    def test_small_pvalue(self):
        """Test formatting small p-value."""
        result = format_pvalue(0.0001)
        assert "<0.001" in result or "0.0001" in result

    def test_very_small_pvalue(self):
        """Test formatting very small p-value."""
        result = format_pvalue(0.00001)
        assert "<0.001" in result

    def test_threshold_pvalue(self):
        """Test p-value at threshold."""
        result = format_pvalue(0.05)
        assert "0.05" in result

    def test_custom_digits(self):
        """Test custom decimal places."""
        result = format_pvalue(0.123, digits=2)
        assert "0.12" in result

    def test_nan_pvalue(self):
        """Test handling of NaN p-value."""
        result = format_pvalue(np.nan)
        assert result == "N/A" or result == ""

    def test_zero_pvalue(self):
        """Test handling of zero p-value."""
        result = format_pvalue(0.0)
        assert "<0.001" in result or "0.000" in result

    def test_one_pvalue(self):
        """Test p-value of 1.0."""
        result = format_pvalue(1.0)
        assert "1.0" in result or "1.00" in result


class TestFormatting:
    """Test general formatting utilities."""

    def test_consistent_formatting(self):
        """Test that formatting is consistent."""
        # Same values should produce same output
        result1 = format_mean_sd(12.5, 3.24)
        result2 = format_mean_sd(12.5, 3.24)
        assert result1 == result2

    def test_rounding_behavior(self):
        """Test rounding behavior."""
        # Test rounding up
        result = format_mean_sd(12.55, 3.245, mean_digits=1, sd_digits=2)
        assert "12.6" in result or "12.5" in result  # Depends on rounding mode

    def test_edge_cases(self):
        """Test edge cases in formatting."""
        # Very small values
        result = format_mean_sd(0.001, 0.0001, mean_digits=4, sd_digits=5)
        assert "0.0010" in result
        assert "0.00010" in result


class TestStatisticalUtilities:
    """Test statistical utility functions."""

    def test_format_combinations(self):
        """Test combining different format functions."""
        mean_sd = format_mean_sd(12.5, 3.24)
        ci = format_ci(12.5, 10.0, 15.0)
        pval = format_pvalue(0.05)

        # All should be strings
        assert isinstance(mean_sd, str)
        assert isinstance(ci, str)
        assert isinstance(pval, str)

    def test_typical_clinical_values(self):
        """Test formatting typical clinical trial values."""
        # Age
        age_result = format_mean_sd(45.3, 12.7)
        assert "45.3" in age_result
        assert "12.7" in age_result

        # Odds ratio
        or_result = format_ci(1.25, 0.95, 1.65)
        assert "1.25" in or_result

        # P-value
        p_result = format_pvalue(0.0234)
        assert "0.02" in p_result or "0.023" in p_result


class TestErrorHandling:
    """Test error handling in utility functions."""

    def test_invalid_inputs(self):
        """Test handling of invalid inputs."""
        # Should handle None gracefully or raise appropriate error
        try:
            result = format_mean_sd(None, 3.24)
            # If it doesn't raise, should return something reasonable
            assert result is not None
        except (TypeError, ValueError):
            # Expected to raise error
            pass

    def test_infinite_values(self):
        """Test handling of infinite values."""
        try:
            result = format_mean_sd(np.inf, 3.24)
            # Should handle gracefully
            assert result is not None
        except (ValueError, OverflowError):
            # May raise error
            pass

    def test_negative_sd(self):
        """Test handling of negative SD (invalid)."""
        # SD should not be negative, but function should handle it
        result = format_mean_sd(12.5, -3.24)
        # Should still format, even if statistically invalid
        assert isinstance(result, str)


class TestWorkflow:
    """Test complete formatting workflow."""

    def test_demographics_formatting(self):
        """Test formatting for demographics table."""
        # Age
        age = format_mean_sd(45.3, 12.7)
        assert isinstance(age, str)

        # Weight
        weight = format_mean_sd(75.2, 15.8)
        assert isinstance(weight, str)

    def test_efficacy_formatting(self):
        """Test formatting for efficacy analysis."""
        # Treatment effect
        effect = format_ci(1.25, 0.95, 1.65)
        assert isinstance(effect, str)

        # P-value
        pval = format_pvalue(0.0234)
        assert isinstance(pval, str)

    def test_safety_formatting(self):
        """Test formatting for safety analysis."""
        # Incidence rate
        rate = format_mean_sd(12.5, 5.3)
        assert isinstance(rate, str)

        # Risk ratio CI
        rr_ci = format_ci(1.15, 0.85, 1.55)
        assert isinstance(rr_ci, str)

