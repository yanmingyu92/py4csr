"""
Unit tests for py4csr.clinical.session.ClinicalSession class.

Tests the main clinical reporting session functionality.
"""

import pandas as pd
import pytest
from unittest.mock import Mock, patch
import warnings

from py4csr.clinical.session import ClinicalSession
from py4csr.exceptions import DataValidationError, SessionError


class TestClinicalSessionInit:
    """Test ClinicalSession initialization."""
    
    def test_basic_initialization(self):
        """Test basic session initialization."""
        session = ClinicalSession(uri="test_table")
        
        assert session.uri == "test_table"
        assert session.purpose == "Clinical table generation for test_table"
        assert session.outname == "test_table"
        assert session.dataset is None
        assert len(session.variables) == 0
        assert session.generated_data is None
    
    def test_initialization_with_all_params(self):
        """Test initialization with all parameters."""
        session = ClinicalSession(
            uri="demographics",
            purpose="Demographics Table",
            outname="t_demographics"
        )
        
        assert session.uri == "demographics"
        assert session.purpose == "Demographics Table"
        assert session.outname == "t_demographics"
    
    def test_stats_engine_initialized(self):
        """Test that statistical engine is initialized."""
        session = ClinicalSession(uri="test")
        
        assert session.stats_engine is not None
        assert hasattr(session.stats_engine, 'calculate_continuous_stats')
        assert hasattr(session.stats_engine, 'calculate_categorical_stats')


class TestDefineReport:
    """Test define_report method."""
    
    def test_define_report_with_dataframe(self, sample_adsl):
        """Test defining report with DataFrame."""
        session = ClinicalSession(uri="test")

        session.define_report(
            dataset=sample_adsl,
            pop_where="SAFFL=='Y'",
            subjid="USUBJID",
            title1="Test Table",
            title2="Safety Population"
        )

        assert session.dataset is not None
        assert len(session.dataset) == 10
        assert session.report_config['subjid'] == "USUBJID"
        assert session.report_config['titles'][0] == "Test Table"
        assert session.report_config['titles'][1] == "Safety Population"
    
    def test_define_report_with_where_clause(self, sample_adsl):
        """Test defining report with population filter."""
        session = ClinicalSession(uri="test")
        
        # Add a flag to filter on
        sample_adsl['EFFFL'] = ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'N', 'Y']
        
        session.define_report(
            dataset=sample_adsl,
            pop_where="EFFFL=='Y'",
            subjid="USUBJID"
        )
        
        # Dataset should be stored (filtering happens during generation)
        assert session.dataset is not None
        assert session.report_config['pop_where'] == "EFFFL=='Y'"
    
    def test_define_report_with_multiple_titles(self, sample_adsl):
        """Test defining report with multiple titles."""
        session = ClinicalSession(uri="test")

        session.define_report(
            dataset=sample_adsl,
            title1="Table 1",
            title2="Demographics and Baseline Characteristics",
            title3="Safety Population",
            footnot1="Note: All subjects",
            footnot2="Source: ADSL"
        )

        assert session.report_config['titles'][0] == "Table 1"
        assert session.report_config['titles'][1] == "Demographics and Baseline Characteristics"
        assert session.report_config['titles'][2] == "Safety Population"
        assert session.report_config['footnotes'][0] == "Note: All subjects"
        assert session.report_config['footnotes'][1] == "Source: ADSL"


class TestAddTrt:
    """Test add_trt method for adding treatment variables."""
    
    def test_add_trt_basic(self, sample_adsl):
        """Test adding treatment variable."""
        session = ClinicalSession(uri="test")
        session.define_report(dataset=sample_adsl, subjid="USUBJID")
        
        result = session.add_trt(name="TRT01PN", decode="TRT01P")
        
        assert result is session  # Method chaining
        assert session.treatments['name'] == "TRT01PN"
        assert session.treatments['decode'] == "TRT01P"
    
    def test_add_trt_with_autospan(self, sample_adsl):
        """Test adding treatment with autospan."""
        session = ClinicalSession(uri="test")
        session.define_report(dataset=sample_adsl, subjid="USUBJID")
        
        session.add_trt(name="TRT01PN", decode="TRT01P", autospan="Y")
        
        assert session.treatments['autospan'] == "Y"


class TestAddVar:
    """Test add_var method for continuous variables."""
    
    def test_add_var_basic(self, sample_adsl):
        """Test adding continuous variable."""
        session = ClinicalSession(uri="test")
        session.define_report(dataset=sample_adsl, subjid="USUBJID")
        
        result = session.add_var(name="AGE", label="Age (years)")
        
        assert result is session  # Method chaining
        assert len(session.variables) == 1
        assert session.variables[0]['name'] == "AGE"
        assert session.variables[0]['label'] == "Age (years)"
        assert session.variables[0]['type'] == 'continuous'
    
    def test_add_var_with_stats(self, sample_adsl):
        """Test adding variable with custom statistics."""
        session = ClinicalSession(uri="test")
        session.define_report(dataset=sample_adsl, subjid="USUBJID")
        
        session.add_var(
            name="AGE",
            label="Age (years)",
            stats="n mean+sd median min+max"
        )
        
        assert session.variables[0]['stats'] == "n mean+sd median min+max"
    
    def test_add_var_with_indent(self, sample_adsl):
        """Test adding variable with indentation."""
        session = ClinicalSession(uri="test")
        session.define_report(dataset=sample_adsl, subjid="USUBJID")
        
        session.add_var(name="AGE", label="Age (years)", indent=2)
        
        assert session.variables[0]['indent'] == 2
    
    def test_add_var_missing_column_warning(self, sample_adsl):
        """Test warning when variable not in dataset."""
        session = ClinicalSession(uri="test")
        session.define_report(dataset=sample_adsl, subjid="USUBJID")
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            session.add_var(name="NONEXISTENT", label="Missing Variable")
            
            assert len(w) == 1
            assert "not found in dataset" in str(w[0].message)


class TestAddCatvar:
    """Test add_catvar method for categorical variables."""
    
    def test_add_catvar_basic(self, sample_adsl):
        """Test adding categorical variable."""
        session = ClinicalSession(uri="test")
        session.define_report(dataset=sample_adsl, subjid="USUBJID")
        
        result = session.add_catvar(
            name="SEX",
            label="Sex, n (%)",
            stats="npct"
        )
        
        assert result is session  # Method chaining
        assert len(session.variables) == 1
        assert session.variables[0]['name'] == "SEX"
        assert session.variables[0]['label'] == "Sex, n (%)"
        assert session.variables[0]['type'] == 'categorical'
        assert session.variables[0]['stats'] == "npct"
    
    def test_add_catvar_with_decode(self, sample_adsl):
        """Test adding categorical variable with decode."""
        session = ClinicalSession(uri="test")
        session.define_report(dataset=sample_adsl, subjid="USUBJID")
        
        session.add_catvar(
            name="SEXN",
            label="Sex, n (%)",
            decode="SEX",
            stats="npct"
        )
        
        assert session.variables[0]['decode'] == "SEX"
    
    def test_add_catvar_with_codelist(self, sample_adsl):
        """Test adding categorical variable with codelist."""
        session = ClinicalSession(uri="test")
        session.define_report(dataset=sample_adsl, subjid="USUBJID")
        
        session.add_catvar(
            name="SEX",
            label="Sex, n (%)",
            codelist="M='Male',F='Female'"
        )
        
        assert session.variables[0]['codelist'] == "M='Male',F='Female'"


class TestAddCond:
    """Test add_cond method for condition-based rows."""

    def test_add_cond_basic(self, sample_adsl):
        """Test adding condition-based row."""
        session = ClinicalSession(uri="test")
        session.define_report(dataset=sample_adsl, subjid="USUBJID")

        result = session.add_cond(
            label="Subjects with Age >= 65",
            where="AGE >= 65",
            stats="n"
        )

        assert result is session  # Method chaining
        assert len(session.variables) == 1
        assert session.variables[0]['type'] == 'condition'
        assert session.variables[0]['label'] == "Subjects with Age >= 65"
        assert session.variables[0]['where'] == "AGE >= 65"


class TestMakeTrt:
    """Test make_trt method for pooling treatment groups."""

    def test_make_trt_basic(self, sample_adsl):
        """Test creating pooled treatment group."""
        session = ClinicalSession(uri="test")
        session.define_report(dataset=sample_adsl, subjid="USUBJID")
        session.add_trt(name="TRT01PN", decode="TRT01P")

        result = session.make_trt(
            name="TRT01PN",
            newvalue=99,
            newdecode="Total",
            values="1,2,3"
        )

        assert result is session  # Method chaining
        assert "pooled" in session.treatments
        assert len(session.treatments["pooled"]) == 1
        assert session.treatments["pooled"][0]["newdecode"] == "Total"
        assert session.treatments["pooled"][0]["newvalue"] == 99


class TestAddGroup:
    """Test add_group method for hierarchical grouping."""

    def test_add_group_basic(self, sample_adsl):
        """Test adding grouping variable."""
        session = ClinicalSession(uri="test")
        session.define_report(dataset=sample_adsl, subjid="USUBJID")

        result = session.add_group(name="AGEGR1", decode="AGEGR1")

        assert result is session  # Method chaining
        assert len(session.groups) > 0


class TestAddLabel:
    """Test add_label method for adding label rows."""

    def test_add_label_basic(self, sample_adsl):
        """Test adding label row."""
        session = ClinicalSession(uri="test")
        session.define_report(dataset=sample_adsl, subjid="USUBJID")

        result = session.add_label(label="Demographics")

        assert result is session  # Method chaining
        assert len(session.variables) == 1
        assert session.variables[0]['type'] == 'label'
        assert session.variables[0]['label'] == "Demographics"


class TestGenerate:
    """Test generate method for table generation."""

    def test_generate_requires_dataset(self):
        """Test that generate requires dataset."""
        session = ClinicalSession(uri="test")

        with pytest.raises(ValueError, match="No dataset defined"):
            session.generate()

    def test_generate_requires_variables(self, sample_adsl):
        """Test that generate requires variables."""
        session = ClinicalSession(uri="test")
        session.define_report(dataset=sample_adsl, subjid="USUBJID")

        with pytest.raises(ValueError, match="No variables added"):
            session.generate()

    def test_generate_requires_treatment(self, sample_adsl):
        """Test that generate requires treatment variable."""
        session = ClinicalSession(uri="test")
        session.define_report(dataset=sample_adsl, subjid="USUBJID")
        session.add_var(name="AGE", label="Age (years)")

        with pytest.raises(ValueError, match="No treatment variable defined"):
            session.generate()


class TestFinalize:
    """Test finalize method for saving output."""

    def test_finalize_requires_generated_table(self):
        """Test that finalize requires generated table."""
        session = ClinicalSession(uri="test")

        with pytest.raises(ValueError, match="No table generated"):
            session.finalize("output.rtf")

    def test_finalize_rtf_format(self, sample_adsl, tmp_path):
        """Test finalize with RTF format."""
        session = ClinicalSession(uri="test")
        session.define_report(dataset=sample_adsl, subjid="USUBJID")

        # Mock generated table
        session.generated_table = pd.DataFrame({
            "Variable": ["Age (years)"],
            "Placebo": ["45.2 (12.3)"],
            "Drug A": ["46.1 (11.8)"]
        })
        session.treatment_info = {
            1: {"decode": "Placebo", "n": 10},
            2: {"decode": "Drug A", "n": 15}
        }

        output_file = tmp_path / "test.rtf"
        session.finalize(str(output_file), output_format="rtf")

        assert output_file.exists()

    def test_finalize_csv_format(self, sample_adsl, tmp_path):
        """Test finalize with CSV format."""
        session = ClinicalSession(uri="test")
        session.define_report(dataset=sample_adsl, subjid="USUBJID")

        # Mock generated table
        session.generated_table = pd.DataFrame({
            "Variable": ["Age (years)"],
            "Placebo": ["45.2 (12.3)"]
        })
        session.treatment_info = {1: {"decode": "Placebo", "n": 10}}

        output_file = tmp_path / "test.csv"
        session.finalize(str(output_file), output_format="csv")

        assert output_file.exists()


class TestToCsv:
    """Test to_csv method."""

    def test_to_csv_requires_generated_table(self, tmp_path):
        """Test that to_csv requires generated table."""
        session = ClinicalSession(uri="test")
        output_file = tmp_path / "test.csv"

        with pytest.raises(ValueError, match="No table generated"):
            session.to_csv(str(output_file))

    def test_to_csv_basic(self, tmp_path):
        """Test basic CSV export."""
        session = ClinicalSession(uri="test")
        session.generated_table = pd.DataFrame({
            "Variable": ["Age"],
            "Value": ["45.2"]
        })

        output_file = tmp_path / "test.csv"
        session.to_csv(str(output_file))

        assert output_file.exists()
        loaded = pd.read_csv(output_file)
        assert len(loaded) == 1


class TestPreview:
    """Test preview method."""

    def test_preview_without_generated_table(self, capsys):
        """Test preview without generated table returns empty DataFrame."""
        session = ClinicalSession(uri="test")

        result = session.preview()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        captured = capsys.readouterr()
        assert "No table generated" in captured.out

    def test_preview_basic(self):
        """Test basic preview."""
        session = ClinicalSession(uri="test")
        session.generated_table = pd.DataFrame({
            "Variable": ["Age", "Sex"],
            "Value": ["45.2", "M: 10 (50%)"]
        })

        result = session.preview()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

    def test_preview_with_max_rows(self):
        """Test preview with max_rows limit."""
        session = ClinicalSession(uri="test")
        session.generated_table = pd.DataFrame({
            "Variable": [f"Var{i}" for i in range(50)],
            "Value": [f"Val{i}" for i in range(50)]
        })

        result = session.preview(max_rows=10)

        assert len(result) <= 10


class TestSummary:
    """Test summary method."""

    def test_summary_empty_session(self, capsys):
        """Test summary of empty session."""
        session = ClinicalSession(uri="test_table", purpose="Test Purpose")

        session.summary()

        captured = capsys.readouterr()
        assert "test_table" in captured.out
        assert "Test Purpose" in captured.out
        assert "0 subjects" in captured.out
        assert "0 added" in captured.out

    def test_summary_with_data(self, sample_adsl, capsys):
        """Test summary with data and variables."""
        session = ClinicalSession(uri="demographics")
        session.define_report(dataset=sample_adsl, subjid="USUBJID")
        session.add_trt(name="TRT01PN", decode="TRT01P")
        session.add_var(name="AGE", label="Age (years)")
        session.add_catvar(name="SEX", label="Sex, n (%)")

        session.summary()

        captured = capsys.readouterr()
        assert "demographics" in captured.out
        assert "10 subjects" in captured.out
        assert "2 added" in captured.out


class TestHelperMethods:
    """Test helper methods."""

    def test_parse_codelist_basic(self):
        """Test parsing basic codelist."""
        session = ClinicalSession(uri="test")

        result = session._parse_codelist("M='Male',F='Female'")

        assert isinstance(result, dict)
        assert result["M"] == "Male"
        assert result["F"] == "Female"

    def test_parse_codelist_with_spaces(self):
        """Test parsing codelist with spaces."""
        session = ClinicalSession(uri="test")

        result = session._parse_codelist("1='Placebo',2='Drug A'")

        # Keys are converted to int
        assert result[1] == "Placebo"
        assert result[2] == "Drug A"

    def test_parse_codelist_with_numbers(self):
        """Test parsing codelist with numeric keys."""
        session = ClinicalSession(uri="test")

        result = session._parse_codelist("1='Low',2='Medium',3='High'")

        # Keys are converted to int
        assert result[1] == "Low"
        assert result[2] == "Medium"
        assert result[3] == "High"

    def test_collect_treatment_info(self, sample_adsl):
        """Test collecting treatment information."""
        session = ClinicalSession(uri="test")
        session.define_report(dataset=sample_adsl, subjid="USUBJID")

        session._collect_treatment_info(sample_adsl, "TRT01PN", "TRT01P")

        assert len(session.treatment_info) > 0
        # Check that treatment info has expected structure
        for trt_num, info in session.treatment_info.items():
            assert "name" in info or "decode" in info
            assert "n" in info

    def test_prepare_table_for_rtf_no_table(self):
        """Test preparing table for RTF when no table generated."""
        session = ClinicalSession(uri="test")

        result = session._prepare_table_for_rtf()

        # Returns empty DataFrame when no table
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    def test_prepare_table_for_rtf_with_table(self, sample_adsl):
        """Test preparing table for RTF with generated table."""
        session = ClinicalSession(uri="test")
        session.define_report(dataset=sample_adsl, subjid="USUBJID")

        # Mock generated table
        session.generated_table = pd.DataFrame({
            "Variable": ["Age (years)"],
            "1": ["45.2 (12.3)"],
            "2": ["46.1 (11.8)"]
        })
        session.treatment_info = {
            1: {"decode": "Placebo", "n": 10},
            2: {"decode": "Drug A", "n": 15}
        }

        result = session._prepare_table_for_rtf()

        assert result is not None
        assert isinstance(result, pd.DataFrame)
        # Check that table has columns
        assert len(result.columns) > 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_add_var_with_all_parameters(self, sample_adsl):
        """Test adding variable with all parameters."""
        session = ClinicalSession(uri="test")
        session.define_report(dataset=sample_adsl, subjid="USUBJID")

        session.add_var(
            name="AGE",
            label="Age (years)",
            stats="n mean+sd median q1q3 min+max",
            indent=2,
            where="SEX=='M'",
            basedec=1,
            skipline="N"
        )

        assert len(session.variables) == 1
        assert session.variables[0]['stats'] == "n mean+sd median q1q3 min+max"
        assert session.variables[0]['indent'] == 2
        assert session.variables[0]['where'] == "SEX=='M'"
        assert session.variables[0]['basedec'] == 1
        assert session.variables[0]['skipline'] == "N"

    def test_add_catvar_with_all_parameters(self, sample_adsl):
        """Test adding categorical variable with all parameters."""
        session = ClinicalSession(uri="test")
        session.define_report(dataset=sample_adsl, subjid="USUBJID")

        session.add_catvar(
            name="SEX",
            label="Sex, n (%)",
            stats="npct",
            codelist="M='Male',F='Female'",
            indent=1,
            where="AGE >= 18",
            denomwhere="1==1",
            totaltext="All Subjects"
        )

        assert len(session.variables) == 1
        assert session.variables[0]['codelist'] == "M='Male',F='Female'"
        assert session.variables[0]['indent'] == 1
        assert session.variables[0]['where'] == "AGE >= 18"
        assert session.variables[0]['denomwhere'] == "1==1"
        assert session.variables[0]['totaltext'] == "All Subjects"

    def test_add_cond_with_all_parameters(self, sample_adsl):
        """Test adding condition with all parameters."""
        session = ClinicalSession(uri="test")
        session.define_report(dataset=sample_adsl, subjid="USUBJID")

        session.add_cond(
            label="Elderly subjects",
            where="AGE >= 65",
            stats="npct",
            denomwhere="1==1",
            indent=2,
            countwhat="subjid"
        )

        assert len(session.variables) == 1
        assert session.variables[0]['label'] == "Elderly subjects"
        assert session.variables[0]['where'] == "AGE >= 65"
        assert session.variables[0]['stats'] == "npct"
        assert session.variables[0]['indent'] == 2
        assert session.variables[0]['denomwhere'] == "1==1"

    def test_add_label_with_indent(self, sample_adsl):
        """Test adding label with indentation."""
        session = ClinicalSession(uri="test")
        session.define_report(dataset=sample_adsl, subjid="USUBJID")

        session.add_label(label="Demographics", indent=1)

        assert session.variables[0]['indent'] == 1

    def test_define_report_with_all_titles_and_footnotes(self, sample_adsl):
        """Test defining report with all titles and footnotes."""
        session = ClinicalSession(uri="test")

        session.define_report(
            dataset=sample_adsl,
            subjid="USUBJID",
            title1="Title 1",
            title2="Title 2",
            title3="Title 3",
            title4="Title 4",
            title5="Title 5",
            title6="Title 6",
            footnot1="Footnote 1",
            footnot2="Footnote 2",
            footnot3="Footnote 3",
            footnot4="Footnote 4",
            footnot5="Footnote 5",
            footnot6="Footnote 6",
            footnot7="Footnote 7",
            footnot8="Footnote 8",
            footnot9="Footnote 9",
            footnot10="Footnote 10"
        )

        # Check that titles and footnotes are stored
        assert len(session.report_config['titles']) >= 6
        assert len(session.report_config['footnotes']) >= 10
        # Check specific values
        assert "Title 6" in session.report_config['titles']
        assert "Footnote 10" in session.report_config['footnotes']

    def test_add_trt_with_all_parameters(self, sample_adsl):
        """Test adding treatment with all parameters."""
        session = ClinicalSession(uri="test")
        session.define_report(dataset=sample_adsl, subjid="USUBJID")

        session.add_trt(
            name="TRT01PN",
            decode="TRT01P",
            autospan="Y",
            across="Y",
            totaltext="All Subjects"
        )

        assert session.treatments['autospan'] == "Y"
        assert session.treatments['across'] == "Y"
        assert session.treatments['totaltext'] == "All Subjects"

    def test_make_trt_multiple_pooled_groups(self, sample_adsl):
        """Test creating multiple pooled treatment groups."""
        session = ClinicalSession(uri="test")
        session.define_report(dataset=sample_adsl, subjid="USUBJID")
        session.add_trt(name="TRT01PN", decode="TRT01P")

        session.make_trt(name="TRT01PN", newvalue=99, newdecode="Total", values="1,2,3")
        session.make_trt(name="TRT01PN", newvalue=98, newdecode="Active", values="2,3")

        assert len(session.treatments["pooled"]) == 2
        assert session.treatments["pooled"][1]["newdecode"] == "Active"

    def test_add_group_with_parameters(self, sample_adsl):
        """Test adding group with parameters."""
        session = ClinicalSession(uri="test")
        session.define_report(dataset=sample_adsl, subjid="USUBJID")

        session.add_group(name="AGEGR1", decode="AGEGR1", across="Y")

        assert len(session.groups) > 0

