"""
Unit tests for py4csr.data.preprocessing module.

Tests data preprocessing utilities.
"""

import pandas as pd
import pytest
import numpy as np

from py4csr.data.preprocessing import (
    apply_formats,
    handle_missing_data,
    derive_variables,
    clean_data,
)


class TestApplyFormats:
    """Test apply_formats function."""

    def test_date_format(self):
        """Test applying date format."""
        data = pd.DataFrame({
            "USUBJID": ["001", "002"],
            "RFSTDTC": ["2023-01-15", "2023-02-20"],
        })

        format_dict = {"RFSTDTC": "date"}
        result = apply_formats(data, format_dict)

        assert pd.api.types.is_datetime64_any_dtype(result["RFSTDTC"])

    def test_numeric_format(self):
        """Test applying numeric format."""
        data = pd.DataFrame({
            "USUBJID": ["001", "002"],
            "AGE": ["65", "70"],
        })

        format_dict = {"AGE": "numeric"}
        result = apply_formats(data, format_dict)

        assert pd.api.types.is_numeric_dtype(result["AGE"])
        assert result["AGE"].tolist() == [65.0, 70.0]

    def test_categorical_format(self):
        """Test applying categorical format."""
        data = pd.DataFrame({
            "USUBJID": ["001", "002", "003"],
            "SEX": ["M", "F", "M"],
        })

        format_dict = {"SEX": "categorical"}
        result = apply_formats(data, format_dict)

        assert pd.api.types.is_categorical_dtype(result["SEX"])

    def test_multiple_formats(self):
        """Test applying multiple formats."""
        data = pd.DataFrame({
            "USUBJID": ["001", "002"],
            "AGE": ["65", "70"],
            "SEX": ["M", "F"],
            "RFSTDTC": ["2023-01-15", "2023-02-20"],
        })

        format_dict = {
            "AGE": "numeric",
            "SEX": "categorical",
            "RFSTDTC": "date",
        }
        result = apply_formats(data, format_dict)

        assert pd.api.types.is_numeric_dtype(result["AGE"])
        assert pd.api.types.is_categorical_dtype(result["SEX"])
        assert pd.api.types.is_datetime64_any_dtype(result["RFSTDTC"])

    def test_nonexistent_column(self):
        """Test format for nonexistent column."""
        data = pd.DataFrame({"USUBJID": ["001", "002"]})

        format_dict = {"AGE": "numeric"}
        result = apply_formats(data, format_dict)

        # Should not raise error, just skip the column
        assert "AGE" not in result.columns


class TestHandleMissingData:
    """Test handle_missing_data function."""

    def test_listwise_deletion(self, capsys):
        """Test listwise deletion strategy."""
        data = pd.DataFrame({
            "USUBJID": ["001", "002", "003"],
            "AGE": [65, np.nan, 70],
            "SEX": ["M", "F", "M"],
        })

        result = handle_missing_data(data, strategy="listwise")

        assert len(result) == 2
        assert "002" not in result["USUBJID"].values
        
        # Check that message was printed
        captured = capsys.readouterr()
        assert "Listwise deletion" in captured.out

    def test_pairwise_deletion(self, capsys):
        """Test pairwise deletion strategy."""
        data = pd.DataFrame({
            "USUBJID": ["001", "002", "003"],
            "AGE": [65, np.nan, 70],
        })

        result = handle_missing_data(data, strategy="pairwise")

        # Should keep all data
        assert len(result) == 3
        
        # Check that message was printed
        captured = capsys.readouterr()
        assert "Pairwise deletion" in captured.out

    def test_impute_with_fill_values(self):
        """Test imputation with specified fill values."""
        data = pd.DataFrame({
            "USUBJID": ["001", "002", "003"],
            "AGE": [65, np.nan, 70],
            "SEX": ["M", np.nan, "F"],
        })

        fill_values = {"AGE": 0, "SEX": "Unknown"}
        result = handle_missing_data(data, strategy="impute", fill_values=fill_values)

        assert result["AGE"].iloc[1] == 0
        assert result["SEX"].iloc[1] == "Unknown"

    def test_impute_default(self):
        """Test default imputation strategy."""
        data = pd.DataFrame({
            "USUBJID": ["001", "002", "003", "004"],
            "AGE": [65, np.nan, 70, 75],
            "SEX": ["M", np.nan, "F", "M"],
        })

        result = handle_missing_data(data, strategy="impute")

        # Numeric should be filled with median
        assert result["AGE"].iloc[1] == 70.0  # median of [65, 70, 75]
        # Categorical should be filled with mode
        assert result["SEX"].iloc[1] == "M"  # mode of ["M", "F", "M"]

    def test_forward_fill(self):
        """Test forward fill strategy."""
        data = pd.DataFrame({
            "USUBJID": ["001", "002", "003"],
            "AGE": [65, np.nan, 70],
        })

        result = handle_missing_data(data, strategy="forward_fill")

        assert result["AGE"].iloc[1] == 65  # Forward filled from row 0

    def test_invalid_strategy(self):
        """Test invalid strategy raises error."""
        data = pd.DataFrame({"USUBJID": ["001"]})

        with pytest.raises(ValueError, match="Unknown missing data strategy"):
            handle_missing_data(data, strategy="invalid_strategy")


class TestDeriveVariables:
    """Test derive_variables function."""

    def test_simple_derivation(self):
        """Test simple variable derivation."""
        data = pd.DataFrame({
            "USUBJID": ["001", "002"],
            "AGE": [65, 70],
        })

        derivations = {"AGE_PLUS_10": "AGE + 10"}
        result = derive_variables(data, derivations)

        assert "AGE_PLUS_10" in result.columns
        assert result["AGE_PLUS_10"].tolist() == [75, 80]

    def test_multiple_derivations(self):
        """Test multiple variable derivations."""
        data = pd.DataFrame({
            "USUBJID": ["001", "002"],
            "AGE": [65, 70],
            "WEIGHT": [70, 80],
        })

        derivations = {
            "AGE_PLUS_WEIGHT": "AGE + WEIGHT",
            "WEIGHT_TIMES_2": "WEIGHT * 2",
        }
        result = derive_variables(data, derivations)

        assert "AGE_PLUS_WEIGHT" in result.columns
        assert "WEIGHT_TIMES_2" in result.columns
        assert result["AGE_PLUS_WEIGHT"].iloc[0] == 135
        assert result["WEIGHT_TIMES_2"].iloc[0] == 140

    def test_conditional_derivation(self):
        """Test conditional derivation."""
        data = pd.DataFrame({
            "USUBJID": ["001", "002", "003"],
            "AGE": [60, 70, 80],
        })

        derivations = {"AGEGR1": "AGE >= 65"}
        result = derive_variables(data, derivations)

        assert "AGEGR1" in result.columns
        assert result["AGEGR1"].tolist() == [False, True, True]

    def test_invalid_derivation(self, capsys):
        """Test invalid derivation expression."""
        data = pd.DataFrame({"USUBJID": ["001"]})

        derivations = {"NEW_VAR": "NONEXISTENT_COL + 10"}
        result = derive_variables(data, derivations)

        # Should print warning but not raise error
        captured = capsys.readouterr()
        assert "Warning" in captured.out
        assert "Could not derive" in captured.out


class TestCleanData:
    """Test clean_data function."""

    def test_remove_duplicates(self, capsys):
        """Test removing duplicate rows."""
        data = pd.DataFrame({
            "USUBJID": ["001", "002", "001"],
            "AGE": [65, 70, 65],
        })

        result = clean_data(data, remove_duplicates=True, standardize_columns=False)

        assert len(result) == 2
        
        # Check that message was printed
        captured = capsys.readouterr()
        assert "Removed 1 duplicate rows" in captured.out

    def test_standardize_columns(self):
        """Test standardizing column names."""
        data = pd.DataFrame({
            "usubjid": ["001", "002"],
            "age ": [65, 70],
            "Sex": ["M", "F"],
        })

        result = clean_data(data, remove_duplicates=False, standardize_columns=True)

        assert "USUBJID" in result.columns
        assert "AGE" in result.columns
        assert "SEX" in result.columns

    def test_convert_string_na(self):
        """Test converting string NA values to NaN."""
        data = pd.DataFrame({
            "USUBJID": ["001", "002", "003", "004", "005", "006", "007"],
            "SEX": ["M", "", " ", "NA", "N/A", "NULL", "Missing"],
        })

        result = clean_data(data, remove_duplicates=False, standardize_columns=False)

        # All string NA values should be converted to NaN
        assert pd.isna(result["SEX"].iloc[1])
        assert pd.isna(result["SEX"].iloc[2])
        assert pd.isna(result["SEX"].iloc[3])
        assert pd.isna(result["SEX"].iloc[4])
        assert pd.isna(result["SEX"].iloc[5])
        assert pd.isna(result["SEX"].iloc[6])

    def test_full_cleaning(self, capsys):
        """Test full cleaning with all options."""
        data = pd.DataFrame({
            "usubjid": ["001", "002", "001", "003"],
            "age": [65, 70, 65, 75],
            "sex": ["M", "F", "M", "NA"],
        })

        result = clean_data(data, remove_duplicates=True, standardize_columns=True)

        # Should remove duplicates
        assert len(result) == 3
        
        # Should standardize columns
        assert "USUBJID" in result.columns
        assert "AGE" in result.columns
        assert "SEX" in result.columns
        
        # Should convert NA to NaN
        assert pd.isna(result["SEX"].iloc[2])
        
        # Check that message was printed
        captured = capsys.readouterr()
        assert "Removed 1 duplicate rows" in captured.out

    def test_no_duplicates(self):
        """Test when there are no duplicates."""
        data = pd.DataFrame({
            "USUBJID": ["001", "002", "003"],
            "AGE": [65, 70, 75],
        })

        result = clean_data(data, remove_duplicates=True, standardize_columns=False)

        assert len(result) == 3

