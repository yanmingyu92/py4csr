"""
Unit tests for py4csr.exceptions module.

Tests all custom exception classes and validation functions.
"""

import pandas as pd
import pytest

from py4csr.exceptions import (
    Py4csrError,
    DataValidationError,
    ConfigurationError,
    OutputFormatError,
    StatisticalError,
    MetadataError,
    SessionError,
    validate_required_columns,
)


class TestPy4csrError:
    """Test base Py4csrError exception."""
    
    def test_base_exception(self):
        """Test that Py4csrError can be raised and caught."""
        with pytest.raises(Py4csrError):
            raise Py4csrError("Test error")
    
    def test_exception_message(self):
        """Test that exception message is preserved."""
        error_msg = "Test error message"
        with pytest.raises(Py4csrError, match=error_msg):
            raise Py4csrError(error_msg)


class TestDataValidationError:
    """Test DataValidationError exception."""
    
    def test_basic_error(self):
        """Test basic DataValidationError."""
        with pytest.raises(DataValidationError):
            raise DataValidationError("Validation failed")
    
    def test_error_with_column(self):
        """Test DataValidationError with column information."""
        error = DataValidationError(
            "Missing column",
            column="USUBJID"
        )
        assert "USUBJID" in str(error)
        assert error.column == "USUBJID"
    
    def test_error_with_expected_actual(self):
        """Test DataValidationError with expected and actual values."""
        error = DataValidationError(
            "Type mismatch",
            column="AGE",
            expected="numeric",
            actual="string"
        )
        assert "AGE" in str(error)
        assert "numeric" in str(error)
        assert "string" in str(error)
        assert error.expected == "numeric"
        assert error.actual == "string"


class TestConfigurationError:
    """Test ConfigurationError exception."""
    
    def test_basic_error(self):
        """Test basic ConfigurationError."""
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("Configuration invalid")
    
    def test_error_with_parameter(self):
        """Test ConfigurationError with parameter information."""
        error = ConfigurationError(
            "Invalid parameter",
            parameter="output_format"
        )
        assert "output_format" in str(error)
        assert error.parameter == "output_format"
    
    def test_error_with_value(self):
        """Test ConfigurationError with value information."""
        error = ConfigurationError(
            "Invalid value",
            parameter="format",
            value="invalid"
        )
        assert "format" in str(error)
        assert "invalid" in str(error)
        assert error.value == "invalid"


class TestOutputFormatError:
    """Test OutputFormatError exception."""
    
    def test_basic_error(self):
        """Test basic OutputFormatError."""
        with pytest.raises(OutputFormatError):
            raise OutputFormatError("Format error")
    
    def test_error_with_format(self):
        """Test OutputFormatError with format information."""
        error = OutputFormatError(
            "Unsupported format",
            format="pdf"
        )
        assert "pdf" in str(error)
        assert error.format == "pdf"
    
    def test_error_with_reason(self):
        """Test OutputFormatError with reason."""
        error = OutputFormatError(
            "Cannot create PDF",
            format="pdf",
            reason="reportlab not installed"
        )
        assert "pdf" in str(error)
        assert "reportlab" in str(error)
        assert error.reason == "reportlab not installed"


class TestStatisticalError:
    """Test StatisticalError exception."""
    
    def test_basic_error(self):
        """Test basic StatisticalError."""
        with pytest.raises(StatisticalError):
            raise StatisticalError("Statistical calculation failed")
    
    def test_error_with_method(self):
        """Test StatisticalError with method information."""
        error = StatisticalError(
            "Calculation failed",
            method="mean"
        )
        assert "mean" in str(error)
        assert error.method == "mean"
    
    def test_error_with_reason(self):
        """Test StatisticalError with reason."""
        error = StatisticalError(
            "Cannot compute",
            method="std",
            reason="Empty array"
        )
        assert "std" in str(error)
        assert "Empty array" in str(error)
        assert error.reason == "Empty array"


class TestMetadataError:
    """Test MetadataError exception."""
    
    def test_basic_error(self):
        """Test basic MetadataError."""
        with pytest.raises(MetadataError):
            raise MetadataError("Metadata error")
    
    def test_error_with_file(self):
        """Test MetadataError with file information."""
        error = MetadataError(
            "Cannot load file",
            file="TitleFootnote.xlsx"
        )
        assert "TitleFootnote.xlsx" in str(error)
        assert error.file == "TitleFootnote.xlsx"
    
    def test_error_with_key(self):
        """Test MetadataError with key information."""
        error = MetadataError(
            "Missing key",
            file="metadata.yaml",
            key="title"
        )
        assert "metadata.yaml" in str(error)
        assert "title" in str(error)
        assert error.key == "title"


class TestSessionError:
    """Test SessionError exception."""
    
    def test_basic_error(self):
        """Test basic SessionError."""
        with pytest.raises(SessionError):
            raise SessionError("Session error")
    
    def test_error_with_state(self):
        """Test SessionError with state information."""
        error = SessionError(
            "Invalid state",
            state="initialized"
        )
        assert "initialized" in str(error)
        assert error.state == "initialized"
    
    def test_error_with_expected_state(self):
        """Test SessionError with expected state."""
        error = SessionError(
            "Wrong state",
            state="initialized",
            expected_state="table_defined"
        )
        assert "initialized" in str(error)
        assert "table_defined" in str(error)
        assert error.expected_state == "table_defined"


class TestValidateRequiredColumns:
    """Test validate_required_columns function."""
    
    def test_valid_columns(self):
        """Test validation passes with all required columns present."""
        df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': [4, 5, 6],
            'C': [7, 8, 9]
        })
        # Should not raise any exception
        validate_required_columns(df, ['A', 'B', 'C'])
    
    def test_missing_single_column(self):
        """Test validation fails with one missing column."""
        df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': [4, 5, 6]
        })
        with pytest.raises(DataValidationError) as exc_info:
            validate_required_columns(df, ['A', 'B', 'C'])
        
        assert 'C' in str(exc_info.value)
        assert 'Missing required columns' in str(exc_info.value)
    
    def test_missing_multiple_columns(self):
        """Test validation fails with multiple missing columns."""
        df = pd.DataFrame({
            'A': [1, 2, 3]
        })
        with pytest.raises(DataValidationError) as exc_info:
            validate_required_columns(df, ['A', 'B', 'C', 'D'])
        
        error_msg = str(exc_info.value)
        assert 'B' in error_msg
        assert 'C' in error_msg
        assert 'D' in error_msg
    
    def test_custom_dataset_name(self):
        """Test validation with custom dataset name."""
        df = pd.DataFrame({'A': [1, 2, 3]})
        with pytest.raises(DataValidationError) as exc_info:
            validate_required_columns(df, ['B'], dataset_name='ADSL')
        
        assert 'ADSL' in str(exc_info.value)
    
    def test_empty_required_list(self):
        """Test validation passes with empty required columns list."""
        df = pd.DataFrame({'A': [1, 2, 3]})
        # Should not raise any exception
        validate_required_columns(df, [])

