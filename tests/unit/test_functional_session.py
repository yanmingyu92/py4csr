"""
Unit tests for py4csr.functional.session module.

Tests ReportSession class and functional composition.
"""

import pandas as pd
import pytest
from pathlib import Path

from py4csr.functional.session import ReportSession
from py4csr.functional.config import FunctionalConfig


class TestReportSessionInit:
    """Test ReportSession initialization."""

    def test_basic_initialization(self):
        """Test basic ReportSession initialization."""
        session = ReportSession()

        assert session.config is not None
        assert isinstance(session.metadata, dict)
        assert isinstance(session.datasets, dict)
        assert isinstance(session.populations, dict)
        assert isinstance(session.treatments, dict)
        assert isinstance(session.tables, list)
        assert session._initialized is False
        assert session._finalized is False

    def test_initialization_with_config(self):
        """Test initialization with custom config."""
        config = FunctionalConfig.clinical_standard()
        session = ReportSession(config=config)

        assert session.config is not None
        assert session.config == config

    def test_initialization_creates_templates(self):
        """Test that initialization creates statistical templates."""
        session = ReportSession()

        assert hasattr(session, "templates")
        assert session.templates is not None


class TestInitStudy:
    """Test init_study method."""

    def test_init_study_basic(self):
        """Test basic study initialization."""
        session = ReportSession()

        result = session.init_study(uri="STUDY001", title="Phase III Study")

        assert result is session  # Method chaining
        assert session.metadata["uri"] == "STUDY001"
        assert session.metadata["title"] == "Phase III Study"
        assert "created_by" in session.metadata
        assert "created_date" in session.metadata

    def test_init_study_with_protocol(self):
        """Test study initialization with protocol."""
        session = ReportSession()

        session.init_study(
            uri="STUDY001", title="Phase III Study", protocol="ABC-123-2024"
        )

        assert session.metadata["protocol"] == "ABC-123-2024"

    def test_init_study_with_all_metadata(self):
        """Test study initialization with all metadata."""
        session = ReportSession()

        session.init_study(
            uri="STUDY001",
            title="Phase III Study",
            protocol="ABC-123-2024",
            compound="Drug X",
            sponsor="Pharma Corp",
        )

        assert session.metadata["compound"] == "Drug X"
        assert session.metadata["sponsor"] == "Pharma Corp"

    def test_init_study_sets_initialized_flag(self):
        """Test that init_study sets initialized flag."""
        session = ReportSession()

        session.init_study(uri="STUDY001", title="Test Study")

        assert session._initialized is True


class TestDefinePopulations:
    """Test define_populations method."""

    def test_define_populations_basic(self):
        """Test basic population definition."""
        session = ReportSession()

        result = session.define_populations(safety="SAFFL=='Y'")

        assert result is session  # Method chaining
        assert "safety" in session.populations
        assert session.populations["safety"] == "SAFFL=='Y'"

    def test_define_multiple_populations(self):
        """Test defining multiple populations."""
        session = ReportSession()

        session.define_populations(
            safety="SAFFL=='Y'", efficacy="EFFFL=='Y'", itt="ITTFL=='Y'"
        )

        assert len(session.populations) == 3
        assert session.populations["safety"] == "SAFFL=='Y'"
        assert session.populations["efficacy"] == "EFFFL=='Y'"
        assert session.populations["itt"] == "ITTFL=='Y'"


class TestDefineTreatments:
    """Test define_treatments method."""

    def test_define_treatments_basic(self):
        """Test basic treatment definition."""
        session = ReportSession()

        result = session.define_treatments(var="TRT01P")

        assert result is session  # Method chaining
        assert "variable" in session.treatments
        assert session.treatments["variable"] == "TRT01P"

    def test_define_treatments_with_decode(self):
        """Test treatment definition with decode."""
        session = ReportSession()

        session.define_treatments(var="TRT01P", decode="TRT01A")

        assert session.treatments["variable"] == "TRT01P"
        assert session.treatments["decode"] == "TRT01A"


class TestLoadDatasets:
    """Test load_datasets method."""

    def test_load_datasets_basic(self, sample_adsl):
        """Test basic dataset loading."""
        session = ReportSession()
        session.init_study(uri="STUDY001", title="Test Study")

        result = session.load_datasets(datasets={"adsl": sample_adsl})

        assert result is session  # Method chaining
        assert "ADSL" in session.datasets

    def test_load_multiple_datasets(self, sample_adsl, sample_adae):
        """Test loading multiple datasets."""
        session = ReportSession()
        session.init_study(uri="STUDY001", title="Test Study")

        session.load_datasets(datasets={"adsl": sample_adsl, "adae": sample_adae})

        assert len(session.datasets) == 2
        assert "ADSL" in session.datasets
        assert "ADAE" in session.datasets


class TestMethodChaining:
    """Test method chaining workflow."""

    def test_complete_workflow_chaining(self, sample_adsl, sample_adae):
        """Test complete workflow with method chaining."""
        session = (
            ReportSession()
            .init_study(uri="STUDY001", title="Phase III Study")
            .load_datasets(datasets={"adsl": sample_adsl, "adae": sample_adae})
            .define_populations(safety="SAFFL=='Y'", efficacy="EFFFL=='Y'")
            .define_treatments(var="TRT01P", decode="TRT01A")
        )

        assert session.metadata["uri"] == "STUDY001"
        assert len(session.datasets) == 2
        assert len(session.populations) == 2
        assert session.treatments["variable"] == "TRT01P"

    def test_minimal_workflow(self, sample_adsl):
        """Test minimal workflow."""
        session = (
            ReportSession()
            .init_study(uri="MINIMAL", title="Minimal Study")
            .load_datasets(datasets={"adsl": sample_adsl})
            .define_populations(safety="SAFFL=='Y'")
            .define_treatments(var="TRT01P")
        )

        assert session.metadata["uri"] == "MINIMAL"
        assert len(session.datasets) == 1


class TestSessionState:
    """Test session state management."""

    def test_initial_state(self):
        """Test initial session state."""
        session = ReportSession()

        assert session._initialized is False
        assert session._finalized is False
        assert session._current_table_id == 0

    def test_state_after_init_study(self):
        """Test state after init_study."""
        session = ReportSession()
        session.init_study(uri="STUDY001", title="Test Study")

        assert session._initialized is True
        assert session._finalized is False

    def test_empty_session(self):
        """Test empty session."""
        session = ReportSession()

        assert len(session.datasets) == 0
        assert len(session.populations) == 0
        assert len(session.treatments) == 0
        assert len(session.tables) == 0


class TestConfigIntegration:
    """Test configuration integration."""

    def test_default_config(self):
        """Test default configuration."""
        session = ReportSession()

        assert session.config is not None

    def test_custom_config(self):
        """Test custom configuration."""
        config = FunctionalConfig.clinical_standard()
        session = ReportSession(config=config)

        assert session.config == config


class TestEdgeCases:
    """Test edge cases."""

    def test_multiple_init_study_calls(self):
        """Test multiple init_study calls."""
        session = ReportSession()

        session.init_study(uri="STUDY001", title="First Study")
        session.init_study(uri="STUDY002", title="Second Study")

        # Should use the latest
        assert session.metadata["uri"] == "STUDY002"
        assert session.metadata["title"] == "Second Study"

    def test_define_populations_multiple_times(self):
        """Test defining populations multiple times."""
        session = ReportSession()

        session.define_populations(safety="SAFFL=='Y'")
        session.define_populations(efficacy="EFFFL=='Y'")

        # Should accumulate
        assert len(session.populations) == 2

    def test_load_dataset_with_same_name(self, sample_adsl):
        """Test loading dataset with same name twice."""
        session = ReportSession()
        session.init_study(uri="STUDY001", title="Test Study")

        session.load_datasets(datasets={"adsl": sample_adsl})
        session.load_datasets(datasets={"adsl": sample_adsl})

        # Should overwrite
        assert len(session.datasets) == 1


class TestStatisticalTemplates:
    """Test statistical templates integration."""

    def test_templates_available(self):
        """Test that templates are available."""
        session = ReportSession()

        assert hasattr(session, "templates")
        assert session.templates is not None

    def test_templates_use_config(self):
        """Test that templates use session config."""
        config = FunctionalConfig.clinical_standard()
        session = ReportSession(config=config)

        assert session.templates.config == config


class TestWorkflowPatterns:
    """Test common workflow patterns."""

    def test_demographics_workflow(self, sample_adsl):
        """Test demographics table workflow."""
        session = (
            ReportSession()
            .init_study(uri="DEMO", title="Demographics Study")
            .load_datasets(datasets={"adsl": sample_adsl})
            .define_populations(safety="SAFFL=='Y'")
            .define_treatments(var="TRT01P")
        )

        assert session._initialized is True
        assert "ADSL" in session.datasets
        assert "safety" in session.populations

    def test_safety_workflow(self, sample_adsl, sample_adae):
        """Test safety analysis workflow."""
        session = (
            ReportSession()
            .init_study(uri="SAFETY", title="Safety Study")
            .load_datasets(datasets={"adsl": sample_adsl, "adae": sample_adae})
            .define_populations(safety="SAFFL=='Y'")
            .define_treatments(var="TRT01P")
        )

        assert len(session.datasets) == 2
        assert "ADSL" in session.datasets
        assert "ADAE" in session.datasets

    def test_efficacy_workflow(self, sample_adsl):
        """Test efficacy analysis workflow."""
        session = (
            ReportSession()
            .init_study(uri="EFFICACY", title="Efficacy Study")
            .load_datasets(datasets={"adsl": sample_adsl})
            .define_populations(efficacy="EFFFL=='Y'", itt="ITTFL=='Y'")
            .define_treatments(var="TRT01P")
        )

        assert "efficacy" in session.populations
        assert "itt" in session.populations

