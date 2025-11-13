"""
Unit tests for py4csr.analysis.efficacy module.

Tests efficacy analysis functions.
"""

import pandas as pd
import pytest
import numpy as np

from py4csr.analysis.efficacy import (
    ancova_analysis,
    create_efficacy_table,
)


@pytest.fixture
def sample_efficacy_data():
    """Create sample efficacy data for testing."""
    np.random.seed(42)
    return pd.DataFrame({
        "USUBJID": [f"{i:03d}" for i in range(1, 101)],
        "TRT01P": ["Placebo"] * 33 + ["Drug Low"] * 33 + ["Drug High"] * 34,
        "BASELINE": np.random.normal(50, 10, 100),
        "CHANGE": np.random.normal(5, 8, 100),
        "AGE": np.random.randint(18, 80, 100),
        "SEX": np.random.choice(["M", "F"], 100),
    })


class TestAncovaAnalysis:
    """Test ancova_analysis function."""

    def test_basic_ancova(self, sample_efficacy_data):
        """Test basic ANCOVA without covariates."""
        pytest.importorskip("statsmodels")
        
        result = ancova_analysis(
            data=sample_efficacy_data,
            endpoint="CHANGE",
            treatment="TRT01P",
        )

        assert "formula" in result
        assert "n_obs" in result
        assert "r_squared" in result
        assert "f_statistic" in result
        assert "f_pvalue" in result
        assert "coefficients" in result
        assert "pvalues" in result

    def test_ancova_with_baseline(self, sample_efficacy_data):
        """Test ANCOVA with baseline covariate."""
        pytest.importorskip("statsmodels")
        
        result = ancova_analysis(
            data=sample_efficacy_data,
            endpoint="CHANGE",
            treatment="TRT01P",
            baseline="BASELINE",
        )

        assert "BASELINE" in result["formula"]
        assert "coefficients" in result
        assert "pvalues" in result

    def test_ancova_with_covariates(self, sample_efficacy_data):
        """Test ANCOVA with additional covariates."""
        pytest.importorskip("statsmodels")
        
        result = ancova_analysis(
            data=sample_efficacy_data,
            endpoint="CHANGE",
            treatment="TRT01P",
            baseline="BASELINE",
            covariates=["AGE"],
        )

        assert "AGE" in result["formula"]
        assert "BASELINE" in result["formula"]

    def test_ancova_multiple_covariates(self, sample_efficacy_data):
        """Test ANCOVA with multiple covariates."""
        pytest.importorskip("statsmodels")
        
        result = ancova_analysis(
            data=sample_efficacy_data,
            endpoint="CHANGE",
            treatment="TRT01P",
            covariates=["AGE", "BASELINE"],
        )

        assert "AGE" in result["formula"]
        assert "BASELINE" in result["formula"]

    def test_ancova_formula_structure(self, sample_efficacy_data):
        """Test ANCOVA formula structure."""
        pytest.importorskip("statsmodels")
        
        result = ancova_analysis(
            data=sample_efficacy_data,
            endpoint="CHANGE",
            treatment="TRT01P",
            baseline="BASELINE",
        )

        formula = result["formula"]
        assert "CHANGE" in formula
        assert "TRT01P" in formula
        assert "BASELINE" in formula
        assert "~" in formula

    def test_ancova_coefficients(self, sample_efficacy_data):
        """Test ANCOVA coefficients."""
        pytest.importorskip("statsmodels")
        
        result = ancova_analysis(
            data=sample_efficacy_data,
            endpoint="CHANGE",
            treatment="TRT01P",
        )

        coefficients = result["coefficients"]
        assert isinstance(coefficients, dict)
        assert len(coefficients) > 0

    def test_ancova_pvalues(self, sample_efficacy_data):
        """Test ANCOVA p-values."""
        pytest.importorskip("statsmodels")
        
        result = ancova_analysis(
            data=sample_efficacy_data,
            endpoint="CHANGE",
            treatment="TRT01P",
        )

        pvalues = result["pvalues"]
        assert isinstance(pvalues, dict)
        assert len(pvalues) > 0

    def test_ancova_conf_int(self, sample_efficacy_data):
        """Test ANCOVA confidence intervals."""
        pytest.importorskip("statsmodels")
        
        result = ancova_analysis(
            data=sample_efficacy_data,
            endpoint="CHANGE",
            treatment="TRT01P",
        )

        conf_int = result["conf_int"]
        assert isinstance(conf_int, dict)

    def test_ancova_residuals(self, sample_efficacy_data):
        """Test ANCOVA residuals."""
        pytest.importorskip("statsmodels")
        
        result = ancova_analysis(
            data=sample_efficacy_data,
            endpoint="CHANGE",
            treatment="TRT01P",
        )

        assert "residuals" in result
        assert len(result["residuals"]) > 0

    def test_ancova_fitted_values(self, sample_efficacy_data):
        """Test ANCOVA fitted values."""
        pytest.importorskip("statsmodels")
        
        result = ancova_analysis(
            data=sample_efficacy_data,
            endpoint="CHANGE",
            treatment="TRT01P",
        )

        assert "fitted_values" in result
        assert len(result["fitted_values"]) > 0

    def test_ancova_r_squared(self, sample_efficacy_data):
        """Test ANCOVA R-squared."""
        pytest.importorskip("statsmodels")
        
        result = ancova_analysis(
            data=sample_efficacy_data,
            endpoint="CHANGE",
            treatment="TRT01P",
        )

        assert "r_squared" in result
        assert 0 <= result["r_squared"] <= 1

    def test_ancova_f_statistic(self, sample_efficacy_data):
        """Test ANCOVA F-statistic."""
        pytest.importorskip("statsmodels")
        
        result = ancova_analysis(
            data=sample_efficacy_data,
            endpoint="CHANGE",
            treatment="TRT01P",
        )

        assert "f_statistic" in result
        assert result["f_statistic"] >= 0

    def test_ancova_missing_data(self):
        """Test ANCOVA with missing data."""
        pytest.importorskip("statsmodels")
        
        data = pd.DataFrame({
            "USUBJID": ["001", "002", "003", "004"],
            "TRT01P": ["Placebo", "Drug", "Placebo", "Drug"],
            "CHANGE": [5.0, np.nan, 7.0, 6.0],
        })

        result = ancova_analysis(
            data=data,
            endpoint="CHANGE",
            treatment="TRT01P",
        )

        # Should handle missing data (statsmodels drops missing by default)
        assert "n_obs" in result

    def test_ancova_error_handling(self):
        """Test ANCOVA error handling."""
        pytest.importorskip("statsmodels")
        
        # Invalid data
        data = pd.DataFrame({
            "USUBJID": ["001", "002"],
            "TRT01P": ["Placebo", "Placebo"],  # Only one treatment group
            "CHANGE": [5.0, 6.0],
        })

        result = ancova_analysis(
            data=data,
            endpoint="CHANGE",
            treatment="TRT01P",
        )

        # Should return error in result
        assert "error" in result or "coefficients" in result

    def test_ancova_without_statsmodels(self, monkeypatch, sample_efficacy_data):
        """Test ANCOVA without statsmodels installed."""
        # Mock import error
        import builtins
        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "statsmodels.api" or name == "statsmodels.formula.api":
                raise ImportError("No module named 'statsmodels'")
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)

        with pytest.raises(ImportError, match="statsmodels is required"):
            ancova_analysis(
                data=sample_efficacy_data,
                endpoint="CHANGE",
                treatment="TRT01P",
            )


class TestCreateEfficacyTable:
    """Test create_efficacy_table function."""

    def test_basic_table(self):
        """Test basic efficacy table creation."""
        ancova_results = {
            "ls_means": {
                "Placebo": {"estimate": 5.0, "ci_lower": 3.0, "ci_upper": 7.0, "p_value": 0.001},
                "Drug": {"estimate": 8.0, "ci_lower": 6.0, "ci_upper": 10.0, "p_value": 0.001},
            },
            "comparisons": {
                "Drug vs Placebo": {"estimate": 3.0, "ci_lower": 1.0, "ci_upper": 5.0, "p_value": 0.005},
            },
            "model_summary": {
                "overall_p": 0.001,
            },
        }

        result = create_efficacy_table(ancova_results)

        assert isinstance(result, pd.DataFrame)
        assert "Parameter" in result.columns
        assert "Estimate" in result.columns
        assert "CI_Lower" in result.columns
        assert "CI_Upper" in result.columns
        assert "P_value" in result.columns

    def test_ls_means_formatting(self):
        """Test LS means formatting."""
        ancova_results = {
            "ls_means": {
                "Placebo": {"estimate": 5.123, "ci_lower": 3.456, "ci_upper": 7.789, "p_value": 0.001234},
            },
        }

        result = create_efficacy_table(ancova_results)

        # Check formatting (2 decimal places for estimates, 4 for p-values)
        assert "5.12" in result["Estimate"].iloc[0]
        assert "0.0012" in result["P_value"].iloc[0]

    def test_comparisons_formatting(self):
        """Test comparisons formatting."""
        ancova_results = {
            "comparisons": {
                "Drug vs Placebo": {"estimate": 3.0, "ci_lower": 1.0, "ci_upper": 5.0, "p_value": 0.005},
            },
        }

        result = create_efficacy_table(ancova_results)

        assert "Difference - Drug vs Placebo" in result["Parameter"].values

    def test_model_summary_formatting(self):
        """Test model summary formatting."""
        ancova_results = {
            "model_summary": {
                "overall_p": 0.001,
            },
        }

        result = create_efficacy_table(ancova_results)

        assert "Overall Treatment Effect" in result["Parameter"].values

    def test_empty_results(self):
        """Test with empty results."""
        ancova_results = {}

        result = create_efficacy_table(ancova_results)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    def test_missing_ls_means(self):
        """Test with missing LS means."""
        ancova_results = {
            "comparisons": {
                "Drug vs Placebo": {"estimate": 3.0, "ci_lower": 1.0, "ci_upper": 5.0, "p_value": 0.005},
            },
        }

        result = create_efficacy_table(ancova_results)

        assert isinstance(result, pd.DataFrame)
        assert len(result) >= 1

    def test_missing_comparisons(self):
        """Test with missing comparisons."""
        ancova_results = {
            "ls_means": {
                "Placebo": {"estimate": 5.0, "ci_lower": 3.0, "ci_upper": 7.0, "p_value": 0.001},
            },
        }

        result = create_efficacy_table(ancova_results)

        assert isinstance(result, pd.DataFrame)
        assert len(result) >= 1

