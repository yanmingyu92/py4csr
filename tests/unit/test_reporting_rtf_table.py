"""
Unit tests for py4csr.reporting.rtf_table module.

Tests RTFTable class and standalone functions.
"""

import pandas as pd
import pytest
from pathlib import Path

from py4csr.reporting.rtf_table import (
    RTFTable,
    rtf_page_header,
    rtf_page_footer,
    rtf_title,
    rtf_subline,
    rtf_colheader,
    rtf_body,
    rtf_footnote,
    rtf_source,
    rtf_page,
    rtf_encode,
    write_rtf,
)


class TestRTFTableInit:
    """Test RTFTable initialization."""

    def test_basic_initialization(self):
        """Test basic RTFTable initialization."""
        rtf = RTFTable()

        assert rtf.page_header == ""
        assert rtf.page_footer == ""
        assert rtf.title == ""
        assert rtf.subtitle == ""
        assert rtf.colheader == []
        assert rtf.body == []
        assert rtf.footnote == []
        assert rtf.source == ""
        assert rtf.embedded_images == []
        assert rtf.page_settings["orientation"] == "landscape"


class TestRTFTableMethods:
    """Test RTFTable methods."""

    def test_rtf_page_header(self):
        """Test adding page header."""
        rtf = RTFTable().rtf_page_header("Study ABC-001")

        assert rtf.page_header == "Study ABC-001"

    def test_rtf_page_footer(self):
        """Test adding page footer."""
        rtf = RTFTable().rtf_page_footer("Page {PAGE}")

        assert rtf.page_footer == "Page {PAGE}"

    def test_rtf_title(self):
        """Test adding title."""
        rtf = RTFTable().rtf_title("Demographics Table")

        assert rtf.title == "Demographics Table"
        assert rtf.subtitle == ""

    def test_rtf_title_with_subtitle(self):
        """Test adding title with subtitle."""
        rtf = RTFTable().rtf_title("Demographics Table", "Safety Population")

        assert rtf.title == "Demographics Table"
        assert rtf.subtitle == "Safety Population"

    def test_rtf_subline(self):
        """Test adding subtitle."""
        rtf = RTFTable().rtf_subline("Safety Population")

        assert rtf.subtitle == "Safety Population"

    def test_rtf_colheader(self):
        """Test adding column headers."""
        headers = ["Variable", "Treatment A", "Treatment B"]
        rtf = RTFTable().rtf_colheader(headers)

        assert rtf.colheader == headers

    def test_rtf_body_dataframe(self):
        """Test adding body from DataFrame."""
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        rtf = RTFTable().rtf_body(df)

        assert len(rtf.body) == 3
        assert rtf.body[0] == [1, 4]

    def test_rtf_body_list(self):
        """Test adding body from list."""
        data = [["Row1", "Value1"], ["Row2", "Value2"]]
        rtf = RTFTable().rtf_body(data)

        assert rtf.body == data

    def test_rtf_footnote_string(self):
        """Test adding single footnote."""
        rtf = RTFTable().rtf_footnote("Note: This is a footnote")

        assert len(rtf.footnote) == 1
        assert rtf.footnote[0] == "Note: This is a footnote"

    def test_rtf_footnote_list(self):
        """Test adding multiple footnotes."""
        footnotes = ["Footnote 1", "Footnote 2"]
        rtf = RTFTable().rtf_footnote(footnotes)

        assert rtf.footnote == footnotes

    def test_rtf_source(self):
        """Test adding source."""
        rtf = RTFTable().rtf_source("Source: Clinical Database")

        assert rtf.source == "Source: Clinical Database"

    def test_rtf_page(self):
        """Test setting page settings."""
        rtf = RTFTable().rtf_page(orientation="portrait", font_size=12)

        assert rtf.page_settings["orientation"] == "portrait"
        assert rtf.page_settings["font_size"] == 12


class TestRTFTableMethodChaining:
    """Test method chaining."""

    def test_method_chaining(self):
        """Test chaining multiple methods."""
        rtf = (
            RTFTable()
            .rtf_title("Test Table", "Test Subtitle")
            .rtf_colheader(["Col1", "Col2"])
            .rtf_body([["A", "B"], ["C", "D"]])
            .rtf_footnote("Test footnote")
        )

        assert rtf.title == "Test Table"
        assert rtf.subtitle == "Test Subtitle"
        assert len(rtf.colheader) == 2
        assert len(rtf.body) == 2
        assert len(rtf.footnote) == 1


class TestRTFTableEncode:
    """Test RTF encoding."""

    def test_rtf_encode_basic(self):
        """Test basic RTF encoding."""
        rtf = RTFTable().rtf_title("Test Title")
        encoded = rtf.rtf_encode()

        assert encoded.startswith("{\\rtf1")
        assert "Test Title" in encoded
        assert encoded.endswith("}")

    def test_rtf_encode_with_table(self):
        """Test RTF encoding with table."""
        rtf = (
            RTFTable()
            .rtf_colheader(["Col1", "Col2"])
            .rtf_body([["A", "B"], ["C", "D"]])
        )
        encoded = rtf.rtf_encode()

        assert "{\\rtf1" in encoded
        assert "Col1" in encoded
        assert "Col2" in encoded

    def test_rtf_encode_with_footnotes(self):
        """Test RTF encoding with footnotes."""
        rtf = RTFTable().rtf_footnote(["Footnote 1", "Footnote 2"])
        encoded = rtf.rtf_encode()

        assert "Footnote 1" in encoded
        assert "Footnote 2" in encoded

    def test_rtf_encode_special_characters(self):
        """Test RTF encoding with special characters."""
        rtf = RTFTable().rtf_title("Test {Title} with \\backslash")
        encoded = rtf.rtf_encode()

        # Special characters should be escaped
        assert "\\{" in encoded or "\\}" in encoded or "\\\\" in encoded


class TestRTFTableWrite:
    """Test writing RTF to file."""

    def test_write_rtf(self, temp_output_dir):
        """Test writing RTF to file."""
        rtf = RTFTable().rtf_title("Test Table")
        output_file = temp_output_dir / "test.rtf"

        rtf.write_rtf(output_file)

        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert "{\\rtf1" in content
        assert "Test Table" in content

    def test_write_rtf_creates_directory(self, temp_output_dir):
        """Test that write_rtf creates parent directories."""
        rtf = RTFTable().rtf_title("Test Table")
        output_file = temp_output_dir / "subdir" / "test.rtf"

        rtf.write_rtf(output_file)

        assert output_file.exists()


class TestStandaloneFunctions:
    """Test standalone functions."""

    def test_rtf_page_header_function(self):
        """Test rtf_page_header standalone function."""
        rtf = rtf_page_header("Test Header")

        assert isinstance(rtf, RTFTable)
        assert rtf.page_header == "Test Header"

    def test_rtf_page_footer_function(self):
        """Test rtf_page_footer standalone function."""
        rtf = rtf_page_footer("Test Footer")

        assert isinstance(rtf, RTFTable)
        assert rtf.page_footer == "Test Footer"

    def test_rtf_title_function(self):
        """Test rtf_title standalone function."""
        rtf = rtf_title("Test Title", "Test Subtitle")

        assert isinstance(rtf, RTFTable)
        assert rtf.title == "Test Title"
        assert rtf.subtitle == "Test Subtitle"

    def test_rtf_subline_function(self):
        """Test rtf_subline standalone function."""
        rtf = rtf_subline("Test Subline")

        assert isinstance(rtf, RTFTable)
        assert rtf.subtitle == "Test Subline"

    def test_rtf_colheader_function(self):
        """Test rtf_colheader standalone function."""
        rtf = rtf_colheader(["Col1", "Col2"])

        assert isinstance(rtf, RTFTable)
        assert rtf.colheader == ["Col1", "Col2"]

    def test_rtf_body_function(self):
        """Test rtf_body standalone function."""
        data = [["A", "B"], ["C", "D"]]
        rtf = rtf_body(data)

        assert isinstance(rtf, RTFTable)
        assert rtf.body == data

    def test_rtf_footnote_function(self):
        """Test rtf_footnote standalone function."""
        rtf = rtf_footnote("Test Footnote")

        assert isinstance(rtf, RTFTable)
        assert rtf.footnote == ["Test Footnote"]

    def test_rtf_source_function(self):
        """Test rtf_source standalone function."""
        rtf = rtf_source("Test Source")

        assert isinstance(rtf, RTFTable)
        assert rtf.source == "Test Source"

    def test_rtf_page_function(self):
        """Test rtf_page standalone function."""
        rtf = rtf_page(orientation="portrait")

        assert isinstance(rtf, RTFTable)
        assert rtf.page_settings["orientation"] == "portrait"

    def test_rtf_encode_function(self):
        """Test rtf_encode standalone function."""
        rtf = RTFTable().rtf_title("Test")
        encoded = rtf_encode(rtf)

        assert isinstance(encoded, str)
        assert "{\\rtf1" in encoded

    def test_write_rtf_function(self, temp_output_dir):
        """Test write_rtf standalone function."""
        rtf = RTFTable().rtf_title("Test")
        output_file = temp_output_dir / "test.rtf"

        write_rtf(rtf, output_file)

        assert output_file.exists()


class TestRTFTableEdgeCases:
    """Test edge cases."""

    def test_empty_table(self):
        """Test encoding empty table."""
        rtf = RTFTable()
        encoded = rtf.rtf_encode()

        assert "{\\rtf1" in encoded
        assert encoded.endswith("}")

    def test_unicode_characters(self):
        """Test handling unicode characters."""
        rtf = RTFTable().rtf_title("Test with émojis 😀")
        encoded = rtf.rtf_encode()

        # Should not raise error
        assert "{\\rtf1" in encoded

    def test_newline_in_text(self):
        """Test handling newlines."""
        rtf = RTFTable().rtf_title("Line 1\nLine 2")
        encoded = rtf.rtf_encode()

        # Newlines should be converted to RTF format
        assert "\\par" in encoded or "\\line" in encoded

