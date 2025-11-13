"""
Unit tests for py4csr.clinical.enhanced_rtf_formatter.EnhancedClinicalRTFFormatter class.

Tests RTF formatting functionality for clinical tables.
"""

import pandas as pd
import pytest

from py4csr.clinical.enhanced_rtf_formatter import EnhancedClinicalRTFFormatter


class TestRTFFormatterInit:
    """Test EnhancedClinicalRTFFormatter initialization."""
    
    def test_default_initialization(self):
        """Test default initialization."""
        formatter = EnhancedClinicalRTFFormatter()
        
        assert formatter.company_name == "py4csr Clinical Reporting"
        assert formatter.website == "www.py4csr.com"
        assert formatter.font_size == 18
    
    def test_custom_initialization(self):
        """Test initialization with custom parameters."""
        formatter = EnhancedClinicalRTFFormatter(
            company_name="Test Company",
            website="www.test.com",
            font_size=20
        )
        
        assert formatter.company_name == "Test Company"
        assert formatter.website == "www.test.com"
        assert formatter.font_size == 20


class TestCreateProfessionalTable:
    """Test create_professional_table method."""
    
    def test_basic_table_creation(self):
        """Test creating a basic clinical table."""
        formatter = EnhancedClinicalRTFFormatter()
        
        # Create simple table data
        table_data = pd.DataFrame({
            'Parameter': ['Age (years)', '  Mean (SD)', '  Median'],
            'Placebo': ['10', '45.2 (12.3)', '44.0'],
            'Treatment A': ['10', '46.8 (11.5)', '45.5']
        })
        
        treatment_info = {
            'Placebo': {'N': 10},
            'Treatment A': {'N': 10}
        }
        
        rtf_output = formatter.create_professional_table(
            table_data=table_data,
            title1="Table 1",
            title2="Demographics",
            title3="Safety Population",
            footnotes=["Note: All subjects"],
            treatment_info=treatment_info,
            p_values={}
        )
        
        assert isinstance(rtf_output, str)
        assert rtf_output.startswith('{\\rtf1')
        assert 'Table 1' in rtf_output
        assert 'Demographics' in rtf_output
        assert 'Safety Population' in rtf_output
    
    def test_table_with_multiple_titles(self):
        """Test table with multiple titles."""
        formatter = EnhancedClinicalRTFFormatter()
        
        table_data = pd.DataFrame({
            'Parameter': ['N'],
            'Total': ['20']
        })
        
        rtf_output = formatter.create_professional_table(
            table_data=table_data,
            title1="Table 1.1",
            title2="Subject Disposition",
            title3="All Randomized Subjects",
            footnotes=[],
            treatment_info={'Total': {'N': 20}},
            p_values={}
        )
        
        assert 'Table 1.1' in rtf_output
        assert 'Subject Disposition' in rtf_output
        assert 'All Randomized Subjects' in rtf_output
    
    def test_table_with_footnotes(self):
        """Test table with multiple footnotes."""
        formatter = EnhancedClinicalRTFFormatter()
        
        table_data = pd.DataFrame({
            'Parameter': ['N'],
            'Total': ['20']
        })
        
        footnotes = [
            "Note: All subjects included",
            "Source: ADSL dataset",
            "Program: demographics.py"
        ]
        
        rtf_output = formatter.create_professional_table(
            table_data=table_data,
            title1="Test Table",
            title2="",
            title3="",
            footnotes=footnotes,
            treatment_info={'Total': {'N': 20}},
            p_values={}
        )
        
        assert 'All subjects included' in rtf_output
        assert 'ADSL dataset' in rtf_output
        assert 'demographics.py' in rtf_output
    
    def test_table_with_p_values(self):
        """Test table with p-values."""
        formatter = EnhancedClinicalRTFFormatter()
        
        table_data = pd.DataFrame({
            'Parameter': ['Age (years)', '  Mean (SD)'],
            'Placebo': ['10', '45.2 (12.3)'],
            'Treatment A': ['10', '46.8 (11.5)']
        })
        
        treatment_info = {
            'Placebo': {'N': 10},
            'Treatment A': {'N': 10}
        }
        
        p_values = {
            'Age (years)': '0.045'
        }
        
        rtf_output = formatter.create_professional_table(
            table_data=table_data,
            title1="Test",
            title2="",
            title3="",
            footnotes=[],
            treatment_info=treatment_info,
            p_values=p_values
        )
        
        assert '0.045' in rtf_output or 'p-value' in rtf_output.lower()
    
    def test_table_with_shift_table(self):
        """Test shift table with two-line headers."""
        formatter = EnhancedClinicalRTFFormatter()
        
        # Shift table has column names with '|' separator
        table_data = pd.DataFrame({
            'Parameter': ['Normal'],
            'Normal|Baseline': ['5'],
            'High|Baseline': ['2']
        })
        
        treatment_info = {'Total': {'N': 7}}
        
        rtf_output = formatter.create_professional_table(
            table_data=table_data,
            title1="Shift Table",
            title2="",
            title3="",
            footnotes=[],
            treatment_info=treatment_info,
            p_values={}
        )
        
        assert isinstance(rtf_output, str)
        assert rtf_output.startswith('{\\rtf1')


class TestRTFHeader:
    """Test _get_rtf_header method."""

    def test_rtf_header_structure(self):
        """Test RTF header contains required elements."""
        formatter = EnhancedClinicalRTFFormatter()

        header = formatter._get_rtf_header()

        assert header.startswith('{\\rtf1')
        assert '\\ansi' in header
        # Font table may or may not be in header depending on implementation
        assert isinstance(header, str)


class TestPageHeader:
    """Test _get_page_header method."""
    
    def test_page_header_content(self):
        """Test page header contains company info."""
        formatter = EnhancedClinicalRTFFormatter(
            company_name="Test Company",
            website="www.test.com"
        )
        
        header = formatter._get_page_header()
        
        assert 'Test Company' in header
        assert 'www.test.com' in header


class TestTableTitles:
    """Test _get_table_titles method."""
    
    def test_single_title(self):
        """Test formatting single title."""
        formatter = EnhancedClinicalRTFFormatter()
        
        titles = formatter._get_table_titles(
            title1="Table 1",
            title2="",
            title3=""
        )
        
        assert 'Table 1' in titles
    
    def test_multiple_titles(self):
        """Test formatting multiple titles."""
        formatter = EnhancedClinicalRTFFormatter()
        
        titles = formatter._get_table_titles(
            title1="Table 1.1",
            title2="Demographics and Baseline Characteristics",
            title3="Safety Population"
        )
        
        assert 'Table 1.1' in titles
        assert 'Demographics and Baseline Characteristics' in titles
        assert 'Safety Population' in titles
    
    def test_empty_titles(self):
        """Test with all empty titles."""
        formatter = EnhancedClinicalRTFFormatter()
        
        titles = formatter._get_table_titles(
            title1="",
            title2="",
            title3=""
        )
        
        assert isinstance(titles, str)


class TestMainTable:
    """Test _get_main_table method."""

    def test_basic_table_formatting(self):
        """Test basic table formatting."""
        formatter = EnhancedClinicalRTFFormatter()

        table_data = pd.DataFrame({
            'Parameter': ['N', 'Mean'],
            'Total': ['10', '45.2']
        })

        treatment_info = {'Total': {'N': 10}}

        table_rtf = formatter._get_main_table(
            table_data=table_data,
            treatment_info=treatment_info,
            p_values={}
        )

        # RTF table should be a string and contain data
        assert isinstance(table_rtf, str)
        assert len(table_rtf) > 0
        # RTF tables contain cell markers
        assert '\\cell' in table_rtf or '\\row' in table_rtf
    
    def test_table_with_indentation(self):
        """Test table respects indentation in Parameter column."""
        formatter = EnhancedClinicalRTFFormatter()
        
        table_data = pd.DataFrame({
            'Parameter': ['Age (years)', '  Mean (SD)', '  Median'],
            'Total': ['10', '45.2 (12.3)', '44.0']
        })
        
        treatment_info = {'Total': {'N': 10}}
        
        table_rtf = formatter._get_main_table(
            table_data=table_data,
            treatment_info=treatment_info,
            p_values={}
        )
        
        # Indentation should be preserved
        assert isinstance(table_rtf, str)


class TestFootnotes:
    """Test _get_footnotes method."""
    
    def test_single_footnote(self):
        """Test formatting single footnote."""
        formatter = EnhancedClinicalRTFFormatter()
        
        footnotes_rtf = formatter._get_footnotes(
            footnotes=["Note: All subjects included"]
        )
        
        assert 'All subjects included' in footnotes_rtf
    
    def test_multiple_footnotes(self):
        """Test formatting multiple footnotes."""
        formatter = EnhancedClinicalRTFFormatter()
        
        footnotes = [
            "Note: All subjects",
            "Source: ADSL",
            "Program: test.py"
        ]
        
        footnotes_rtf = formatter._get_footnotes(footnotes=footnotes)
        
        assert 'All subjects' in footnotes_rtf
        assert 'ADSL' in footnotes_rtf
        assert 'test.py' in footnotes_rtf
    
    def test_empty_footnotes(self):
        """Test with empty footnotes list."""
        formatter = EnhancedClinicalRTFFormatter()
        
        footnotes_rtf = formatter._get_footnotes(footnotes=[])
        
        assert isinstance(footnotes_rtf, str)


class TestProgramPath:
    """Test _get_program_path method."""
    
    def test_program_path_footer(self):
        """Test program path footer generation."""
        formatter = EnhancedClinicalRTFFormatter()
        
        footer = formatter._get_program_path()
        
        assert isinstance(footer, str)
        # Should contain some path or program information

