"""
Unit tests for py4csr.reporting.table_specification module.

Tests TableSpecification class.
"""

import pandas as pd
import pytest

from py4csr.reporting.table_specification import TableSpecification
from py4csr.config.report_config import ReportConfig


class TestTableSpecification:
    """Test TableSpecification class."""

    def test_basic_initialization(self):
        """Test basic TableSpecification initialization."""
        config = ReportConfig()
        datasets = {"adsl": pd.DataFrame()}
        populations = {"safety": "SAFFL=='Y'"}
        treatments = {"var": "TRT01P"}

        spec = TableSpecification(
            type="demographics",
            config=config,
            datasets=datasets,
            populations=populations,
            treatments=treatments,
        )

        assert spec.type == "demographics"
        assert spec.config is not None
        assert "adsl" in spec.datasets

    def test_with_title_and_subtitle(self):
        """Test with title and subtitle."""
        config = ReportConfig()
        datasets = {}
        populations = {}
        treatments = {}

        spec = TableSpecification(
            type="demographics",
            config=config,
            datasets=datasets,
            populations=populations,
            treatments=treatments,
            title="Demographics Table",
            subtitle="Safety Population",
        )

        assert spec.title == "Demographics Table"
        assert spec.subtitle == "Safety Population"

    def test_with_footnotes(self):
        """Test with footnotes."""
        config = ReportConfig()
        datasets = {}
        populations = {}
        treatments = {}

        footnotes = ["Footnote 1", "Footnote 2"]

        spec = TableSpecification(
            type="demographics",
            config=config,
            datasets=datasets,
            populations=populations,
            treatments=treatments,
            footnotes=footnotes,
        )

        assert spec.footnotes is not None
        assert len(spec.footnotes) == 2

    def test_with_variables(self):
        """Test with variables."""
        config = ReportConfig()
        datasets = {}
        populations = {}
        treatments = {}

        variables = ["AGE", "SEX", "RACE"]

        spec = TableSpecification(
            type="demographics",
            config=config,
            datasets=datasets,
            populations=populations,
            treatments=treatments,
            variables=variables,
        )

        assert spec.variables is not None
        assert len(spec.variables) == 3

    def test_get_filename_demographics(self):
        """Test get_filename for demographics table."""
        config = ReportConfig()
        datasets = {}
        populations = {}
        treatments = {}

        spec = TableSpecification(
            type="demographics",
            config=config,
            datasets=datasets,
            populations=populations,
            treatments=treatments,
        )

        filename = spec.get_filename()
        assert filename == "tlf_base"

    def test_get_filename_disposition(self):
        """Test get_filename for disposition table."""
        config = ReportConfig()
        datasets = {}
        populations = {}
        treatments = {}

        spec = TableSpecification(
            type="disposition",
            config=config,
            datasets=datasets,
            populations=populations,
            treatments=treatments,
        )

        filename = spec.get_filename()
        assert filename == "tbl_disp"

    def test_get_filename_ae_summary(self):
        """Test get_filename for AE summary table."""
        config = ReportConfig()
        datasets = {}
        populations = {}
        treatments = {}

        spec = TableSpecification(
            type="ae_summary",
            config=config,
            datasets=datasets,
            populations=populations,
            treatments=treatments,
        )

        filename = spec.get_filename()
        assert filename == "tlf_ae_summary"

    def test_get_filename_unknown_type(self):
        """Test get_filename for unknown table type."""
        config = ReportConfig()
        datasets = {}
        populations = {}
        treatments = {}

        spec = TableSpecification(
            type="unknown_type",
            config=config,
            datasets=datasets,
            populations=populations,
            treatments=treatments,
        )

        filename = spec.get_filename()
        assert filename == "tlf_unknown_type"

    def test_with_all_optional_parameters(self):
        """Test with all optional parameters."""
        config = ReportConfig()
        datasets = {"adsl": pd.DataFrame()}
        populations = {"safety": "SAFFL=='Y'"}
        treatments = {"var": "TRT01P"}

        spec = TableSpecification(
            type="demographics",
            config=config,
            datasets=datasets,
            populations=populations,
            treatments=treatments,
            title="Demographics Table",
            subtitle="Safety Population",
            footnotes=["Footnote 1"],
            population="safety",
            variables=["AGE", "SEX"],
            statistics=["n", "mean"],
            grouping=["TRT01P"],
            filters={"AGE": ">= 18"},
            analysis_type="descriptive",
            parameters=["param1"],
            visits=["BASELINE"],
            endpoint="PRIMARY",
            time_var="AVAL",
            event_var="CNSR",
            min_frequency=5,
            sort_by="frequency",
            include_total=True,
            page_by="VISIT",
            custom_template="custom"
        )

        assert spec.type == "demographics"
        assert spec.title == "Demographics Table"
        assert spec.subtitle == "Safety Population"
        assert len(spec.footnotes) == 1
        assert spec.population == "safety"
        assert len(spec.variables) == 2
        assert len(spec.statistics) == 2
        assert len(spec.grouping) == 1
        assert spec.filters is not None
        assert spec.analysis_type == "descriptive"
        assert len(spec.parameters) == 1
        assert len(spec.visits) == 1
        assert spec.endpoint == "PRIMARY"
        assert spec.time_var == "AVAL"
        assert spec.event_var == "CNSR"
        assert spec.min_frequency == 5
        assert spec.sort_by == "frequency"
        assert spec.include_total is True
        assert spec.page_by == "VISIT"
        assert spec.custom_template == "custom"

    def test_with_statistics(self):
        """Test with statistics."""
        config = ReportConfig()
        datasets = {}
        populations = {}
        treatments = {}

        statistics = ["N", "MEAN", "STD", "MEDIAN"]

        spec = TableSpecification(
            type="demographics",
            config=config,
            datasets=datasets,
            populations=populations,
            treatments=treatments,
            statistics=statistics,
        )

        assert spec.statistics is not None
        assert "MEAN" in spec.statistics

    def test_get_filename_demographics(self):
        """Test filename generation for demographics."""
        config = ReportConfig()
        datasets = {}
        populations = {}
        treatments = {}

        spec = TableSpecification(
            type="demographics",
            config=config,
            datasets=datasets,
            populations=populations,
            treatments=treatments,
        )

        filename = spec.get_filename()
        assert filename == "tlf_base"

    def test_get_filename_ae_summary(self):
        """Test filename generation for AE summary."""
        config = ReportConfig()
        datasets = {}
        populations = {}
        treatments = {}

        spec = TableSpecification(
            type="ae_summary",
            config=config,
            datasets=datasets,
            populations=populations,
            treatments=treatments,
        )

        filename = spec.get_filename()
        assert filename == "tlf_ae_summary"

    def test_get_filename_disposition(self):
        """Test filename generation for disposition."""
        config = ReportConfig()
        datasets = {}
        populations = {}
        treatments = {}

        spec = TableSpecification(
            type="disposition",
            config=config,
            datasets=datasets,
            populations=populations,
            treatments=treatments,
        )

        filename = spec.get_filename()
        assert filename == "tbl_disp"

    def test_default_population(self):
        """Test default population."""
        config = ReportConfig()
        datasets = {}
        populations = {}
        treatments = {}

        spec = TableSpecification(
            type="demographics",
            config=config,
            datasets=datasets,
            populations=populations,
            treatments=treatments,
        )

        assert spec.population == "safety"

    def test_custom_population(self):
        """Test custom population."""
        config = ReportConfig()
        datasets = {}
        populations = {}
        treatments = {}

        spec = TableSpecification(
            type="demographics",
            config=config,
            datasets=datasets,
            populations=populations,
            treatments=treatments,
            population="efficacy",
        )

        assert spec.population == "efficacy"

    def test_with_filters(self):
        """Test with filters."""
        config = ReportConfig()
        datasets = {}
        populations = {}
        treatments = {}

        filters = {"AGE": ">= 18", "SEX": "== 'M'"}

        spec = TableSpecification(
            type="demographics",
            config=config,
            datasets=datasets,
            populations=populations,
            treatments=treatments,
            filters=filters,
        )

        assert spec.filters is not None
        assert "AGE" in spec.filters

    def test_with_grouping(self):
        """Test with grouping variables."""
        config = ReportConfig()
        datasets = {}
        populations = {}
        treatments = {}

        grouping = ["COUNTRY", "SITE"]

        spec = TableSpecification(
            type="demographics",
            config=config,
            datasets=datasets,
            populations=populations,
            treatments=treatments,
            grouping=grouping,
        )

        assert spec.grouping is not None
        assert "COUNTRY" in spec.grouping

    def test_include_total_default(self):
        """Test default include_total."""
        config = ReportConfig()
        datasets = {}
        populations = {}
        treatments = {}

        spec = TableSpecification(
            type="demographics",
            config=config,
            datasets=datasets,
            populations=populations,
            treatments=treatments,
        )

        assert spec.include_total is True

    def test_include_total_false(self):
        """Test include_total set to False."""
        config = ReportConfig()
        datasets = {}
        populations = {}
        treatments = {}

        spec = TableSpecification(
            type="demographics",
            config=config,
            datasets=datasets,
            populations=populations,
            treatments=treatments,
            include_total=False,
        )

        assert spec.include_total is False


class TestTableSpecificationWorkflow:
    """Test complete table specification workflow."""

    def test_demographics_specification(self, sample_adsl):
        """Test creating demographics table specification."""
        config = ReportConfig()
        datasets = {"adsl": sample_adsl}
        populations = {"safety": "SAFFL=='Y'"}
        treatments = {"var": "TRT01P", "decode": "TRT01A"}

        spec = TableSpecification(
            type="demographics",
            config=config,
            datasets=datasets,
            populations=populations,
            treatments=treatments,
            title="Baseline Demographics and Characteristics",
            subtitle="Safety Population",
            footnotes=["All randomized subjects"],
            variables=["AGE", "SEX", "RACE"],
            statistics=["N", "MEAN", "STD"],
            population="safety",
            include_total=True,
        )

        assert spec.type == "demographics"
        assert spec.title is not None
        assert len(spec.variables) == 3
        assert spec.get_filename() == "tlf_base"

    def test_ae_summary_specification(self, sample_adae):
        """Test creating AE summary table specification."""
        config = ReportConfig()
        datasets = {"adae": sample_adae}
        populations = {"safety": "SAFFL=='Y'"}
        treatments = {"var": "TRT01P"}

        spec = TableSpecification(
            type="ae_summary",
            config=config,
            datasets=datasets,
            populations=populations,
            treatments=treatments,
            title="Adverse Events Summary",
            subtitle="Safety Population",
            min_frequency=5,
            sort_by="frequency",
        )

        assert spec.type == "ae_summary"
        assert spec.min_frequency == 5
        assert spec.sort_by == "frequency"
        assert spec.get_filename() == "tlf_ae_summary"


class TestTableSpecificationEdgeCases:
    """Test edge cases in table specification."""

    def test_empty_datasets(self):
        """Test with empty datasets."""
        config = ReportConfig()
        datasets = {}
        populations = {}
        treatments = {}

        spec = TableSpecification(
            type="demographics",
            config=config,
            datasets=datasets,
            populations=populations,
            treatments=treatments,
        )

        assert len(spec.datasets) == 0

    def test_no_variables(self):
        """Test with no variables specified."""
        config = ReportConfig()
        datasets = {}
        populations = {}
        treatments = {}

        spec = TableSpecification(
            type="demographics",
            config=config,
            datasets=datasets,
            populations=populations,
            treatments=treatments,
        )

        assert spec.variables is None

    def test_no_statistics(self):
        """Test with no statistics specified."""
        config = ReportConfig()
        datasets = {}
        populations = {}
        treatments = {}

        spec = TableSpecification(
            type="demographics",
            config=config,
            datasets=datasets,
            populations=populations,
            treatments=treatments,
        )

        assert spec.statistics is None

