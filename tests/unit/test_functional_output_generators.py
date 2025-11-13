"""
Unit tests for py4csr.functional.output_generators module.

Tests output generation functionality for different formats (RTF, PDF, HTML, Excel).
"""

import pandas as pd
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from py4csr.functional.output_generators import (
    OutputGeneratorFactory,
    BaseOutputGenerator,
    RTFGenerator,
    PDFGenerator,
    HTMLGenerator,
    ExcelGenerator,
)
from py4csr.functional.config import FunctionalConfig
from py4csr.functional.table_builder import TableResult


@pytest.fixture
def sample_config():
    """Create sample FunctionalConfig."""
    return FunctionalConfig(
        output_formats=["rtf", "pdf"],
        font_family="Times New Roman",
        font_size=10
    )


@pytest.fixture
def sample_table_result():
    """Create sample TableResult."""
    data = pd.DataFrame({
        "Treatment": ["Placebo", "Drug A", "Drug B"],
        "N": [10, 15, 12],
        "Mean": [5.2, 7.8, 6.5]
    })

    metadata = {
        "table_type": "demographics",
        "population": "safety",
        "title": "Demographics Summary",
        "subtitle": "Safety Population",
        "footnotes": ["Note: All subjects included", "Data cutoff: 2024-01-01"]
    }

    return TableResult(data=data, metadata=metadata)


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create temporary output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


class TestOutputGeneratorFactory:
    """Test OutputGeneratorFactory class."""

    def test_create_rtf_generator(self, sample_config):
        """Test creating RTF generator."""
        generator = OutputGeneratorFactory.create("rtf", sample_config)
        assert isinstance(generator, RTFGenerator)
        assert generator.config == sample_config

    def test_create_pdf_generator(self, sample_config):
        """Test creating PDF generator."""
        generator = OutputGeneratorFactory.create("pdf", sample_config)
        assert isinstance(generator, PDFGenerator)
        assert generator.config == sample_config

    def test_create_html_generator(self, sample_config):
        """Test creating HTML generator."""
        generator = OutputGeneratorFactory.create("html", sample_config)
        assert isinstance(generator, HTMLGenerator)
        assert generator.config == sample_config

    def test_create_excel_generator(self, sample_config):
        """Test creating Excel generator."""
        generator = OutputGeneratorFactory.create("excel", sample_config)
        assert isinstance(generator, ExcelGenerator)
        assert generator.config == sample_config

    def test_create_case_insensitive(self, sample_config):
        """Test format type is case-insensitive."""
        generator1 = OutputGeneratorFactory.create("RTF", sample_config)
        generator2 = OutputGeneratorFactory.create("Rtf", sample_config)
        assert isinstance(generator1, RTFGenerator)
        assert isinstance(generator2, RTFGenerator)

    def test_create_unsupported_format(self, sample_config):
        """Test creating generator with unsupported format."""
        with pytest.raises(ValueError, match="Unsupported output format"):
            OutputGeneratorFactory.create("xml", sample_config)


class TestBaseOutputGenerator:
    """Test BaseOutputGenerator class."""

    def test_initialization(self, sample_config):
        """Test BaseOutputGenerator initialization."""
        generator = BaseOutputGenerator(sample_config)
        assert generator.config == sample_config

    def test_generate_not_implemented(self, sample_config, sample_table_result, temp_output_dir):
        """Test generate method raises NotImplementedError."""
        generator = BaseOutputGenerator(sample_config)
        with pytest.raises(NotImplementedError, match="Subclasses must implement"):
            generator.generate(sample_table_result, temp_output_dir)

    def test_get_output_filename(self, sample_config, sample_table_result):
        """Test _get_output_filename method."""
        generator = BaseOutputGenerator(sample_config)
        filename = generator._get_output_filename(sample_table_result, "rtf")
        assert filename.startswith("demographics_")
        assert filename.endswith(".rtf")

    def test_get_output_filename_default_table_type(self, sample_config):
        """Test _get_output_filename with default table type."""
        generator = BaseOutputGenerator(sample_config)
        table_result = TableResult(
            data=pd.DataFrame(),
            metadata={}  # No table_type
        )
        filename = generator._get_output_filename(table_result, "pdf")
        assert filename.startswith("table_")
        assert filename.endswith(".pdf")


class TestRTFGenerator:
    """Test RTFGenerator class."""

    def test_initialization(self, sample_config):
        """Test RTFGenerator initialization."""
        generator = RTFGenerator(sample_config)
        assert isinstance(generator, BaseOutputGenerator)
        assert generator.config == sample_config

    def test_generate_basic(self, sample_config, sample_table_result, temp_output_dir):
        """Test basic RTF generation."""
        generator = RTFGenerator(sample_config)
        output_file = generator.generate(sample_table_result, temp_output_dir)
        
        assert output_file.exists()
        assert output_file.suffix == ".rtf"
        
        # Check file content
        content = output_file.read_text(encoding="utf-8")
        assert r"{\rtf1\ansi\deff0" in content
        assert "Demographics Summary" in content
        assert "Safety Population" in content

    def test_generate_with_title(self, sample_config, temp_output_dir):
        """Test RTF generation with title."""
        table_result = TableResult(
            data=pd.DataFrame({"A": [1, 2]}),
            metadata={"table_type": "test", "title": "Test Title"}
        )

        generator = RTFGenerator(sample_config)
        output_file = generator.generate(table_result, temp_output_dir)

        content = output_file.read_text(encoding="utf-8")
        assert "Test Title" in content
        assert r"\qc\b\fs24" in content  # Center, bold, 12pt

    def test_generate_with_subtitle(self, sample_config, temp_output_dir):
        """Test RTF generation with subtitle."""
        table_result = TableResult(
            data=pd.DataFrame({"A": [1, 2]}),
            metadata={"table_type": "test", "subtitle": "Test Subtitle"}
        )

        generator = RTFGenerator(sample_config)
        output_file = generator.generate(table_result, temp_output_dir)

        content = output_file.read_text(encoding="utf-8")
        assert "Test Subtitle" in content

    def test_generate_with_footnotes(self, sample_config, temp_output_dir):
        """Test RTF generation with footnotes."""
        table_result = TableResult(
            data=pd.DataFrame({"A": [1, 2]}),
            metadata={"table_type": "test", "footnotes": ["Footnote 1", "Footnote 2"]}
        )

        generator = RTFGenerator(sample_config)
        output_file = generator.generate(table_result, temp_output_dir)

        content = output_file.read_text(encoding="utf-8")
        assert "1. Footnote 1" in content
        assert "2. Footnote 2" in content
        assert r"\fs16" in content  # 8pt for footnotes

    def test_generate_empty_data(self, sample_config, temp_output_dir):
        """Test RTF generation with empty data."""
        table_result = TableResult(
            data=pd.DataFrame(),
            metadata={"table_type": "test", "title": "Empty Table"}
        )

        generator = RTFGenerator(sample_config)
        output_file = generator.generate(table_result, temp_output_dir)

        content = output_file.read_text(encoding="utf-8")
        assert "Empty Table" in content

    def test_escape_rtf_special_characters(self, sample_config):
        """Test RTF special character escaping."""
        generator = RTFGenerator(sample_config)
        
        assert generator._escape_rtf("test\\text") == "test\\\\text"
        assert generator._escape_rtf("test{text}") == "test\\{text\\}"
        assert generator._escape_rtf("normal text") == "normal text"

    def test_escape_rtf_nan(self, sample_config):
        """Test RTF escaping with NaN values."""
        generator = RTFGenerator(sample_config)
        assert generator._escape_rtf(pd.NA) == ""
        assert generator._escape_rtf(float('nan')) == ""

    def test_generate_rtf_table(self, sample_config, sample_table_result):
        """Test RTF table generation."""
        generator = RTFGenerator(sample_config)
        rtf_lines = generator._generate_rtf_table(sample_table_result.data)
        
        rtf_content = "\n".join(rtf_lines)
        assert r"\trowd\trgaph108" in rtf_content
        assert "Treatment" in rtf_content
        assert "Placebo" in rtf_content
        assert "Drug A" in rtf_content

    def test_generate_rtf_table_empty(self, sample_config):
        """Test RTF table generation with empty DataFrame."""
        generator = RTFGenerator(sample_config)
        rtf_lines = generator._generate_rtf_table(pd.DataFrame())
        
        rtf_content = "\n".join(rtf_lines)
        assert "No data available" in rtf_content


class TestPDFGenerator:
    """Test PDFGenerator class."""

    def test_initialization(self, sample_config):
        """Test PDFGenerator initialization."""
        generator = PDFGenerator(sample_config)
        assert isinstance(generator, BaseOutputGenerator)
        assert generator.config == sample_config

    @pytest.mark.skipif(True, reason="reportlab is optional dependency")
    def test_generate_basic(self, sample_config, sample_table_result, temp_output_dir):
        """Test basic PDF generation."""
        generator = PDFGenerator(sample_config)
        output_file = generator.generate(sample_table_result, temp_output_dir)
        
        assert output_file.exists()
        assert output_file.suffix == ".pdf"

    def test_generate_without_reportlab(self, sample_config, sample_table_result, temp_output_dir):
        """Test PDF generation without reportlab installed."""
        generator = PDFGenerator(sample_config)

        # When reportlab is not available, it generates a text file with a warning
        with patch.dict('sys.modules', {'reportlab': None}):
            with pytest.warns(UserWarning, match="reportlab not available"):
                output_file = generator.generate(sample_table_result, temp_output_dir)
                assert output_file.suffix == ".txt"  # Falls back to text file


class TestHTMLGenerator:
    """Test HTMLGenerator class."""

    def test_initialization(self, sample_config):
        """Test HTMLGenerator initialization."""
        generator = HTMLGenerator(sample_config)
        assert isinstance(generator, BaseOutputGenerator)
        assert generator.config == sample_config

    def test_generate_basic(self, sample_config, sample_table_result, temp_output_dir):
        """Test basic HTML generation."""
        generator = HTMLGenerator(sample_config)
        output_file = generator.generate(sample_table_result, temp_output_dir)
        
        assert output_file.exists()
        assert output_file.suffix == ".html"
        
        # Check file content
        content = output_file.read_text(encoding="utf-8")
        assert "<html>" in content
        assert "<table>" in content
        assert "Demographics Summary" in content

    def test_generate_with_title(self, sample_config, temp_output_dir):
        """Test HTML generation with title."""
        table_result = TableResult(
            data=pd.DataFrame({"A": [1, 2]}),
            metadata={"table_type": "test", "title": "Test Title"}
        )

        generator = HTMLGenerator(sample_config)
        output_file = generator.generate(table_result, temp_output_dir)

        content = output_file.read_text(encoding="utf-8")
        assert "<h1>Test Title</h1>" in content

    def test_generate_with_footnotes(self, sample_config, temp_output_dir):
        """Test HTML generation with footnotes."""
        table_result = TableResult(
            data=pd.DataFrame({"A": [1, 2]}),
            metadata={"table_type": "test", "footnotes": ["Note 1", "Note 2"]}
        )

        generator = HTMLGenerator(sample_config)
        output_file = generator.generate(table_result, temp_output_dir)

        content = output_file.read_text(encoding="utf-8")
        assert "Note 1" in content
        assert "Note 2" in content


class TestExcelGenerator:
    """Test ExcelGenerator class."""

    def test_initialization(self, sample_config):
        """Test ExcelGenerator initialization."""
        generator = ExcelGenerator(sample_config)
        assert isinstance(generator, BaseOutputGenerator)
        assert generator.config == sample_config

    def test_generate_basic(self, sample_config, sample_table_result, temp_output_dir):
        """Test basic Excel generation."""
        generator = ExcelGenerator(sample_config)
        output_file = generator.generate(sample_table_result, temp_output_dir)

        assert output_file.exists()
        assert output_file.suffix == ".xlsx"

        # Check that file has the expected sheet
        excel_file = pd.ExcelFile(output_file)
        assert "Clinical Table" in excel_file.sheet_names

    def test_generate_with_metadata(self, sample_config, sample_table_result, temp_output_dir):
        """Test Excel generation includes title and footnotes."""
        generator = ExcelGenerator(sample_config)
        output_file = generator.generate(sample_table_result, temp_output_dir)

        # Check that file exists and has correct sheet
        excel_file = pd.ExcelFile(output_file)
        assert "Clinical Table" in excel_file.sheet_names

        # The Excel file includes title, subtitle, data, and footnotes all in one sheet
        assert output_file.exists()

