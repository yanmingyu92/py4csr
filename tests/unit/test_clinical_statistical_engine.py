"""
Unit tests for py4csr.clinical.statistical_engine module.

Tests the ClinicalStatisticalEngine class for statistical calculations.
"""

import pandas as pd
import pytest
import numpy as np

from py4csr.clinical.statistical_engine import ClinicalStatisticalEngine


@pytest.fixture
def sample_continuous_data():
    """Create sample data for continuous variable testing."""
    return pd.DataFrame({
        "USUBJID": [f"S{i:03d}" for i in range(1, 31)],
        "TRT01P": ["Placebo"] * 10 + ["Drug A"] * 10 + ["Drug B"] * 10,
        "TRT01PN": [1] * 10 + [2] * 10 + [3] * 10,
        "AGE": [25, 30, 35, 40, 45, 50, 55, 60, 65, 70] * 3,
        "WEIGHT": [60.5, 65.2, 70.1, 75.3, 80.0, 85.5, 90.2, 95.1, 100.0, 105.5] * 3,
        "HEIGHT": [160, 165, 170, 175, 180, 165, 170, 175, 180, 185] * 3,
    })


@pytest.fixture
def sample_categorical_data():
    """Create sample data for categorical variable testing."""
    return pd.DataFrame({
        "USUBJID": [f"S{i:03d}" for i in range(1, 31)],
        "TRT01P": ["Placebo"] * 10 + ["Drug A"] * 10 + ["Drug B"] * 10,
        "TRT01PN": [1] * 10 + [2] * 10 + [3] * 10,
        "SEX": ["M", "F", "M", "F", "M", "F", "M", "F", "M", "F"] * 3,
        "RACE": ["WHITE"] * 15 + ["BLACK"] * 10 + ["ASIAN"] * 5,
        "ETHNIC": ["NOT HISPANIC"] * 20 + ["HISPANIC"] * 10,
    })


@pytest.fixture
def engine():
    """Create ClinicalStatisticalEngine instance."""
    return ClinicalStatisticalEngine()


class TestClinicalStatisticalEngineInit:
    """Test ClinicalStatisticalEngine initialization."""

    def test_initialization(self, engine):
        """Test basic initialization."""
        assert engine is not None
        assert hasattr(engine, 'decimal_places')
        assert engine.decimal_places['age'] == 1
        assert engine.decimal_places['default'] == 1


class TestCalculateContinuousStats:
    """Test calculate_continuous_stats method."""

    def test_basic_continuous_stats(self, engine, sample_continuous_data):
        """Test basic continuous statistics calculation."""
        result = engine.calculate_continuous_stats(
            data=sample_continuous_data,
            variable="AGE",
            treatment_var="TRT01P",
            stats_spec="n mean sd"
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        # Check for lowercase column names
        assert "statistic" in result.columns or "Statistic" in result.columns

    def test_continuous_stats_with_where_clause(self, engine, sample_continuous_data):
        """Test continuous stats with where clause."""
        result = engine.calculate_continuous_stats(
            data=sample_continuous_data,
            variable="AGE",
            treatment_var="TRT01P",
            stats_spec="n mean",
            where_clause="AGE >= 40"
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

    def test_continuous_stats_all_statistics(self, engine, sample_continuous_data):
        """Test continuous stats with all statistics."""
        result = engine.calculate_continuous_stats(
            data=sample_continuous_data,
            variable="AGE",
            treatment_var="TRT01P",
            stats_spec="n mean+sd median q1q3 min+max"
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) >= 5  # At least 5 statistics

    def test_continuous_stats_with_decimals(self, engine, sample_continuous_data):
        """Test continuous stats with custom decimals."""
        result = engine.calculate_continuous_stats(
            data=sample_continuous_data,
            variable="WEIGHT",
            treatment_var="TRT01P",
            stats_spec="n mean",
            base_decimals=2
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0


class TestCalculateCategoricalStats:
    """Test calculate_categorical_stats method."""

    def test_basic_categorical_stats(self, engine, sample_categorical_data):
        """Test basic categorical statistics calculation."""
        result = engine.calculate_categorical_stats(
            data=sample_categorical_data,
            variable="SEX",
            treatment_var="TRT01P",
            stats_spec="npct"
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        # Check for lowercase column names
        assert "category" in result.columns or "Category" in result.columns

    def test_categorical_stats_with_where_clause(self, engine, sample_categorical_data):
        """Test categorical stats with where clause."""
        result = engine.calculate_categorical_stats(
            data=sample_categorical_data,
            variable="RACE",
            treatment_var="TRT01P",
            stats_spec="npct",
            where_clause="SEX == 'M'"
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

    def test_categorical_stats_with_decode(self, engine, sample_categorical_data):
        """Test categorical stats with decode variable."""
        result = engine.calculate_categorical_stats(
            data=sample_categorical_data,
            variable="SEX",
            treatment_var="TRT01P",
            stats_spec="npct",
            decode_var="SEX"
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

    def test_categorical_stats_with_show_missing(self, engine, sample_categorical_data):
        """Test categorical stats with show_missing parameter."""
        result = engine.calculate_categorical_stats(
            data=sample_categorical_data,
            variable="SEX",
            treatment_var="TRT01P",
            stats_spec="npct",
            show_missing="N"
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0


class TestCalculateShiftTableStats:
    """Test calculate_shift_table_stats method."""

    def test_basic_shift_table(self, engine):
        """Test basic shift table calculation."""
        data = pd.DataFrame({
            "USUBJID": [f"S{i:03d}" for i in range(1, 21)],
            "TRT01P": ["Placebo"] * 10 + ["Drug A"] * 10,
            "BASELINE": ["Normal"] * 5 + ["High"] * 5 + ["Normal"] * 5 + ["High"] * 5,
            "POST": ["Normal"] * 8 + ["High"] * 12,
        })

        result = engine.calculate_shift_table_stats(
            data=data,
            row_variable="POST",
            col_variable="BASELINE",
            treatment_var="TRT01P",
            stats_spec="npct",
            row_codelist={"Normal": "Normal", "High": "High"},
            col_codelist={"Normal": "Normal", "High": "High"}
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0


class TestStatisticalTests:
    """Test statistical test methods."""

    def test_perform_anova(self, engine, sample_continuous_data):
        """Test ANOVA calculation."""
        result = engine.perform_anova(
            data=sample_continuous_data,
            variable="AGE",
            treatment_var="TRT01P"
        )

        assert isinstance(result, dict)
        assert "f_stat" in result or "f_statistic" in result
        assert "p_value" in result

    def test_perform_chi_square(self, engine, sample_categorical_data):
        """Test chi-square calculation."""
        result = engine.perform_chi_square(
            data=sample_categorical_data,
            variable="SEX",
            treatment_var="TRT01P"
        )

        assert isinstance(result, dict)
        assert "chi2" in result or "chi2_statistic" in result
        assert "p_value" in result

    def test_perform_fisher_exact(self, engine, sample_categorical_data):
        """Test Fisher's exact test calculation."""
        result = engine.perform_fisher_exact(
            data=sample_categorical_data,
            variable="SEX",
            treatment_var="TRT01P"
        )

        assert isinstance(result, dict)
        assert "p_value" in result


class TestGtsummaryTestSelection:
    """Test gtsummary-style default test selection (Task: p-value parity)."""

    def test_perform_wilcoxon_matches_scipy(self, engine):
        """Wilcoxon rank-sum for 2 groups matches scipy mannwhitneyu."""
        from scipy import stats as sps

        rng = np.random.default_rng(42)
        data = pd.DataFrame({
            "TRT": ["A"] * 50 + ["B"] * 50,
            "VAL": np.concatenate([rng.normal(10, 2, 50), rng.normal(11, 2, 50)]),
        })
        result = engine.perform_wilcoxon(data, "VAL", "TRT")
        ref = sps.mannwhitneyu(
            data.loc[data.TRT == "A", "VAL"],
            data.loc[data.TRT == "B", "VAL"],
            alternative="two-sided",
        )
        assert result["error"] is None
        assert result["test"] == "Wilcoxon rank-sum test"
        assert abs(result["p_value"] - ref.pvalue) < 1e-12

    def test_perform_wilcoxon_requires_two_groups(self, engine, sample_continuous_data):
        """Wilcoxon with 3 groups returns a clear error, not a crash."""
        result = engine.perform_wilcoxon(sample_continuous_data, "AGE", "TRT01P")
        assert result["p_value"] is None
        assert "2 groups" in result["error"]

    def test_perform_kruskal_matches_scipy(self, engine, sample_continuous_data):
        """Kruskal-Wallis for 3 groups matches scipy kruskal."""
        from scipy import stats as sps

        result = engine.perform_kruskal(sample_continuous_data, "AGE", "TRT01P")
        ref = sps.kruskal(
            *[g["AGE"].values for _, g in sample_continuous_data.groupby("TRT01P")]
        )
        assert result["error"] is None
        assert result["test"] == "Kruskal-Wallis test"
        assert abs(result["p_value"] - ref.pvalue) < 1e-12

    def test_perform_ttest(self, engine):
        """Pooled two-sample t-test for 2 groups."""
        rng = np.random.default_rng(7)
        data = pd.DataFrame({
            "TRT": ["A"] * 30 + ["B"] * 30,
            "VAL": np.concatenate([rng.normal(0, 1, 30), rng.normal(0.8, 1, 30)]),
        })
        result = engine.perform_ttest(data, "VAL", "TRT")
        assert result["error"] is None
        assert 0 <= result["p_value"] <= 1

    def test_continuous_test_auto_two_groups_uses_wilcoxon(self, engine):
        """auto with 2 groups selects Wilcoxon rank-sum (gtsummary default)."""
        rng = np.random.default_rng(1)
        data = pd.DataFrame({
            "TRT": ["A"] * 20 + ["B"] * 20,
            "VAL": rng.normal(0, 1, 40),
        })
        result = engine.perform_continuous_test(data, "VAL", "TRT", test="auto")
        assert result["test"] == "Wilcoxon rank-sum test"
        assert result["p_value"] is not None

    def test_continuous_test_auto_multi_groups_uses_kruskal(
        self, engine, sample_continuous_data
    ):
        """auto with >2 groups selects Kruskal-Wallis (gtsummary default)."""
        result = engine.perform_continuous_test(
            sample_continuous_data, "AGE", "TRT01P", test="auto"
        )
        assert result["test"] == "Kruskal-Wallis test"
        assert result["p_value"] is not None

    def test_continuous_test_anova_override(self, engine, sample_continuous_data):
        """test='anova' keeps the pre-existing ANOVA behavior."""
        result = engine.perform_continuous_test(
            sample_continuous_data, "AGE", "TRT01P", test="anova"
        )
        ref = engine.perform_anova(sample_continuous_data, "AGE", "TRT01P")
        assert result["test"] == "One-way ANOVA"
        assert result["p_value"] == ref["p_value"]

    def test_continuous_test_unknown_test(self, engine, sample_continuous_data):
        """Unknown test name returns a clear, actionable error."""
        result = engine.perform_continuous_test(
            sample_continuous_data, "AGE", "TRT01P", test="bogus"
        )
        assert result["p_value"] is None
        assert "Unknown continuous test" in result["error"]

    def test_categorical_test_auto_uses_chisq_when_expected_ok(
        self, engine, sample_categorical_data
    ):
        """auto uses Pearson chi-square when all expected counts >= 5."""
        result = engine.perform_categorical_test(
            sample_categorical_data, "SEX", "TRT01P", test="auto"
        )
        assert result["test"] == "Pearson's Chi-squared test"
        assert result["p_value"] is not None

    def test_categorical_test_auto_switches_to_fisher_on_small_expected(self, engine):
        """auto switches to Fisher exact when any expected count < 5."""
        data = pd.DataFrame({
            "TRT": ["A"] * 10 + ["B"] * 10,
            "RARE": ["Y", "N", "N", "N", "N", "N", "N", "N", "N", "N",
                     "N", "N", "N", "N", "N", "N", "N", "N", "N", "N"],
        })
        result = engine.perform_categorical_test(data, "RARE", "TRT", test="auto")
        assert result["test"] == "Fisher's exact test"
        ref = engine.perform_fisher_exact(data, "RARE", "TRT")
        assert abs(result["p_value"] - ref["p_value"]) < 1e-12

    def test_categorical_test_fisher_override_larger_table(self, engine):
        """test='fisher' works for RxC tables via fixed-seed Monte Carlo."""
        data = pd.DataFrame({
            "TRT": ["A"] * 9 + ["B"] * 9,
            "CAT": ["x", "y", "z", "x", "y", "z", "x", "y", "y",
                    "x", "x", "z", "y", "z", "z", "x", "x", "x"],
        })
        result = engine.perform_categorical_test(data, "CAT", "TRT", test="fisher")
        assert result["test"] == "Fisher's exact test"
        assert result["p_value"] is not None
        # deterministic across calls (fixed seed)
        result2 = engine.perform_categorical_test(data, "CAT", "TRT", test="fisher")
        assert result["p_value"] == result2["p_value"]

    def test_categorical_test_unknown_test(self, engine, sample_categorical_data):
        """Unknown test name returns a clear, actionable error."""
        result = engine.perform_categorical_test(
            sample_categorical_data, "SEX", "TRT01P", test="bogus"
        )
        assert result["p_value"] is None
        assert "Unknown categorical test" in result["error"]


class TestCalculateConditionStats:
    """Test calculate_condition_stats method."""

    def test_condition_stats(self, engine, sample_continuous_data):
        """Test condition-based statistics."""
        result = engine.calculate_condition_stats(
            data=sample_continuous_data,
            treatment_var="TRT01P",
            where_clause="AGE >= 65",
            stats_spec="n"
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0


class TestHelperMethods:
    """Test helper methods."""

    def test_parse_stats_spec(self, engine):
        """Test _parse_stats_spec method."""
        result = engine._parse_stats_spec("n mean+sd median q1q3 min+max")

        assert isinstance(result, list)
        assert len(result) > 0
        # Check for any of the expected statistics (case-insensitive)
        result_lower = [s.lower() for s in result]
        assert any("n" in s.lower() for s in result) or any("mean" in s.lower() for s in result)

    def test_parse_categorical_stats_spec(self, engine):
        """Test _parse_categorical_stats_spec method."""
        result = engine._parse_categorical_stats_spec("npct")

        assert isinstance(result, list)
        assert len(result) > 0

    def test_format_category_name(self, engine):
        """Test _format_category_name method."""
        result = engine._format_category_name("male")

        assert isinstance(result, str)
        assert result == "Male"

    def test_format_category_name_missing(self, engine):
        """Test _format_category_name with Missing."""
        result = engine._format_category_name("Missing")

        assert result == "Missing"


class TestEdgeCases:
    """Test edge cases."""

    def test_continuous_stats_with_missing_values(self, engine):
        """Test continuous stats with missing values."""
        data = pd.DataFrame({
            "USUBJID": [f"S{i:03d}" for i in range(1, 11)],
            "TRT01P": ["Placebo"] * 5 + ["Drug A"] * 5,
            "AGE": [25, 30, np.nan, 40, 45, 50, np.nan, 60, 65, 70],
        })

        result = engine.calculate_continuous_stats(
            data=data,
            variable="AGE",
            treatment_var="TRT01P",
            stats_spec="n mean"
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

    def test_categorical_stats_with_empty_categories(self, engine):
        """Test categorical stats with empty categories."""
        data = pd.DataFrame({
            "USUBJID": [f"S{i:03d}" for i in range(1, 11)],
            "TRT01P": ["Placebo"] * 10,
            "SEX": ["M"] * 10,
        })

        result = engine.calculate_categorical_stats(
            data=data,
            variable="SEX",
            treatment_var="TRT01P",
            stats_spec="npct"
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0


class TestConditionStats:
    """Test calculate_condition_stats method."""

    def test_condition_stats_basic(self, sample_categorical_data, engine):
        """Test basic condition statistics."""
        results = engine.calculate_condition_stats(
            data=sample_categorical_data,
            treatment_var="TRT01P",
            where_clause="SEX=='M'",
            stats_spec="n",
            subjid_var="USUBJID",
        )

        assert isinstance(results, pd.DataFrame)
        assert len(results) > 0

    def test_condition_stats_with_npct(self, sample_categorical_data, engine):
        """Test condition statistics with n and percentage."""
        results = engine.calculate_condition_stats(
            data=sample_categorical_data,
            treatment_var="TRT01P",
            where_clause="SEX=='F'",
            stats_spec="npct",
            subjid_var="USUBJID",
        )

        assert isinstance(results, pd.DataFrame)
        assert len(results) > 0

    def test_condition_stats_with_denomwhere(self, sample_categorical_data, engine):
        """Test condition statistics with custom denominator."""
        results = engine.calculate_condition_stats(
            data=sample_categorical_data,
            treatment_var="TRT01P",
            where_clause="SEX=='M'",
            stats_spec="npct",
            subjid_var="USUBJID",
            denomwhere="SEX.notna()",
        )

        assert isinstance(results, pd.DataFrame)
        assert len(results) > 0

    def test_condition_stats_count_events(self, sample_categorical_data, engine):
        """Test condition statistics counting events instead of subjects."""
        results = engine.calculate_condition_stats(
            data=sample_categorical_data,
            treatment_var="TRT01P",
            where_clause="SEX=='M'",
            stats_spec="n",
            subjid_var="USUBJID",
            countwhat="events",
        )

        assert isinstance(results, pd.DataFrame)
        assert len(results) > 0

    def test_condition_stats_invalid_where_clause(self, sample_categorical_data, engine):
        """Test condition statistics with invalid where clause."""
        # Should handle gracefully with warning
        results = engine.calculate_condition_stats(
            data=sample_categorical_data,
            treatment_var="TRT01P",
            where_clause="INVALID_COLUMN=='value'",
            stats_spec="n",
            subjid_var="USUBJID",
        )

        assert isinstance(results, pd.DataFrame)


class TestHelperMethods:
    """Test helper methods in ClinicalStatisticalEngine."""

    def test_calculate_single_continuous_stat_variance(self, engine):
        """Test variance calculation."""
        data = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        result = engine._calculate_single_continuous_stat(data, "Variance", 2)

        assert result["name"] == "Variance"
        assert result["value"] is not None
        assert isinstance(result["formatted"], str)
        # Variance should be calculated
        expected_var = data.var()
        assert abs(result["value"] - expected_var) < 0.01

    def test_calculate_single_continuous_stat_q1q3(self, engine):
        """Test Q1, Q3 calculation."""
        data = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        result = engine._calculate_single_continuous_stat(data, "Q1, Q3", 1)

        assert result["name"] == "Q1, Q3"
        assert result["value"] is not None
        # Should be a tuple of (Q1, Q3)
        assert isinstance(result["value"], tuple)
        assert len(result["value"]) == 2

    def test_calculate_single_continuous_stat_min_max(self, engine):
        """Test Min, Max calculation."""
        data = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        result = engine._calculate_single_continuous_stat(data, "Min, Max", 1)

        assert result["name"] == "Min, Max"
        assert result["value"] is not None
        # Should be a tuple of (Min, Max)
        assert isinstance(result["value"], tuple)
        assert result["value"] == (1.0, 5.0)

    def test_calculate_single_continuous_stat_mean_sd(self, engine):
        """Test Mean (SD) calculation."""
        data = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        result = engine._calculate_single_continuous_stat(data, "Mean (SD)", 1)

        assert result["name"] == "Mean (SD)"
        assert result["value"] is not None
        # Should be a tuple of (mean, sd)
        assert isinstance(result["value"], tuple)
        assert len(result["value"]) == 2

    def test_calculate_single_continuous_stat_unknown(self, engine):
        """Test unknown statistic name."""
        data = pd.Series([1.0, 2.0, 3.0])
        result = engine._calculate_single_continuous_stat(data, "UnknownStat", 1)

        assert result["name"] == "UnknownStat"
        # Should handle gracefully with None value
        assert result["value"] is None
        assert result["formatted"] == "N/A"

    def test_format_categorical_stat_n(self, engine):
        """Test formatting categorical statistic - n only."""
        result = engine._format_categorical_stat(n=10, percentage=33.3, total_n=30, stat_name="n")
        assert result == "10"

    def test_format_categorical_stat_pct(self, engine):
        """Test formatting categorical statistic - percentage only."""
        result = engine._format_categorical_stat(n=10, percentage=33.3, total_n=30, stat_name="pct")
        assert "33.3%" in result

    def test_format_categorical_stat_n_pct(self, engine):
        """Test formatting categorical statistic - n (pct)."""
        result = engine._format_categorical_stat(n=10, percentage=33.3, total_n=30, stat_name="n_pct")
        assert "10" in result
        assert "33.3%" in result

    def test_format_categorical_stat_nn_pct(self, engine):
        """Test formatting categorical statistic - n/N (pct)."""
        result = engine._format_categorical_stat(n=10, percentage=33.3, total_n=30, stat_name="nn_pct")
        assert "10/30" in result
        assert "33.3%" in result

    def test_format_category_name_race(self, engine):
        """Test formatting race category names."""
        result = engine._format_category_name("WHITE")
        assert result == "White"

        result = engine._format_category_name("BLACK OR AFRICAN AMERICAN")
        assert result == "Black or African American"

    def test_format_category_name_general(self, engine):
        """Test formatting general category names."""
        result = engine._format_category_name("male")
        assert result == "Male"

        result = engine._format_category_name("FEMALE")
        assert result == "Female"



class TestEdgeCaseRobustness:
    """Edge-case robustness for the table engine core.

    Each edge case must either produce a correct result or raise a clear,
    actionable error (ValueError with a message naming the problem) — never a
    stack-trace crash (KeyError/TypeError) or silently wrong numbers.
    """

    # --- all-missing variable -------------------------------------------------

    def test_all_missing_continuous_variable(self, engine):
        """All-missing continuous variable: N=0 and empty cells, no crash."""
        data = pd.DataFrame({
            "TRT": ["A"] * 5 + ["B"] * 5,
            "VAL": [np.nan] * 10,
        })
        result = engine.calculate_continuous_stats(
            data, "VAL", "TRT", "n mean sd median"
        )
        n_rows = result[result["statistic"] == "N"]
        assert all(n_rows["value"] == 0)
        # Non-count statistics have no value and empty formatted cell
        mean_rows = result[result["statistic"] == "Mean"]
        assert all(mean_rows["value"].isna())

    def test_all_missing_categorical_variable(self, engine):
        """All-missing categorical variable collapses to a 'Missing' row."""
        data = pd.DataFrame({
            "TRT": ["A"] * 5 + ["B"] * 5,
            "CAT": [None] * 10,
        })
        result = engine.calculate_categorical_stats(
            data, "CAT", "TRT", "npct", show_missing="Y"
        )
        assert set(result["category"].unique()) == {"Missing"}
        assert result[result["treatment"] == "A"]["n"].iloc[0] == 5
        assert result[result["treatment"] == "Total"]["n"].iloc[0] == 10

    # --- single-level categorical ----------------------------------------------

    def test_single_level_categorical(self, engine):
        """Single-level categorical variable produces correct 100% rows."""
        data = pd.DataFrame({
            "TRT": ["A"] * 4 + ["B"] * 6,
            "CAT": ["Active"] * 10,
        })
        result = engine.calculate_categorical_stats(
            data, "CAT", "TRT", "npct", show_missing="N"
        )
        assert set(result["category"].unique()) == {"Active"}
        assert result[result["treatment"] == "B"]["percentage"].iloc[0] == 100.0

    def test_single_level_categorical_test_returns_error_not_crash(self, engine):
        """A 1-level categorical cannot be tested: clear error, no crash."""
        data = pd.DataFrame({
            "TRT": ["A"] * 4 + ["B"] * 6,
            "CAT": ["ONLY"] * 10,
        })
        result = engine.perform_categorical_test(data, "CAT", "TRT")
        assert result["p_value"] is None
        assert "less than 2 levels" in result["error"]

    # --- zero-count category ----------------------------------------------------

    def test_zero_count_category(self, engine):
        """Category present in one arm only: 0 (0.0%) in the other arm."""
        data = pd.DataFrame({
            "TRT": ["A"] * 4 + ["B"] * 4,
            "CAT": ["X", "X", "X", "X", "Y", "Y", "Y", "Y"],
        })
        result = engine.calculate_categorical_stats(
            data, "CAT", "TRT", "npct", show_missing="N"
        )
        x_in_b = result[
            (result["treatment"] == "B") & (result["category"] == "X")
        ]
        assert x_in_b["n"].iloc[0] == 0
        assert x_in_b["formatted_value"].iloc[0] == "0 (0.0%)"

    def test_zero_count_category_chisquare(self, engine):
        """Chi-square still computable when a category is absent in one arm."""
        data = pd.DataFrame({
            "TRT": ["A"] * 4 + ["B"] * 4,
            "CAT": ["X", "X", "X", "X", "Y", "Y", "Y", "Y"],
        })
        result = engine.perform_categorical_test(data, "CAT", "TRT")
        assert result["p_value"] is not None

    # --- NaN in treatment variable ----------------------------------------------

    def test_nan_treatment_continuous_raises_clear_error(self, engine):
        """NaN in treatment variable -> ValueError with actionable message."""
        data = pd.DataFrame({
            "TRT": ["A", "B", None, "A", "B"],
            "VAL": [1.0, 2.0, 3.0, 4.0, 5.0],
        })
        with pytest.raises(ValueError, match="missing"):
            engine.calculate_continuous_stats(data, "VAL", "TRT", "n mean")

    def test_nan_treatment_categorical_raises_clear_error(self, engine):
        data = pd.DataFrame({
            "TRT": ["A", "B", None, "A", "B"],
            "CAT": ["X", "Y", "X", "Y", "X"],
        })
        with pytest.raises(ValueError, match="missing"):
            engine.calculate_categorical_stats(data, "CAT", "TRT", "npct")

    def test_missing_treatment_column_raises_clear_error(self, engine):
        """Treatment column absent -> ValueError, not a bare KeyError."""
        data = pd.DataFrame({"VAL": [1.0, 2.0]})
        with pytest.raises(ValueError, match="not found"):
            engine.calculate_continuous_stats(data, "VAL", "TRT", "n")

    # --- unknown stat keyword -----------------------------------------------------

    def test_unknown_continuous_stat_keyword_raises(self, engine):
        """Unknown stats= keyword -> ValueError listing valid keywords."""
        with pytest.raises(ValueError, match="Unknown statistic 'bogus'"):
            engine._parse_stats_spec("n mean bogus")

    def test_unknown_combined_stat_keyword_raises(self, engine):
        """Unknown keyword inside a combined spec -> ValueError."""
        with pytest.raises(ValueError, match="Unknown statistic"):
            engine._parse_stats_spec("mean+bogus")

    def test_unknown_categorical_stat_keyword_raises(self, engine):
        with pytest.raises(ValueError, match="Unknown categorical statistic"):
            engine._parse_categorical_stats_spec("npct bogus")

    def test_valid_stat_specs_still_parse(self, engine):
        """Regression: documented keywords keep parsing as before."""
        assert engine._parse_stats_spec("n mean+sd median q1q3 min+max") == [
            "N", "Mean (SD)", "Median", "Q1, Q3", "Min, Max",
        ]
        assert engine._parse_categorical_stats_spec("npct") == ["n_pct"]

    # --- empty groups / empty filtered data ---------------------------------------

    def test_where_clause_removing_all_rows_raises(self, engine):
        """Where clause that empties the data -> clear ValueError."""
        data = pd.DataFrame({
            "TRT": ["A", "B"],
            "VAL": [1.0, 2.0],
        })
        with pytest.raises(ValueError, match="No rows remain"):
            engine.calculate_continuous_stats(
                data, "VAL", "TRT", "n mean", where_clause="VAL > 100"
            )

    def test_empty_group_excluded_from_results(self, engine):
        """A treatment level with zero rows simply does not appear (the
        remaining groups and Total stay correct)."""
        data = pd.DataFrame({
            "TRT": ["A"] * 3 + ["B"] * 3,
            "VAL": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
        })
        result = engine.calculate_continuous_stats(
            data, "VAL", "TRT", "n", where_clause="TRT == 'A'"
        )
        assert set(result["treatment"].unique()) == {"A", "Total"}
        assert result[result["treatment"] == "Total"]["value"].iloc[0] == 3
