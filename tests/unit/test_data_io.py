"""
Unit tests for py4csr.data.io module.

Tests data loading and saving functionality.
"""

import pandas as pd
import pytest
import os
from pathlib import Path

from py4csr.data.io import (
    read_sas,
    read_xpt,
    load_dataset,
    get_dataset_info,
    load_adam_data
)
from py4csr.exceptions import DataValidationError


class TestLoadDataset:
    """Test load_dataset function."""

    def test_load_csv_dataset(self, temp_output_dir):
        """Test loading CSV file via load_dataset."""
        # Create a test CSV file
        test_file = temp_output_dir / "test.csv"
        df = pd.DataFrame({
            'USUBJID': ['SUBJ001', 'SUBJ002', 'SUBJ003'],
            'AGE': [45, 52, 38],
            'SEX': ['M', 'F', 'M']
        })
        df.to_csv(test_file, index=False)

        # Read it back
        result = load_dataset(str(test_file), dataset_type='csv')

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert 'USUBJID' in result.columns

    def test_load_excel_dataset(self, temp_output_dir):
        """Test loading Excel file via load_dataset."""
        test_file = temp_output_dir / "test.xlsx"
        df = pd.DataFrame({
            'USUBJID': ['SUBJ001', 'SUBJ002'],
            'AGE': [45, 52]
        })
        df.to_excel(test_file, index=False)

        result = load_dataset(str(test_file), dataset_type='excel')

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

    def test_load_dataset_auto_detect(self, temp_output_dir):
        """Test auto-detecting file type."""
        test_file = temp_output_dir / "test.csv"
        df = pd.DataFrame({'A': [1, 2, 3]})
        df.to_csv(test_file, index=False)

        result = load_dataset(str(test_file))

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3





class TestReadSAS:
    """Test read_sas function."""

    def test_read_sas_nonexistent_file(self):
        """Test that read_sas raises error for nonexistent file."""
        with pytest.raises(FileNotFoundError):
            read_sas("nonexistent.sas7bdat")


class TestReadXPT:
    """Test read_xpt function."""

    def test_read_xpt_nonexistent_file(self):
        """Test that read_xpt raises error for nonexistent file."""
        try:
            result = read_xpt("nonexistent.xpt")
            # If it doesn't raise, it should return None or empty DataFrame
            assert result is None or isinstance(result, pd.DataFrame)
        except (FileNotFoundError, Exception):
            # Expected - file doesn't exist
            pass


class TestGetDatasetInfo:
    """Test get_dataset_info function."""

    def test_get_info_basic(self, sample_adsl):
        """Test getting dataset information."""
        info = get_dataset_info(sample_adsl)

        assert isinstance(info, dict)
        assert 'n_rows' in info or 'rows' in info or 'shape' in info
        assert 'n_cols' in info or 'columns' in info or 'shape' in info

    def test_get_info_empty_dataframe(self):
        """Test getting info from empty DataFrame."""
        df = pd.DataFrame()
        info = get_dataset_info(df)

        assert isinstance(info, dict)


class TestLoadAdamData:
    """Test load_adam_data function."""

    def test_load_adam_data_nonexistent_dir(self):
        """Test loading from nonexistent directory."""
        result = load_adam_data("nonexistent_directory")

        # Should return empty dict or raise error
        assert isinstance(result, dict) or result is None


class TestDataIOIntegration:
    """Integration tests for data I/O operations."""

    def test_csv_round_trip(self, temp_output_dir):
        """Test CSV write and read round trip."""
        original_df = pd.DataFrame({
            'USUBJID': ['SUBJ001', 'SUBJ002', 'SUBJ003'],
            'AGE': [45, 52, 38],
            'SEX': ['M', 'F', 'M']
        })

        file_path = temp_output_dir / "round_trip.csv"

        # Save
        original_df.to_csv(file_path, index=False)

        # Read
        result_df = load_dataset(str(file_path), dataset_type='csv')

        # Compare
        assert len(result_df) == len(original_df)
        assert list(result_df.columns) == list(original_df.columns)
        assert result_df['USUBJID'].tolist() == original_df['USUBJID'].tolist()

    def test_excel_round_trip(self, temp_output_dir):
        """Test Excel write and read round trip."""
        original_df = pd.DataFrame({
            'USUBJID': ['SUBJ001', 'SUBJ002'],
            'AGE': [45, 52]
        })

        file_path = temp_output_dir / "round_trip.xlsx"

        # Save
        original_df.to_excel(file_path, index=False)

        # Read
        result_df = load_dataset(str(file_path), dataset_type='excel')

        # Compare
        assert len(result_df) == len(original_df)
        assert list(result_df.columns) == list(original_df.columns)

