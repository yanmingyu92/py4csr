"""
Unit tests for py4csr.reporting.table_result module.

Tests TableResult and ReportResult classes.
"""

import pandas as pd
import pytest
from pathlib import Path

from py4csr.reporting.table_result import TableResult, ReportResult
from py4csr.reporting.rtf_table import RTFTable
from py4csr.config.report_config import ReportConfig


class TestTableResult:
    """Test TableResult class."""

    def test_initialization(self):
        """Test basic TableResult initialization."""
        data = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        rtf_table = RTFTable()
        metadata = {"table_type": "test", "generation_time": "2024-01-01"}

        result = TableResult(data=data, rtf_table=rtf_table, metadata=metadata)

        assert isinstance(result.data, pd.DataFrame)
        assert isinstance(result.rtf_table, RTFTable)
        assert result.metadata["table_type"] == "test"

    def test_with_figures(self):
        """Test TableResult with figures."""
        data = pd.DataFrame({"A": [1, 2, 3]})
        rtf_table = RTFTable()
        metadata = {"table_type": "test"}
        figures = {"plot1": "figure_data"}

        result = TableResult(
            data=data, rtf_table=rtf_table, metadata=metadata, figures=figures
        )

        assert result.figures is not None
        assert "plot1" in result.figures

    def test_with_validation_results(self):
        """Test TableResult with validation results."""
        data = pd.DataFrame({"A": [1, 2, 3]})
        rtf_table = RTFTable()
        metadata = {"table_type": "test"}
        validation = {"passed": True, "warnings": []}

        result = TableResult(
            data=data,
            rtf_table=rtf_table,
            metadata=metadata,
            validation_results=validation,
        )

        assert result.validation_results is not None
        assert result.validation_results["passed"] is True

    def test_get_rtf_content(self):
        """Test getting RTF content."""
        data = pd.DataFrame({"A": [1, 2, 3]})
        rtf_table = RTFTable()
        metadata = {"table_type": "test"}

        result = TableResult(data=data, rtf_table=rtf_table, metadata=metadata)
        content = result.get_rtf_content()

        assert isinstance(content, str)
        assert len(content) > 0

    def test_get_summary(self):
        """Test getting table summary."""
        data = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        rtf_table = RTFTable()
        metadata = {"table_type": "demographics", "generation_time": "2024-01-01"}

        result = TableResult(data=data, rtf_table=rtf_table, metadata=metadata)
        summary = result.get_summary()

        assert isinstance(summary, dict)
        assert summary["table_type"] == "demographics"
        assert summary["n_rows"] == 3
        assert summary["n_columns"] == 2

    def test_get_summary_with_figures(self):
        """Test summary with figures."""
        data = pd.DataFrame({"A": [1, 2, 3]})
        rtf_table = RTFTable()
        metadata = {"table_type": "test"}
        figures = {"plot1": "data1", "plot2": "data2"}

        result = TableResult(
            data=data, rtf_table=rtf_table, metadata=metadata, figures=figures
        )
        summary = result.get_summary()

        assert summary["has_figures"] is True
        assert summary["n_figures"] == 2

    def test_write_rtf(self, tmp_path):
        """Test writing RTF to file."""
        data = pd.DataFrame({"A": [1, 2, 3]})
        rtf_table = RTFTable()
        metadata = {"table_type": "test"}

        result = TableResult(data=data, rtf_table=rtf_table, metadata=metadata)
        output_file = tmp_path / "test.rtf"
        result.write_rtf(output_file)

        assert output_file.exists()

    def test_to_rtf_alias(self, tmp_path):
        """Test to_rtf as alias for write_rtf."""
        data = pd.DataFrame({"A": [1, 2, 3]})
        rtf_table = RTFTable()
        metadata = {"table_type": "test"}

        result = TableResult(data=data, rtf_table=rtf_table, metadata=metadata)
        output_file = tmp_path / "test.rtf"
        result.to_rtf(output_file)

        assert output_file.exists()

    def test_save_data_csv(self, tmp_path):
        """Test saving data as CSV."""
        data = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        rtf_table = RTFTable()
        metadata = {"table_type": "test"}

        result = TableResult(data=data, rtf_table=rtf_table, metadata=metadata)
        output_file = tmp_path / "test.csv"
        result.save_data(output_file, format="csv")

        assert output_file.exists()
        loaded_data = pd.read_csv(output_file)
        assert len(loaded_data) == 3

    def test_save_data_excel(self, tmp_path):
        """Test saving data as Excel."""
        data = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        rtf_table = RTFTable()
        metadata = {"table_type": "test"}

        result = TableResult(data=data, rtf_table=rtf_table, metadata=metadata)
        output_file = tmp_path / "test.xlsx"
        result.save_data(output_file, format="excel")

        assert output_file.exists()

    def test_save_data_xlsx(self, tmp_path):
        """Test saving data as xlsx."""
        data = pd.DataFrame({"A": [1, 2, 3]})
        rtf_table = RTFTable()
        metadata = {"table_type": "test"}

        result = TableResult(data=data, rtf_table=rtf_table, metadata=metadata)
        output_file = tmp_path / "test.xlsx"
        result.save_data(output_file, format="xlsx")

        assert output_file.exists()

    def test_save_data_sas_not_implemented(self, tmp_path):
        """Test that SAS export raises NotImplementedError."""
        data = pd.DataFrame({"A": [1, 2, 3]})
        rtf_table = RTFTable()
        metadata = {"table_type": "test"}

        result = TableResult(data=data, rtf_table=rtf_table, metadata=metadata)
        output_file = tmp_path / "test.sas7bdat"

        with pytest.raises(NotImplementedError, match="SAS export not yet implemented"):
            result.save_data(output_file, format="sas")

    def test_save_data_unsupported_format(self, tmp_path):
        """Test that unsupported format raises ValueError."""
        data = pd.DataFrame({"A": [1, 2, 3]})
        rtf_table = RTFTable()
        metadata = {"table_type": "test"}

        result = TableResult(data=data, rtf_table=rtf_table, metadata=metadata)
        output_file = tmp_path / "test.txt"

        with pytest.raises(ValueError, match="Unsupported format"):
            result.save_data(output_file, format="txt")

    def test_get_summary_with_validation(self):
        """Test summary with validation results."""
        data = pd.DataFrame({"A": [1, 2, 3]})
        rtf_table = RTFTable()
        metadata = {"table_type": "test"}
        validation = {"passed": False}

        result = TableResult(
            data=data,
            rtf_table=rtf_table,
            metadata=metadata,
            validation_results=validation,
        )
        summary = result.get_summary()

        assert summary["validation_passed"] is False

    def test_write_rtf(self, temp_output_dir):
        """Test writing RTF to file."""
        data = pd.DataFrame({"A": [1, 2, 3]})
        rtf_table = RTFTable()
        metadata = {"table_type": "test"}

        result = TableResult(data=data, rtf_table=rtf_table, metadata=metadata)
        output_file = temp_output_dir / "test_table.rtf"

        result.write_rtf(output_file)

        assert output_file.exists()

    def test_to_rtf_alias(self, temp_output_dir):
        """Test to_rtf as alias for write_rtf."""
        data = pd.DataFrame({"A": [1, 2, 3]})
        rtf_table = RTFTable()
        metadata = {"table_type": "test"}

        result = TableResult(data=data, rtf_table=rtf_table, metadata=metadata)
        output_file = temp_output_dir / "test_table2.rtf"

        result.to_rtf(output_file)

        assert output_file.exists()


class TestReportResult:
    """Test ReportResult class."""

    def test_initialization(self):
        """Test basic ReportResult initialization."""
        metadata = {"study_id": "STUDY001", "title": "Test Study"}
        generated_files = [Path("file1.rtf"), Path("file2.rtf")]
        summary = {"n_tables": 2, "n_files": 2}
        config = ReportConfig()

        result = ReportResult(
            metadata=metadata,
            generated_files=generated_files,
            summary=summary,
            config=config,
        )

        assert result.metadata["study_id"] == "STUDY001"
        assert len(result.generated_files) == 2
        assert result.summary["n_tables"] == 2

    def test_with_table_results(self):
        """Test ReportResult with table results."""
        metadata = {"study_id": "STUDY001"}
        generated_files = []
        summary = {}
        config = ReportConfig()

        data = pd.DataFrame({"A": [1, 2, 3]})
        rtf_table = RTFTable()
        table_metadata = {"table_type": "test"}
        table_result = TableResult(
            data=data, rtf_table=rtf_table, metadata=table_metadata
        )

        table_results = {"demographics": table_result}

        result = ReportResult(
            metadata=metadata,
            generated_files=generated_files,
            summary=summary,
            config=config,
            table_results=table_results,
        )

        assert result.table_results is not None
        assert "demographics" in result.table_results

    def test_with_errors(self):
        """Test ReportResult with errors."""
        metadata = {"study_id": "STUDY001"}
        generated_files = []
        summary = {}
        config = ReportConfig()
        errors = ["Error 1", "Error 2"]

        result = ReportResult(
            metadata=metadata,
            generated_files=generated_files,
            summary=summary,
            config=config,
            errors=errors,
        )

        assert result.errors is not None
        assert len(result.errors) == 2


class TestTableResultWorkflow:
    """Test complete table result workflow."""

    def test_create_and_save(self, temp_output_dir):
        """Test creating and saving table result."""
        # Create table data
        data = pd.DataFrame(
            {
                "Treatment": ["Placebo", "Drug A", "Drug B"],
                "N": [30, 35, 32],
                "Mean Age": [45.2, 47.1, 46.5],
            }
        )

        # Create RTF table
        rtf_table = RTFTable()
        rtf_table.rtf_title("Demographics Table")
        rtf_table.rtf_body(data)

        # Create metadata
        metadata = {
            "table_type": "demographics",
            "generation_time": "2024-01-01 12:00:00",
            "population": "safety",
        }

        # Create result
        result = TableResult(data=data, rtf_table=rtf_table, metadata=metadata)

        # Get summary
        summary = result.get_summary()
        assert summary["table_type"] == "demographics"
        assert summary["n_rows"] == 3

        # Save to file
        output_file = temp_output_dir / "demographics.rtf"
        result.write_rtf(output_file)
        assert output_file.exists()

    def test_multiple_tables_report(self):
        """Test report with multiple tables."""
        metadata = {
            "study_id": "STUDY001",
            "title": "Phase III Study",
            "date": "2024-01-01",
        }

        generated_files = [
            Path("demographics.rtf"),
            Path("ae_summary.rtf"),
            Path("efficacy.rtf"),
        ]

        summary = {
            "n_tables": 3,
            "n_files": 3,
            "generation_time": "2024-01-01 12:00:00",
        }

        config = ReportConfig()

        result = ReportResult(
            metadata=metadata,
            generated_files=generated_files,
            summary=summary,
            config=config,
        )

        assert len(result.generated_files) == 3
        assert result.summary["n_tables"] == 3


class TestTableResultEdgeCases:
    """Test edge cases in table results."""

    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        data = pd.DataFrame()
        rtf_table = RTFTable()
        metadata = {"table_type": "test"}

        result = TableResult(data=data, rtf_table=rtf_table, metadata=metadata)
        summary = result.get_summary()

        assert summary["n_rows"] == 0
        assert summary["n_columns"] == 0

    def test_no_figures(self):
        """Test with no figures."""
        data = pd.DataFrame({"A": [1, 2, 3]})
        rtf_table = RTFTable()
        metadata = {"table_type": "test"}

        result = TableResult(data=data, rtf_table=rtf_table, metadata=metadata)
        summary = result.get_summary()

        assert summary["has_figures"] is False
        assert summary["n_figures"] == 0

    def test_no_validation_results(self):
        """Test with no validation results."""
        data = pd.DataFrame({"A": [1, 2, 3]})
        rtf_table = RTFTable()
        metadata = {"table_type": "test"}

        result = TableResult(data=data, rtf_table=rtf_table, metadata=metadata)
        summary = result.get_summary()

        assert summary["validation_passed"] is True

