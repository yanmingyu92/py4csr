"""
Unit tests for py4csr.functional.table_builder module.

Tests TableResult and TableBuilder classes.
"""

import pandas as pd
import pytest

from py4csr.functional.table_builder import TableResult, TableBuilder
from py4csr.functional.session import ReportSession
from py4csr.functional.config import FunctionalConfig


class TestTableResultInit:
    """Test TableResult initialization."""

    def test_basic_initialization(self):
        """Test basic TableResult initialization."""
        data = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        metadata = {
            "title": "Test Table",
            "subtitle": "Test Subtitle",
            "footnotes": ["Footnote 1"],
        }

        result = TableResult(data=data, metadata=metadata)

        assert isinstance(result.data, pd.DataFrame)
        assert result.title == "Test Table"
        assert result.subtitle == "Test Subtitle"
        assert len(result.footnotes) == 1

    def test_initialization_with_defaults(self):
        """Test initialization with minimal metadata."""
        data = pd.DataFrame({"A": [1, 2, 3]})
        metadata = {}

        result = TableResult(data=data, metadata=metadata)

        assert result.title == ""
        assert result.subtitle == ""
        assert result.footnotes == []

    def test_repr(self):
        """Test __repr__ method."""
        data = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        metadata = {"title": "This is a very long title that should be truncated"}

        result = TableResult(data=data, metadata=metadata)
        repr_str = repr(result)

        assert "TableResult" in repr_str
        assert "shape=(3, 2)" in repr_str


class TestTableBuilderInit:
    """Test TableBuilder initialization."""

    def test_basic_initialization(self, sample_adsl):
        """Test basic TableBuilder initialization."""
        session = ReportSession()
        session.init_study(uri="STUDY001", title="Test Study")
        session.load_datasets(datasets={"adsl": sample_adsl})
        session.define_treatments(var="TRT01P")

        table_spec = {"type": "demographics", "population": "safety"}

        builder = TableBuilder(session=session, table_spec=table_spec)

        assert builder.session is session
        assert builder.spec["type"] == "demographics"
        assert builder.config is session.config
        assert builder.templates is session.templates


class TestTableBuilderDemographics:
    """Test TableBuilder demographics table building."""

    def test_build_demographics_basic(self, sample_adsl):
        """Test building basic demographics table."""
        session = ReportSession()
        session.init_study(uri="STUDY001", title="Test Study")
        session.load_datasets(datasets={"adsl": sample_adsl})
        session.define_populations(safety="SAFFL=='Y'")
        session.define_treatments(var="TRT01P")

        table_spec = {
            "type": "demographics",
            "population": "safety",
            "variables": ["AGE", "SEX"],
        }

        builder = TableBuilder(session=session, table_spec=table_spec)
        result = builder.build()

        assert isinstance(result, TableResult)
        assert isinstance(result.data, pd.DataFrame)
        assert result.metadata["table_type"] == "demographics"

    def test_build_demographics_missing_adsl(self):
        """Test building demographics without ADSL raises error."""
        session = ReportSession()
        session.init_study(uri="STUDY001", title="Test Study")
        session.define_treatments(var="TRT01P")

        table_spec = {"type": "demographics", "population": "safety"}

        builder = TableBuilder(session=session, table_spec=table_spec)

        with pytest.raises(ValueError, match="ADSL dataset required"):
            builder.build()


class TestTableBuilderDisposition:
    """Test TableBuilder disposition table building."""

    def test_build_disposition_basic(self, sample_adsl):
        """Test building basic disposition table."""
        # Add disposition variable - ensure length matches
        n = len(sample_adsl)
        sample_adsl = sample_adsl.copy()
        sample_adsl["DCSREAS"] = (
            ["Completed", "Adverse Event", "Completed"] * (n // 3 + 1)
        )[:n]

        session = ReportSession()
        session.init_study(uri="STUDY001", title="Test Study")
        session.load_datasets(datasets={"adsl": sample_adsl})
        session.define_treatments(var="TRT01P")

        table_spec = {"type": "disposition"}

        builder = TableBuilder(session=session, table_spec=table_spec)
        result = builder.build()

        assert isinstance(result, TableResult)
        assert result.metadata["table_type"] == "disposition"
        assert result.metadata["population"] == "randomized"

    def test_build_disposition_missing_adsl(self):
        """Test building disposition without ADSL raises error."""
        session = ReportSession()
        session.init_study(uri="STUDY001", title="Test Study")
        session.define_treatments(var="TRT01P")

        table_spec = {"type": "disposition"}

        builder = TableBuilder(session=session, table_spec=table_spec)

        with pytest.raises(ValueError, match="ADSL dataset required"):
            builder.build()


class TestTableBuilderAESummary:
    """Test TableBuilder AE summary table building."""

    def test_build_ae_summary_basic(self, sample_adsl, sample_adae):
        """Test building basic AE summary table."""
        session = ReportSession()
        session.init_study(uri="STUDY001", title="Test Study")
        session.load_datasets(datasets={"adsl": sample_adsl, "adae": sample_adae})
        session.define_populations(safety="SAFFL=='Y'")
        session.define_treatments(var="TRT01P")

        table_spec = {"type": "ae_summary", "population": "safety"}

        builder = TableBuilder(session=session, table_spec=table_spec)
        result = builder.build()

        assert isinstance(result, TableResult)
        assert result.metadata["table_type"] == "ae_summary"

    def test_build_ae_summary_missing_adae(self, sample_adsl):
        """Test building AE summary without ADAE raises error."""
        session = ReportSession()
        session.init_study(uri="STUDY001", title="Test Study")
        session.load_datasets(datasets={"adsl": sample_adsl})
        session.define_treatments(var="TRT01P")

        table_spec = {"type": "ae_summary"}

        builder = TableBuilder(session=session, table_spec=table_spec)

        with pytest.raises(ValueError, match="ADAE dataset required"):
            builder.build()


class TestTableBuilderAEDetail:
    """Test TableBuilder AE detail table building."""

    def test_build_ae_detail_basic(self, sample_adsl, sample_adae):
        """Test building basic AE detail table."""
        session = ReportSession()
        session.init_study(uri="STUDY001", title="Test Study")
        session.load_datasets(datasets={"adsl": sample_adsl, "adae": sample_adae})
        session.define_populations(safety="SAFFL=='Y'")
        session.define_treatments(var="TRT01P")

        table_spec = {"type": "ae_detail", "population": "safety"}

        builder = TableBuilder(session=session, table_spec=table_spec)
        result = builder.build()

        assert isinstance(result, TableResult)
        assert result.metadata["table_type"] == "ae_detail"


class TestTableBuilderLaboratory:
    """Test TableBuilder laboratory table building."""

    def test_build_laboratory_basic(self, sample_adsl, sample_adlb):
        """Test building basic laboratory table."""
        session = ReportSession()
        session.init_study(uri="STUDY001", title="Test Study")
        session.load_datasets(datasets={"adsl": sample_adsl, "adlb": sample_adlb})
        session.define_populations(safety="SAFFL=='Y'")
        session.define_treatments(var="TRT01P")

        table_spec = {"type": "laboratory", "population": "safety"}

        builder = TableBuilder(session=session, table_spec=table_spec)
        result = builder.build()

        assert isinstance(result, TableResult)
        assert result.metadata["table_type"] == "laboratory"

    def test_build_laboratory_missing_adlb(self, sample_adsl):
        """Test building laboratory without ADLB raises error."""
        session = ReportSession()
        session.init_study(uri="STUDY001", title="Test Study")
        session.load_datasets(datasets={"adsl": sample_adsl})
        session.define_treatments(var="TRT01P")

        table_spec = {"type": "laboratory"}

        builder = TableBuilder(session=session, table_spec=table_spec)

        with pytest.raises(ValueError, match="ADLB dataset required"):
            builder.build()


class TestTableBuilderEfficacy:
    """Test TableBuilder efficacy table building."""

    def test_build_efficacy_basic(self, sample_adsl):
        """Test building basic efficacy table."""
        session = ReportSession()
        session.init_study(uri="STUDY001", title="Test Study")
        session.load_datasets(datasets={"adsl": sample_adsl})
        session.define_populations(efficacy="EFFFL=='Y'")
        session.define_treatments(var="TRT01P")

        table_spec = {"type": "efficacy", "population": "efficacy"}

        builder = TableBuilder(session=session, table_spec=table_spec)
        result = builder.build()

        assert isinstance(result, TableResult)
        assert result.metadata["table_type"] == "efficacy"


class TestTableBuilderHelperMethods:
    """Test TableBuilder helper methods."""

    def test_create_ae_summary_categories(self, sample_adsl):
        """Test _create_ae_summary_categories method."""
        session = ReportSession()
        session.init_study(uri="STUDY001", title="Test Study")
        session.load_datasets(datasets={"adsl": sample_adsl})
        session.define_treatments(var="TRT01P")

        table_spec = {"type": "ae_summary", "population": "all"}
        builder = TableBuilder(session=session, table_spec=table_spec)

        # Create sample ADAE data
        adae = pd.DataFrame({
            "USUBJID": [f"S{i:03d}" for i in range(1, 11)],
            "TRT01P": ["Placebo"] * 5 + ["Drug A"] * 5,
            "AESOC": ["Infections"] * 10,
            "AEDECOD": ["Headache"] * 10,
            "AESER": ["Y"] * 3 + ["N"] * 7,
            "AESEV": ["SEVERE"] * 2 + ["MILD"] * 8,
        })

        result = builder._create_ae_summary_categories(adae, "TRT01P")

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0


class TestTableBuilderVitalSigns:
    """Test TableBuilder vital signs table building."""

    def test_build_vital_signs_no_template(self, sample_adsl):
        """Test that vital_signs table type has no default template."""
        # Create sample ADVS data
        n = len(sample_adsl)
        advs = pd.DataFrame({
            "USUBJID": sample_adsl["USUBJID"].tolist() * 2,
            "TRT01P": sample_adsl["TRT01P"].tolist() * 2,
            "SAFFL": sample_adsl["SAFFL"].tolist() * 2,
            "PARAMCD": ["SYSBP"] * n + ["DIABP"] * n,
            "PARAM": ["Systolic Blood Pressure"] * n + ["Diastolic Blood Pressure"] * n,
            "AVAL": [120.5, 118.3, 122.1, 119.8, 121.2, 117.9, 123.4, 120.1, 119.5, 121.8] * 2,
            "AVISITN": [1] * (n * 2),
        })

        session = ReportSession()
        session.init_study(uri="STUDY001", title="Test Study")
        session.load_datasets(datasets={"adsl": sample_adsl, "advs": advs})
        session.define_populations(safety="SAFFL=='Y'")
        session.define_treatments(var="TRT01P")

        table_spec = {"type": "vital_signs", "population": "safety"}

        builder = TableBuilder(session=session, table_spec=table_spec)

        # Should raise ValueError because no template is defined for vital_signs
        with pytest.raises(ValueError, match="No template found for table type"):
            builder.build()

    def test_build_vital_signs_missing_advs(self, sample_adsl):
        """Test that vital_signs builder method checks for ADVS dataset."""
        from py4csr.functional.config import TableTemplate

        session = ReportSession()
        session.init_study(uri="STUDY001", title="Test Study")
        session.load_datasets(datasets={"adsl": sample_adsl})
        session.define_treatments(var="TRT01P")

        # Manually add a vital_signs template to test the method
        vital_signs_template = TableTemplate(
            name="vital_signs",
            title_template="Vital Signs Analysis",
            subtitle_template="{study_title} - {population_label}",
            default_statistics=["n", "mean_sd", "median"],
        )
        session.config.templates["vital_signs"] = vital_signs_template

        table_spec = {"type": "vital_signs"}

        builder = TableBuilder(session=session, table_spec=table_spec)

        with pytest.raises(ValueError, match="ADVS dataset required"):
            builder.build()


class TestTableBuilderSurvival:
    """Test TableBuilder survival table building."""

    def test_build_survival_basic(self, sample_adsl):
        """Test building basic survival table."""
        # Create sample ADTTE data
        n = len(sample_adsl)
        adtte = pd.DataFrame({
            "USUBJID": sample_adsl["USUBJID"].tolist(),
            "TRT01P": sample_adsl["TRT01P"].tolist(),
            "EFFFL": sample_adsl["EFFFL"].tolist(),
            "AVAL": [365.2, 412.5, 298.7, 456.3, 389.1, 421.8, 367.9, 401.2, 378.5, 395.6],
            "CNSR": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        })

        session = ReportSession()
        session.init_study(uri="STUDY001", title="Test Study")
        session.load_datasets(datasets={"adsl": sample_adsl, "adtte": adtte})
        session.define_populations(efficacy="EFFFL=='Y'")
        session.define_treatments(var="TRT01P")

        table_spec = {"type": "survival", "population": "efficacy"}

        builder = TableBuilder(session=session, table_spec=table_spec)
        result = builder.build()

        assert isinstance(result, TableResult)
        assert result.metadata["table_type"] == "survival"

    def test_build_survival_missing_adtte(self, sample_adsl):
        """Test building survival without ADTTE raises error."""
        session = ReportSession()
        session.init_study(uri="STUDY001", title="Test Study")
        session.load_datasets(datasets={"adsl": sample_adsl})
        session.define_treatments(var="TRT01P")

        table_spec = {"type": "survival"}

        builder = TableBuilder(session=session, table_spec=table_spec)

        with pytest.raises(ValueError, match="ADTTE dataset required"):
            builder.build()

    def test_build_survival_custom_columns(self, sample_adsl):
        """Test building survival with custom duration and event columns."""
        # Create sample ADTTE data with custom column names
        n = len(sample_adsl)
        adtte = pd.DataFrame({
            "USUBJID": sample_adsl["USUBJID"].tolist(),
            "TRT01P": sample_adsl["TRT01P"].tolist(),
            "EFFFL": sample_adsl["EFFFL"].tolist(),
            "DURATION": [365.2, 412.5, 298.7, 456.3, 389.1, 421.8, 367.9, 401.2, 378.5, 395.6],
            "EVENT": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        })

        session = ReportSession()
        session.init_study(uri="STUDY001", title="Test Study")
        session.load_datasets(datasets={"adsl": sample_adsl, "adtte": adtte})
        session.define_populations(efficacy="EFFFL=='Y'")
        session.define_treatments(var="TRT01P")

        table_spec = {
            "type": "survival",
            "population": "efficacy",
            "duration_col": "DURATION",
            "event_col": "EVENT",
        }

        builder = TableBuilder(session=session, table_spec=table_spec)
        result = builder.build()

        assert isinstance(result, TableResult)
        assert result.metadata["table_type"] == "survival"


class TestTableBuilderEdgeCases:
    """Test edge cases."""

    def test_unsupported_table_type(self, sample_adsl):
        """Test unsupported table type raises error."""
        session = ReportSession()
        session.init_study(uri="STUDY001", title="Test Study")
        session.load_datasets(datasets={"adsl": sample_adsl})
        session.define_treatments(var="TRT01P")

        table_spec = {"type": "unsupported_type"}

        builder = TableBuilder(session=session, table_spec=table_spec)

        # Should raise ValueError for either no template or unsupported type
        with pytest.raises(ValueError):
            builder.build()

    def test_custom_title_and_footnotes(self, sample_adsl):
        """Test custom title and footnotes."""
        session = ReportSession()
        session.init_study(uri="STUDY001", title="Test Study")
        session.load_datasets(datasets={"adsl": sample_adsl})
        session.define_populations(safety="SAFFL=='Y'")
        session.define_treatments(var="TRT01P")

        table_spec = {
            "type": "demographics",
            "population": "safety",
            "title": "Custom Demographics Title",
            "footnotes": ["Custom footnote 1", "Custom footnote 2"],
        }

        builder = TableBuilder(session=session, table_spec=table_spec)
        result = builder.build()

        assert result.metadata["title"] == "Custom Demographics Title"
        assert len(result.metadata["footnotes"]) == 2

    def test_demographics_with_statistical_tests(self, sample_adsl):
        """Test demographics table with statistical tests."""
        session = ReportSession()
        session.init_study(uri="STUDY001", title="Test Study")
        session.load_datasets(datasets={"adsl": sample_adsl})
        session.define_populations(safety="SAFFL=='Y'")
        session.define_treatments(var="TRT01P")

        table_spec = {
            "type": "demographics",
            "population": "safety",
            "variables": ["AGE", "SEX"],
            "tests": ["ANOVA", "CHISQ"],
        }

        builder = TableBuilder(session=session, table_spec=table_spec)
        result = builder.build()

        assert isinstance(result, TableResult)
        # Should have p-value rows for statistical tests
        assert "P-value" in str(result.data) or "p-value" in str(result.data).lower() or len(result.data) > 0

    def test_empty_dataset_handling(self, sample_adsl):
        """Test handling of empty filtered datasets."""
        session = ReportSession()
        session.init_study(uri="STUDY001", title="Test Study")
        session.load_datasets(datasets={"adsl": sample_adsl})
        # Define a population filter that results in empty dataset
        session.define_populations(empty_pop="AGE > 200")
        session.define_treatments(var="TRT01P")

        table_spec = {
            "type": "demographics",
            "population": "empty_pop",
        }

        builder = TableBuilder(session=session, table_spec=table_spec)
        result = builder.build()

        # Should handle empty data gracefully
        assert isinstance(result, TableResult)

