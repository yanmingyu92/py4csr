"""
Unit tests for py4csr.reporting.generators module.

Tests table generator classes.
"""

import pandas as pd
import pytest
import numpy as np
from datetime import datetime

from py4csr.reporting.generators.base_generator import BaseTableGenerator
from py4csr.reporting.generators.demographics_generator import DemographicsGenerator
from py4csr.reporting.generators.ae_summary_generator import AESummaryGenerator
from py4csr.reporting.table_specification import TableSpecification
from py4csr.reporting.table_result import TableResult
from py4csr.config.report_config import ReportConfig


@pytest.fixture
def sample_demographics_data():
    """Create sample demographics data for testing."""
    np.random.seed(42)
    return pd.DataFrame({
        "USUBJID": [f"{i:03d}" for i in range(1, 31)],
        "TRT01P": ["Placebo"] * 10 + ["Drug Low"] * 10 + ["Drug High"] * 10,
        "AGE": np.random.randint(18, 80, 30),
        "SEX": np.random.choice(["M", "F"], 30),
        "RACE": np.random.choice(["White", "Black", "Asian"], 30),
        "WEIGHT": np.random.uniform(50, 100, 30),
        "HEIGHT": np.random.uniform(150, 190, 30),
    })


@pytest.fixture
def sample_ae_data():
    """Create sample AE data for testing."""
    return pd.DataFrame({
        "USUBJID": ["001", "001", "002", "003", "004", "005"],
        "TRT01P": ["Placebo", "Placebo", "Drug", "Drug", "Placebo", "Drug"],
        "AEDECOD": ["Headache", "Nausea", "Headache", "Fatigue", "Nausea", "Headache"],
        "AEBODSYS": ["Nervous", "GI", "Nervous", "General", "GI", "Nervous"],
        "AESEV": ["MILD", "MODERATE", "MILD", "MILD", "SEVERE", "MILD"],
        "AESER": ["N", "N", "N", "N", "Y", "N"],
        "AEREL": ["RELATED", "RELATED", "NOT RELATED", "RELATED", "RELATED", "NOT RELATED"],
    })


@pytest.fixture
def sample_table_spec(sample_demographics_data):
    """Create sample table specification."""
    # Add SAFFL column for population filter
    data_with_flag = sample_demographics_data.copy()
    data_with_flag["SAFFL"] = "Y"

    config = ReportConfig()
    return TableSpecification(
        type="demographics",
        config=config,
        datasets={"adsl": {"data": data_with_flag}},
        populations={"Safety": "SAFFL == 'Y'"},
        treatments={"variable": "TRT01P", "levels": ["Placebo", "Drug Low", "Drug High"]},
        title="Demographics and Baseline Characteristics",
        subtitle="Safety Population",
        population="Safety",
        variables=["AGE", "SEX", "RACE"],
        statistics=["n", "mean", "sd", "median", "min", "max"],
    )


class ConcreteTableGenerator(BaseTableGenerator):
    """Concrete implementation for testing abstract base class."""

    def generate(self, spec: TableSpecification) -> TableResult:
        """Concrete implementation of generate method."""
        data = spec.get_data()
        validation_result = self.validate_data(data, spec)
        rtf_table = self.create_rtf_table(data, spec)
        metadata = self.generate_metadata(spec)
        
        return TableResult(
            data=data,
            rtf_table=rtf_table,
            metadata=metadata,
            validation_results=validation_result,
        )


class TestBaseTableGenerator:
    """Test BaseTableGenerator class."""

    def test_initialization(self):
        """Test generator initialization."""
        generator = ConcreteTableGenerator()
        
        assert hasattr(generator, "template_registry")
        assert hasattr(generator, "validation_rules")
        assert isinstance(generator.template_registry, dict)
        assert isinstance(generator.validation_rules, dict)

    def test_register_template(self):
        """Test template registration."""
        generator = ConcreteTableGenerator()
        
        def my_template(data, **kwargs):
            return data
        
        generator.register_template("test_template", my_template)
        
        assert "test_template" in generator.template_registry
        assert generator.template_registry["test_template"] == my_template

    def test_apply_template(self, sample_demographics_data):
        """Test applying a registered template."""
        generator = ConcreteTableGenerator()
        
        def add_column(data, col_name="new_col", value=1):
            result = data.copy()
            result[col_name] = value
            return result
        
        generator.register_template("add_column", add_column)
        
        result = generator.apply_template("add_column", sample_demographics_data, col_name="TEST", value=99)
        
        assert "TEST" in result.columns
        assert all(result["TEST"] == 99)

    def test_apply_template_not_found(self, sample_demographics_data):
        """Test applying non-existent template."""
        generator = ConcreteTableGenerator()
        
        with pytest.raises(ValueError, match="Template 'nonexistent' not found"):
            generator.apply_template("nonexistent", sample_demographics_data)

    def test_validate_data_success(self, sample_table_spec):
        """Test successful data validation."""
        generator = ConcreteTableGenerator()
        data = sample_table_spec.get_data()
        
        result = generator.validate_data(data, sample_table_spec)
        
        assert result["passed"] is True
        assert len(result["errors"]) == 0

    def test_validate_data_empty(self, sample_table_spec):
        """Test validation with empty data."""
        generator = ConcreteTableGenerator()
        empty_data = pd.DataFrame()
        
        result = generator.validate_data(empty_data, sample_table_spec)
        
        assert result["passed"] is False
        assert "Dataset is empty" in result["errors"]

    def test_validate_data_missing_variables(self, sample_table_spec):
        """Test validation with missing variables."""
        generator = ConcreteTableGenerator()
        data = pd.DataFrame({
            "USUBJID": ["001", "002"],
            "TRT01P": ["Placebo", "Drug"],
            # Missing AGE, SEX, RACE
        })
        
        result = generator.validate_data(data, sample_table_spec)
        
        assert result["passed"] is False
        assert any("Missing required variables" in err for err in result["errors"])

    def test_validate_data_missing_treatment(self, sample_demographics_data):
        """Test validation with missing treatment variable."""
        generator = ConcreteTableGenerator()
        data_with_flag = sample_demographics_data.copy()
        data_with_flag["SAFFL"] = "Y"

        config = ReportConfig()
        spec = TableSpecification(
            type="demographics",
            config=config,
            datasets={"adsl": {"data": data_with_flag}},
            populations={"Safety": "SAFFL == 'Y'"},
            treatments={"variable": "NONEXISTENT", "levels": []},
            variables=["AGE"],
        )

        result = generator.validate_data(sample_demographics_data, spec)

        assert result["passed"] is False
        assert any("Treatment variable" in err for err in result["errors"])

    def test_get_required_variables(self, sample_table_spec):
        """Test getting required variables."""
        generator = ConcreteTableGenerator()
        
        required = generator.get_required_variables(sample_table_spec)
        
        assert "TRT01P" in required
        assert "AGE" in required
        assert "SEX" in required
        assert "RACE" in required

    def test_create_rtf_table(self, sample_table_spec):
        """Test RTF table creation."""
        generator = ConcreteTableGenerator()
        data = sample_table_spec.get_data()
        
        rtf_table = generator.create_rtf_table(data, sample_table_spec)
        
        assert rtf_table is not None
        assert hasattr(rtf_table, "rtf_page")

    def test_format_statistics_numeric(self):
        """Test formatting numeric statistics."""
        generator = ConcreteTableGenerator()
        config = ReportConfig()
        
        result = generator.format_statistics(12.345, "mean", config)
        
        assert isinstance(result, str)
        assert "12" in result

    def test_format_statistics_missing(self):
        """Test formatting missing values."""
        generator = ConcreteTableGenerator()
        config = ReportConfig()
        
        result = generator.format_statistics(np.nan, "mean", config)
        
        assert result == ""

    def test_generate_metadata(self, sample_table_spec):
        """Test metadata generation."""
        generator = ConcreteTableGenerator()
        
        metadata = generator.generate_metadata(sample_table_spec)
        
        assert "table_type" in metadata
        assert "title" in metadata
        assert "treatment_variable" in metadata
        assert "generation_time" in metadata
        assert metadata["table_type"] == "demographics"

    def test_generate_metadata_custom_time(self, sample_table_spec):
        """Test metadata generation with custom time."""
        generator = ConcreteTableGenerator()
        custom_time = datetime(2023, 1, 1, 12, 0, 0)
        
        metadata = generator.generate_metadata(sample_table_spec, generation_time=custom_time)
        
        assert metadata["generation_time"] == custom_time

    def test_post_process_data(self, sample_table_spec):
        """Test data post-processing."""
        generator = ConcreteTableGenerator()
        data = sample_table_spec.get_data()
        
        result = generator.post_process_data(data, sample_table_spec)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(data)


class TestDemographicsGenerator:
    """Test DemographicsGenerator class."""

    def test_initialization(self):
        """Test demographics generator initialization."""
        generator = DemographicsGenerator()
        
        assert isinstance(generator, BaseTableGenerator)
        assert hasattr(generator, "template_registry")

    def test_generate_basic(self, sample_table_spec):
        """Test basic demographics table generation."""
        generator = DemographicsGenerator()
        
        result = generator.generate(sample_table_spec)
        
        assert isinstance(result, TableResult)
        assert result.data is not None
        assert result.rtf_table is not None
        assert result.metadata is not None

    def test_generate_with_validation_error(self):
        """Test generation with validation error."""
        generator = DemographicsGenerator()

        # Create spec with empty data
        config = ReportConfig()
        spec = TableSpecification(
            type="demographics",
            config=config,
            datasets={"adsl": {"data": pd.DataFrame()}},
            populations={"Safety": "SAFFL == 'Y'"},
            treatments={"variable": "TRT01P", "levels": []},
            variables=["AGE"],
        )

        with pytest.raises(ValueError, match="Data validation failed"):
            generator.generate(spec)

    def test_generate_metadata(self, sample_table_spec):
        """Test metadata in generated result."""
        generator = DemographicsGenerator()
        
        result = generator.generate(sample_table_spec)
        
        assert "table_type" in result.metadata
        assert "n_subjects" in result.metadata
        assert result.metadata["table_type"] == "demographics"


class TestAESummaryGenerator:
    """Test AESummaryGenerator class."""

    def test_initialization(self):
        """Test AE summary generator initialization."""
        generator = AESummaryGenerator()
        
        assert isinstance(generator, BaseTableGenerator)

    def test_generate_basic(self, sample_ae_data):
        """Test basic AE summary table generation."""
        generator = AESummaryGenerator()

        # Add SAFFL column for population filter
        ae_data_with_flag = sample_ae_data.copy()
        ae_data_with_flag["SAFFL"] = "Y"

        config = ReportConfig()
        spec = TableSpecification(
            type="ae_summary",
            config=config,
            datasets={"adae": {"data": ae_data_with_flag}},
            populations={"Safety": "SAFFL == 'Y'"},
            treatments={"variable": "TRT01P", "levels": ["Placebo", "Drug"]},
            variables=["AEDECOD"],
        )

        result = generator.generate(spec)

        assert isinstance(result, TableResult)
        assert result.data is not None
        assert result.metadata is not None

    def test_generate_metadata(self, sample_ae_data):
        """Test metadata in AE summary result."""
        generator = AESummaryGenerator()

        # Add SAFFL column for population filter
        ae_data_with_flag = sample_ae_data.copy()
        ae_data_with_flag["SAFFL"] = "Y"

        config = ReportConfig()
        spec = TableSpecification(
            type="ae_summary",
            config=config,
            datasets={"adae": {"data": ae_data_with_flag}},
            populations={"Safety": "SAFFL == 'Y'"},
            treatments={"variable": "TRT01P", "levels": ["Placebo", "Drug"]},
            variables=["AEDECOD"],
        )

        result = generator.generate(spec)

        assert "n_subjects" in result.metadata
        assert "n_events" in result.metadata
        assert "treatment_groups" in result.metadata
        assert result.metadata["n_events"] == 6

