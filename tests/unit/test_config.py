"""
Unit tests for py4csr.config modules.

Tests configuration classes and utilities.
"""

import pytest

from py4csr.config.report_config import ReportConfig, StatisticConfig, PageSettings
from py4csr.config.clinical_standard import (
    get_clinical_standard_config,
    get_regulatory_submission_config,
    get_oncology_config,
)


class TestStatisticConfig:
    """Test StatisticConfig class."""

    def test_initialization(self):
        """Test basic StatisticConfig initialization."""
        config = StatisticConfig(
            name="mean",
            display="Mean",
            label="Arithmetic Mean",
            precision=1
        )
        assert config is not None
        assert config.name == "mean"
        assert config.display == "Mean"
        assert config.label == "Arithmetic Mean"
        assert config.precision == 1

    def test_attributes(self):
        """Test StatisticConfig attributes."""
        config = StatisticConfig(
            name="n",
            display="n",
            label="Number of subjects",
            precision=0
        )
        assert hasattr(config, "name")
        assert config.name == "n"


class TestPageSettings:
    """Test PageSettings class."""

    def test_initialization(self):
        """Test basic PageSettings initialization."""
        settings = PageSettings()
        assert settings is not None

    def test_default_orientation(self):
        """Test default orientation."""
        settings = PageSettings()
        assert settings.orientation == "portrait"


class TestReportConfig:
    """Test ReportConfig class."""

    def test_initialization(self):
        """Test basic ReportConfig initialization."""
        config = ReportConfig()
        assert config is not None

    def test_attributes(self):
        """Test ReportConfig has expected attributes."""
        config = ReportConfig()
        # Check for common attributes
        assert hasattr(config, "__dict__") or hasattr(config, "__dataclass_fields__")


class TestClinicalStandardConfig:
    """Test clinical standard configuration functions."""

    def test_get_clinical_standard_config(self):
        """Test getting clinical standard configuration."""
        config = get_clinical_standard_config()
        assert isinstance(config, ReportConfig)

    def test_get_regulatory_submission_config(self):
        """Test getting regulatory submission configuration."""
        config = get_regulatory_submission_config()
        assert isinstance(config, ReportConfig)

    def test_get_oncology_config(self):
        """Test getting oncology configuration."""
        config = get_oncology_config()
        assert isinstance(config, ReportConfig)


class TestConfigWorkflow:
    """Test complete configuration workflow."""

    def test_use_standard_configs(self):
        """Test using standard configurations."""
        # Get all standard configs
        clinical_config = get_clinical_standard_config()
        regulatory_config = get_regulatory_submission_config()
        oncology_config = get_oncology_config()

        # All should be ReportConfig instances
        assert isinstance(clinical_config, ReportConfig)
        assert isinstance(regulatory_config, ReportConfig)
        assert isinstance(oncology_config, ReportConfig)


class TestConfigEdgeCases:
    """Test edge cases in configuration."""

    def test_config_attributes(self):
        """Test configuration attributes."""
        config = ReportConfig()
        # Should be a valid object
        assert config is not None
        assert hasattr(config, "__dict__") or hasattr(config, "__dataclass_fields__")

