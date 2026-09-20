"""
Unit tests for py4csr.tbl_summary convenience API.
"""

import numpy as np
import pandas as pd
import pytest

import py4csr
from py4csr.summary import TblSummaryResult, tbl_summary


@pytest.fixture
def adsl():
    rng = np.random.default_rng(123)
    n = 60
    return pd.DataFrame({
        "USUBJID": [f"S{i:03d}" for i in range(n)],
        "TRT01P": ["Drug A"] * 30 + ["Drug B"] * 30,
        "AGE": rng.normal(55, 10, n),
        "SEX": ["M", "F"] * 30,
        "SAFFL": ["Y"] * (n - 4) + ["N"] * 4,
    })


class TestTblSummary:
    """Test the tbl_summary convenience entry point."""

    def test_basic_summary(self, adsl):
        """Continuous + categorical variables produce ARD and table."""
        tbl = tbl_summary(data=adsl, by="TRT01P", include=["AGE", "SEX"])

        assert isinstance(tbl, TblSummaryResult)
        assert isinstance(tbl.ard, pd.DataFrame)
        assert {"AGE", "SEX"} <= set(tbl.ard["variable"].unique())
        # wide table has one column per arm plus Total
        table = tbl.to_table()
        assert "Drug A" in table.columns
        assert "Drug B" in table.columns
        assert "Total" in table.columns

    def test_ard_matches_session_engine(self, adsl):
        """ARD values are identical to the underlying ClinicalSession."""
        from py4csr.clinical import ClinicalSession

        tbl = tbl_summary(data=adsl, by="TRT01P", include=["AGE"])

        session = ClinicalSession(uri="ref")
        session.define_report(dataset=adsl, subjid="USUBJID")
        session.add_trt(name="TRT01P", decode="TRT01P")
        session.add_var(name="AGE", label="AGE")
        session.generate()

        ref = session.generated_data.set_index(["treatment", "statistic"])["value"]
        got = tbl.ard.set_index(["treatment", "statistic"])["value"]
        pd.testing.assert_series_equal(
            ref.sort_index(), got.sort_index(), check_names=False
        )

    def test_statistic_and_label_and_type_overrides(self, adsl):
        """statistic=, label= and type= are honored."""
        tbl = tbl_summary(
            data=adsl,
            by="TRT01P",
            include=["AGE"],
            statistic={"AGE": "n mean sd"},
            label={"AGE": "Age (years)"},
            type={"AGE": "continuous"},
        )
        assert set(tbl.ard["statistic"].unique()) == {"N", "Mean", "SD"}
        assert tbl.ard["variable_label"].iloc[0] == "Age (years)"

    def test_where_filter(self, adsl):
        """where= restricts the analysis population."""
        tbl = tbl_summary(
            data=adsl, by="TRT01P", include=["AGE"], where="SAFFL == 'Y'"
        )
        total_n = tbl.ard[
            (tbl.ard["treatment"] == "Total") & (tbl.ard["statistic"] == "N")
        ]["value"].iloc[0]
        assert total_n == (adsl["SAFFL"] == "Y").sum()

    def test_total_false_drops_total_column(self, adsl):
        """total=False removes the Total column."""
        tbl = tbl_summary(data=adsl, by="TRT01P", include=["AGE"], total=False)
        assert "Total" not in tbl.to_table().columns
        assert "Total" not in tbl.ard["treatment"].astype(str).unique()

    def test_default_test_selection_recorded(self, adsl):
        """Default p-values use gtsummary tests and are recorded."""
        tbl = tbl_summary(data=adsl, by="TRT01P", include=["AGE", "SEX"])
        assert tbl.p_value_tests["AGE"] == "Wilcoxon rank-sum test"
        assert tbl.p_value_tests["SEX"] == "Pearson's Chi-squared test"
        assert tbl.p_values["AGE"] != "N/A"

    def test_test_override(self, adsl):
        """test= override is honored (single string and per-variable dict)."""
        tbl = tbl_summary(data=adsl, by="TRT01P", include=["AGE"], test="ttest")
        assert tbl.p_value_tests["AGE"] == "Two-sample t-test"

        tbl2 = tbl_summary(
            data=adsl, by="TRT01P", include=["AGE", "SEX"],
            test={"SEX": "fisher"},
        )
        assert tbl2.p_value_tests["SEX"] == "Fisher's exact test"
        assert tbl2.p_value_tests["AGE"] == "Wilcoxon rank-sum test"

    def test_input_validation(self, adsl):
        """Clear errors for bad inputs."""
        with pytest.raises(TypeError, match="DataFrame"):
            tbl_summary(data=[1, 2], by="TRT01P", include=["AGE"])
        with pytest.raises(ValueError, match="not found"):
            tbl_summary(data=adsl, by="NOPE", include=["AGE"])
        with pytest.raises(ValueError, match="not found"):
            tbl_summary(data=adsl, by="TRT01P", include=["NOPE"])
        with pytest.raises(ValueError, match="at least one"):
            tbl_summary(data=adsl, by="TRT01P", include=[])
        with pytest.raises(ValueError, match="continuous"):
            tbl_summary(
                data=adsl, by="TRT01P", include=["AGE"], type={"AGE": "weird"}
            )

    def test_exported_at_top_level(self):
        """py4csr.tbl_summary is importable from the package root."""
        assert callable(py4csr.tbl_summary)
        assert py4csr.TblSummaryResult is TblSummaryResult
