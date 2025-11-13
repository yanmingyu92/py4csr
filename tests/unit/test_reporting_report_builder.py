"""
Unit tests for py4csr.reporting.report_builder module.

Tests ReportBuilder class and functional report building.
"""

import pandas as pd
import pytest
from pathlib import Path

from py4csr.reporting.report_builder import ReportBuilder
from py4csr.config.report_config import ReportConfig


class TestReportBuilderInit:
    """Test ReportBuilder initialization."""

    def test_basic_initialization(self):
        """Test basic ReportBuilder initialization."""
        config = ReportConfig()
        builder = ReportBuilder(config)

        assert builder.config is not None
        assert isinstance(builder.datasets, dict)
        assert isinstance(builder.populations, dict)
        assert isinstance(builder.treatments, dict)
        assert isinstance(builder.tables, list)
        assert isinstance(builder.metadata, dict)
        assert builder._finalized is False

    def test_initialization_with_custom_config(self):
        """Test initialization with custom config."""
        config = ReportConfig()
        config.page_settings.orientation = "landscape"

        builder = ReportBuilder(config)

        assert builder.config.page_settings.orientation == "landscape"


class TestInitStudy:
    """Test init_study method."""

    def test_init_study_basic(self):
        """Test basic study initialization."""
        config = ReportConfig()
        builder = ReportBuilder(config)

        result = builder.init_study(uri="STUDY001", title="Phase III Study")

        assert result is builder  # Method chaining
        assert builder.metadata["uri"] == "STUDY001"
        assert builder.metadata["title"] == "Phase III Study"
        assert "created_by" in builder.metadata
        assert "created_date" in builder.metadata

    def test_init_study_with_protocol(self):
        """Test study initialization with protocol."""
        config = ReportConfig()
        builder = ReportBuilder(config)

        builder.init_study(
            uri="STUDY001", title="Phase III Study", protocol="ABC-123-2024"
        )

        assert builder.metadata["protocol"] == "ABC-123-2024"

    def test_init_study_with_all_metadata(self):
        """Test study initialization with all metadata."""
        config = ReportConfig()
        builder = ReportBuilder(config)

        builder.init_study(
            uri="STUDY001",
            title="Phase III Study",
            protocol="ABC-123-2024",
            compound="Drug X",
            indication="Hypertension",
            sponsor="Pharma Corp",
        )

        assert builder.metadata["compound"] == "Drug X"
        assert builder.metadata["indication"] == "Hypertension"
        assert builder.metadata["sponsor"] == "Pharma Corp"


class TestAddDataset:
    """Test add_dataset method."""

    def test_add_dataset_basic(self, sample_adsl):
        """Test basic dataset addition."""
        config = ReportConfig()
        builder = ReportBuilder(config)

        result = builder.add_dataset(sample_adsl, "adsl", "subject_level")

        assert result is builder  # Method chaining
        assert "adsl" in builder.datasets
        assert builder.datasets["adsl"]["type"] == "subject_level"

    def test_add_multiple_datasets(self, sample_adsl, sample_adae):
        """Test adding multiple datasets."""
        config = ReportConfig()
        builder = ReportBuilder(config)

        builder.add_dataset(sample_adsl, "adsl", "subject_level")
        builder.add_dataset(sample_adae, "adae", "adverse_events")

        assert len(builder.datasets) == 2
        assert "adsl" in builder.datasets
        assert "adae" in builder.datasets

    def test_dataset_copy(self, sample_adsl):
        """Test that dataset is copied, not referenced."""
        config = ReportConfig()
        builder = ReportBuilder(config)

        original_shape = sample_adsl.shape
        builder.add_dataset(sample_adsl, "adsl", "subject_level")

        # Modify original
        sample_adsl["NEW_COL"] = 1

        # Builder's copy should not be affected
        assert "NEW_COL" not in builder.datasets["adsl"]["data"].columns


class TestDefinePopulations:
    """Test define_populations method."""

    def test_define_populations_basic(self):
        """Test basic population definition."""
        config = ReportConfig()
        builder = ReportBuilder(config)

        result = builder.define_populations(safety="SAFFL=='Y'")

        assert result is builder  # Method chaining
        assert "safety" in builder.populations
        assert builder.populations["safety"] == "SAFFL=='Y'"

    def test_define_multiple_populations(self):
        """Test defining multiple populations."""
        config = ReportConfig()
        builder = ReportBuilder(config)

        builder.define_populations(
            safety="SAFFL=='Y'", efficacy="EFFFL=='Y'", itt="ITTFL=='Y'"
        )

        assert len(builder.populations) == 3
        assert builder.populations["safety"] == "SAFFL=='Y'"
        assert builder.populations["efficacy"] == "EFFFL=='Y'"
        assert builder.populations["itt"] == "ITTFL=='Y'"


class TestDefineTreatments:
    """Test define_treatments method."""

    def test_define_treatments_basic(self, sample_adsl):
        """Test basic treatment definition."""
        config = ReportConfig()
        builder = ReportBuilder(config)
        builder.add_dataset(sample_adsl, "adsl", "subject_level")

        result = builder.define_treatments(var="TRT01P")

        assert result is builder  # Method chaining
        assert builder.treatments["variable"] == "TRT01P"
        assert builder.treatments["decode"] == "TRT01P"  # Default to var

    def test_define_treatments_with_decode(self, sample_adsl):
        """Test treatment definition with decode."""
        config = ReportConfig()
        builder = ReportBuilder(config)
        builder.add_dataset(sample_adsl, "adsl", "subject_level")

        builder.define_treatments(var="TRT01P", decode="TRT01A")

        assert builder.treatments["variable"] == "TRT01P"
        assert builder.treatments["decode"] == "TRT01A"

    def test_define_treatments_with_num_var(self, sample_adsl):
        """Test treatment definition with numeric variable."""
        config = ReportConfig()
        builder = ReportBuilder(config)
        builder.add_dataset(sample_adsl, "adsl", "subject_level")

        builder.define_treatments(var="TRT01P", num_var="TRT01PN")

        assert builder.treatments["num_variable"] == "TRT01PN"


class TestAddTable:
    """Test add_table method."""

    def test_add_table_basic(self, sample_adsl):
        """Test basic table addition."""
        config = ReportConfig()
        builder = ReportBuilder(config)
        builder.add_dataset(sample_adsl, "adsl", "subject_level")
        builder.define_populations(safety="SAFFL=='Y'")
        builder.define_treatments(var="TRT01P")

        result = builder.add_table("demographics")

        assert result is builder  # Method chaining
        assert len(builder.tables) == 1
        assert builder.tables[0].type == "demographics"

    def test_add_table_with_parameters(self, sample_adsl):
        """Test table addition with parameters."""
        config = ReportConfig()
        builder = ReportBuilder(config)
        builder.add_dataset(sample_adsl, "adsl", "subject_level")
        builder.define_populations(safety="SAFFL=='Y'")
        builder.define_treatments(var="TRT01P")

        builder.add_table(
            "demographics",
            title="Demographics Table",
            subtitle="Safety Population",
            variables=["AGE", "SEX", "RACE"],
        )

        assert builder.tables[0].title == "Demographics Table"
        assert builder.tables[0].subtitle == "Safety Population"
        assert len(builder.tables[0].variables) == 3


class TestConvenienceMethods:
    """Test convenience methods for common tables."""

    def test_add_demographics_table(self, sample_adsl):
        """Test add_demographics_table convenience method."""
        config = ReportConfig()
        builder = ReportBuilder(config)
        builder.add_dataset(sample_adsl, "adsl", "subject_level")
        builder.define_populations(safety="SAFFL=='Y'")
        builder.define_treatments(var="TRT01P")

        result = builder.add_demographics_table()

        assert result is builder
        assert len(builder.tables) == 1
        assert builder.tables[0].type == "demographics"
        assert "Demographics" in builder.tables[0].title

    def test_add_disposition_table(self, sample_adsl):
        """Test add_disposition_table convenience method."""
        config = ReportConfig()
        builder = ReportBuilder(config)
        builder.add_dataset(sample_adsl, "adsl", "subject_level")
        builder.define_populations(randomized="RANDFL=='Y'")
        builder.define_treatments(var="TRT01P")

        result = builder.add_disposition_table()

        assert result is builder
        assert len(builder.tables) == 1
        assert builder.tables[0].type == "disposition"

    def test_add_ae_summary_table(self, sample_adsl, sample_adae):
        """Test add_ae_summary_table convenience method."""
        config = ReportConfig()
        builder = ReportBuilder(config)
        builder.add_dataset(sample_adsl, "adsl", "subject_level")
        builder.add_dataset(sample_adae, "adae", "adverse_events")
        builder.define_populations(safety="SAFFL=='Y'")
        builder.define_treatments(var="TRT01P")

        result = builder.add_ae_summary_table()

        assert result is builder
        assert len(builder.tables) == 1
        assert builder.tables[0].type == "ae_summary"


class TestMethodChaining:
    """Test method chaining workflow."""

    def test_complete_workflow_chaining(self, sample_adsl, sample_adae):
        """Test complete workflow with method chaining."""
        config = ReportConfig()

        builder = (
            ReportBuilder(config)
            .init_study(uri="STUDY001", title="Phase III Study")
            .add_dataset(sample_adsl, "adsl", "subject_level")
            .add_dataset(sample_adae, "adae", "adverse_events")
            .define_populations(safety="SAFFL=='Y'", efficacy="EFFFL=='Y'")
            .define_treatments(var="TRT01P", decode="TRT01A")
            .add_demographics_table()
            .add_ae_summary_table()
        )

        assert builder.metadata["uri"] == "STUDY001"
        assert len(builder.datasets) == 2
        assert len(builder.populations) == 2
        assert len(builder.tables) == 2

    def test_minimal_workflow(self, sample_adsl):
        """Test minimal workflow."""
        config = ReportConfig()

        builder = (
            ReportBuilder(config)
            .init_study(uri="MINIMAL", title="Minimal Study")
            .add_dataset(sample_adsl, "adsl", "subject_level")
            .define_populations(safety="SAFFL=='Y'")
            .define_treatments(var="TRT01P")
            .add_demographics_table()
        )

        assert len(builder.tables) == 1


class TestFinalize:
    """Test finalize method."""

    def test_finalize_basic(self, sample_adsl):
        """Test basic finalize."""
        config = ReportConfig()
        builder = (
            ReportBuilder(config)
            .init_study(uri="STUDY001", title="Test Study")
            .add_dataset(sample_adsl, "adsl", "subject_level")
            .define_populations(safety="SAFFL=='Y'")
            .define_treatments(var="TRT01P")
        )

        result = builder.finalize()

        assert result is not None
        assert result.metadata["uri"] == "STUDY001"
        assert builder._finalized is True

    def test_finalize_returns_report_result(self, sample_adsl):
        """Test that finalize returns ReportResult."""
        config = ReportConfig()
        builder = (
            ReportBuilder(config)
            .init_study(uri="STUDY001", title="Test Study")
            .add_dataset(sample_adsl, "adsl", "subject_level")
        )

        result = builder.finalize()

        assert hasattr(result, "metadata")
        assert hasattr(result, "generated_files")
        assert hasattr(result, "summary")
        assert hasattr(result, "config")


class TestAdditionalConvenienceMethods:
    """Test additional convenience methods for common tables."""

    def test_add_ae_detail_table(self, sample_adsl, sample_adae):
        """Test add_ae_detail_table convenience method."""
        config = ReportConfig()
        builder = ReportBuilder(config)
        builder.add_dataset(sample_adsl, "adsl", "subject_level")
        builder.add_dataset(sample_adae, "adae", "adverse_events")
        builder.define_populations(safety="SAFFL=='Y'")
        builder.define_treatments(var="TRT01P")

        result = builder.add_ae_detail_table()

        assert result is builder
        assert len(builder.tables) == 1
        assert builder.tables[0].type == "ae_detail"
        assert "Adverse Events" in builder.tables[0].title

    def test_add_efficacy_table(self, sample_adsl):
        """Test add_efficacy_table convenience method."""
        config = ReportConfig()
        builder = ReportBuilder(config)
        builder.add_dataset(sample_adsl, "adsl", "subject_level")
        builder.define_populations(efficacy="EFFFL=='Y'")
        builder.define_treatments(var="TRT01P")

        result = builder.add_efficacy_table()

        assert result is builder
        assert len(builder.tables) == 1
        assert builder.tables[0].type == "efficacy"
        assert "Efficacy" in builder.tables[0].title

    def test_add_laboratory_tables(self, sample_adsl):
        """Test add_laboratory_tables convenience method."""
        config = ReportConfig()
        builder = ReportBuilder(config)
        builder.add_dataset(sample_adsl, "adsl", "subject_level")
        builder.define_populations(safety="SAFFL=='Y'")
        builder.define_treatments(var="TRT01P")

        result = builder.add_laboratory_tables()

        assert result is builder
        assert len(builder.tables) == 1
        assert builder.tables[0].type == "laboratory"
        assert "Laboratory" in builder.tables[0].title

    def test_add_survival_analysis(self, sample_adsl):
        """Test add_survival_analysis convenience method."""
        config = ReportConfig()
        builder = ReportBuilder(config)
        builder.add_dataset(sample_adsl, "adsl", "subject_level")
        builder.define_populations(efficacy="EFFFL=='Y'")
        builder.define_treatments(var="TRT01P")

        result = builder.add_survival_analysis()

        assert result is builder
        assert len(builder.tables) == 1
        assert builder.tables[0].type == "survival"
        assert "Kaplan-Meier" in builder.tables[0].title

    def test_add_vital_signs_table(self, sample_adsl):
        """Test add_vital_signs_table convenience method."""
        config = ReportConfig()
        builder = ReportBuilder(config)
        builder.add_dataset(sample_adsl, "adsl", "subject_level")
        builder.define_populations(safety="SAFFL=='Y'")
        builder.define_treatments(var="TRT01P")

        result = builder.add_vital_signs_table()

        assert result is builder
        assert len(builder.tables) == 1
        assert builder.tables[0].type == "vital_signs"
        assert "Vital Signs" in builder.tables[0].title

    def test_add_concomitant_meds_table(self, sample_adsl):
        """Test add_concomitant_meds_table convenience method."""
        config = ReportConfig()
        builder = ReportBuilder(config)
        builder.add_dataset(sample_adsl, "adsl", "subject_level")
        builder.define_populations(safety="SAFFL=='Y'")
        builder.define_treatments(var="TRT01P")

        result = builder.add_concomitant_meds_table()

        assert result is builder
        assert len(builder.tables) == 1
        assert builder.tables[0].type == "concomitant_meds"
        assert "Concomitant Medications" in builder.tables[0].title

    def test_add_medical_history_table(self, sample_adsl):
        """Test add_medical_history_table convenience method."""
        config = ReportConfig()
        builder = ReportBuilder(config)
        builder.add_dataset(sample_adsl, "adsl", "subject_level")
        builder.define_populations(safety="SAFFL=='Y'")
        builder.define_treatments(var="TRT01P")

        result = builder.add_medical_history_table()

        assert result is builder
        assert len(builder.tables) == 1
        assert builder.tables[0].type == "medical_history"
        assert "Medical History" in builder.tables[0].title

    def test_add_exposure_table(self, sample_adsl):
        """Test add_exposure_table convenience method."""
        config = ReportConfig()
        builder = ReportBuilder(config)
        builder.add_dataset(sample_adsl, "adsl", "subject_level")
        builder.define_populations(safety="SAFFL=='Y'")
        builder.define_treatments(var="TRT01P")

        result = builder.add_exposure_table()

        assert result is builder
        assert len(builder.tables) == 1
        assert builder.tables[0].type == "exposure"
        assert "Exposure" in builder.tables[0].title


class TestHelperMethods:
    """Test helper methods."""

    def test_extract_dataset_metadata(self, sample_adsl):
        """Test _extract_dataset_metadata helper method."""
        config = ReportConfig()
        builder = ReportBuilder(config)

        metadata = builder._extract_dataset_metadata(sample_adsl, "subject_level")

        assert "n_records" in metadata
        assert "n_variables" in metadata
        assert "variables" in metadata
        assert "type" in metadata
        assert "memory_usage" in metadata
        assert metadata["type"] == "subject_level"
        assert metadata["n_records"] == len(sample_adsl)
        assert metadata["n_variables"] == len(sample_adsl.columns)

    def test_get_treatment_levels(self, sample_adsl):
        """Test _get_treatment_levels helper method."""
        config = ReportConfig()
        builder = ReportBuilder(config)
        builder.add_dataset(sample_adsl, "adsl", "subject_level")

        levels = builder._get_treatment_levels("TRT01P")

        assert isinstance(levels, list)
        assert len(levels) > 0
        # Should be sorted
        assert levels == sorted(levels)

    def test_get_treatment_levels_multiple_datasets(self, sample_adsl, sample_adae):
        """Test _get_treatment_levels with multiple datasets."""
        config = ReportConfig()
        builder = ReportBuilder(config)
        builder.add_dataset(sample_adsl, "adsl", "subject_level")
        builder.add_dataset(sample_adae, "adae", "adverse_events")

        levels = builder._get_treatment_levels("TRT01P")

        assert isinstance(levels, list)
        # Should remove duplicates
        assert len(levels) == len(set(levels))

    def test_generate_summary(self, sample_adsl, tmp_path):
        """Test _generate_summary helper method."""
        config = ReportConfig()
        builder = ReportBuilder(config)
        builder.add_dataset(sample_adsl, "adsl", "subject_level")
        builder.define_populations(safety="SAFFL=='Y'")
        builder.define_treatments(var="TRT01P")
        builder.add_demographics_table()

        # Create a dummy file to simulate generated files
        dummy_file = tmp_path / "test.rtf"
        dummy_file.write_text("test content")
        builder.generated_files = [dummy_file]

        summary = builder._generate_summary()

        assert "total_files" in summary
        assert "total_size_bytes" in summary
        assert "total_size_mb" in summary
        assert "file_types" in summary
        assert "tables_generated" in summary
        assert "datasets_used" in summary
        assert "populations_defined" in summary
        assert "generation_time" in summary
        assert summary["total_files"] == 1
        assert summary["tables_generated"] == 1
        assert summary["datasets_used"] == 1
        assert summary["populations_defined"] == 1


class TestEdgeCases:
    """Test edge cases."""

    def test_empty_builder(self):
        """Test builder with no configuration."""
        config = ReportConfig()
        builder = ReportBuilder(config)

        assert len(builder.datasets) == 0
        assert len(builder.tables) == 0

    def test_add_table_without_datasets(self):
        """Test adding table without datasets."""
        config = ReportConfig()
        builder = ReportBuilder(config)

        # Should not raise error
        builder.add_table("demographics")
        assert len(builder.tables) == 1

    def test_finalize_twice(self, sample_adsl):
        """Test finalizing twice raises warning."""
        config = ReportConfig()
        builder = (
            ReportBuilder(config)
            .init_study(uri="STUDY001", title="Test Study")
            .add_dataset(sample_adsl, "adsl", "subject_level")
        )

        builder.finalize()

        # Second finalize should warn
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            builder.finalize()
            assert len(w) == 1
            assert "already finalized" in str(w[0].message).lower()

    def test_init_study_with_custom_metadata(self):
        """Test init_study with custom metadata fields."""
        config = ReportConfig()
        builder = ReportBuilder(config)

        builder.init_study(
            uri="STUDY001",
            title="Test Study",
            custom_field1="value1",
            custom_field2="value2",
        )

        assert builder.metadata["custom_field1"] == "value1"
        assert builder.metadata["custom_field2"] == "value2"

