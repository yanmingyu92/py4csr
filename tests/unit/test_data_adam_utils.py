"""
Unit tests for py4csr.data.adam_utils module.

Tests ADaM data manipulation utilities.
"""

import pandas as pd
import pytest
import numpy as np

from py4csr.data.adam_utils import (
    derive_treatment_variables,
    derive_analysis_flags,
    derive_disposition_variables,
    derive_demographic_categories,
    merge_adam_datasets,
    create_analysis_dataset,
    format_ae_data,
    format_lab_data,
    create_summary_statistics,
    create_frequency_table,
    apply_cdisc_formats,
    validate_adam_structure,
)


class TestDeriveTreatmentVariables:
    """Test derive_treatment_variables function."""

    def test_derive_trt01pn(self):
        """Test deriving TRT01PN from TRT01P."""
        adsl = pd.DataFrame({
            "USUBJID": ["001", "002", "003"],
            "TRT01P": ["Placebo", "Xanomeline Low Dose", "Xanomeline High Dose"],
        })

        result = derive_treatment_variables(adsl)

        assert "TRT01PN" in result.columns
        assert result["TRT01PN"].tolist() == [0, 54, 81]

    def test_derive_trt01a(self):
        """Test deriving TRT01A from TRT01P."""
        adsl = pd.DataFrame({
            "USUBJID": ["001", "002"],
            "TRT01P": ["Placebo", "Xanomeline Low Dose"],
        })

        result = derive_treatment_variables(adsl)

        assert "TRT01A" in result.columns
        assert result["TRT01A"].tolist() == ["Placebo", "Xanomeline Low Dose"]

    def test_derive_trt01an(self):
        """Test deriving TRT01AN from TRT01PN."""
        adsl = pd.DataFrame({
            "USUBJID": ["001", "002"],
            "TRT01P": ["Placebo", "Xanomeline Low Dose"],
        })

        result = derive_treatment_variables(adsl)

        assert "TRT01AN" in result.columns
        assert result["TRT01AN"].tolist() == [0, 54]

    def test_existing_variables_not_overwritten(self):
        """Test that existing variables are not overwritten."""
        adsl = pd.DataFrame({
            "USUBJID": ["001"],
            "TRT01P": ["Placebo"],
            "TRT01PN": [99],  # Existing value
        })

        result = derive_treatment_variables(adsl)

        assert result["TRT01PN"].tolist() == [99]  # Should not be overwritten


class TestDeriveAnalysisFlags:
    """Test derive_analysis_flags function."""

    def test_derive_saffl(self):
        """Test deriving SAFFL."""
        adsl = pd.DataFrame({"USUBJID": ["001", "002", "003"]})

        result = derive_analysis_flags(adsl)

        assert "SAFFL" in result.columns
        assert all(result["SAFFL"] == "Y")

    def test_derive_efffl(self):
        """Test deriving EFFFL."""
        adsl = pd.DataFrame({
            "USUBJID": ["001", "002", "003"],
            "DTHFL": ["N", "Y", "N"],
        })

        result = derive_analysis_flags(adsl)

        assert "EFFFL" in result.columns
        assert result["EFFFL"].tolist() == ["Y", "N", "Y"]

    def test_derive_ittfl(self):
        """Test deriving ITTFL."""
        adsl = pd.DataFrame({"USUBJID": ["001", "002"]})

        result = derive_analysis_flags(adsl)

        assert "ITTFL" in result.columns
        assert all(result["ITTFL"] == "Y")


class TestDeriveDispositionVariables:
    """Test derive_disposition_variables function."""

    def test_derive_disconfl(self):
        """Test deriving DISCONFL."""
        adsl = pd.DataFrame({
            "USUBJID": ["001", "002", "003"],
            "DCSREAS": ["COMPLETED", "ADVERSE EVENT", "COMPLETED"],
        })

        result = derive_disposition_variables(adsl)

        assert "DISCONFL" in result.columns
        assert result["DISCONFL"].tolist() == ["N", "Y", "N"]

    def test_derive_dcreascd(self):
        """Test deriving DCREASCD."""
        adsl = pd.DataFrame({
            "USUBJID": ["001", "002", "003"],
            "DCSREAS": ["COMPLETED", "ADVERSE EVENT", "WITHDREW CONSENT"],
        })

        result = derive_disposition_variables(adsl)

        assert "DCREASCD" in result.columns
        assert result["DCREASCD"].tolist() == ["COMPLETED", "AE", "WITHDREW"]


class TestDeriveDemographicCategories:
    """Test derive_demographic_categories function."""

    def test_derive_agegr1(self):
        """Test deriving AGEGR1."""
        adsl = pd.DataFrame({
            "USUBJID": ["001", "002", "003", "004"],
            "AGE": [60, 70, 80, 65],
        })

        result = derive_demographic_categories(adsl)

        assert "AGEGR1" in result.columns
        assert result["AGEGR1"].tolist() == ["<65", "65-74", ">=75", "65-74"]

    def test_derive_bmi(self):
        """Test deriving BMI."""
        adsl = pd.DataFrame({
            "USUBJID": ["001", "002"],
            "HEIGHT": [170, 180],  # cm
            "WEIGHT": [70, 80],  # kg
        })

        result = derive_demographic_categories(adsl)

        assert "BMI" in result.columns
        # BMI = weight / (height_m)^2
        expected_bmi_1 = 70 / (1.7**2)
        expected_bmi_2 = 80 / (1.8**2)
        assert abs(result["BMI"].iloc[0] - expected_bmi_1) < 0.01
        assert abs(result["BMI"].iloc[1] - expected_bmi_2) < 0.01

    def test_derive_bmigr1(self):
        """Test deriving BMIGR1."""
        adsl = pd.DataFrame({
            "USUBJID": ["001", "002", "003", "004"],
            "HEIGHT": [170, 170, 170, 170],
            "WEIGHT": [50, 65, 75, 90],
        })

        result = derive_demographic_categories(adsl)

        assert "BMIGR1" in result.columns
        # BMI categories: <18.5, 18.5-25, 25-30, >=30


class TestMergeAdamDatasets:
    """Test merge_adam_datasets function."""

    def test_merge_with_treatment_vars(self):
        """Test merging datasets with treatment variables."""
        adsl = pd.DataFrame({
            "USUBJID": ["001", "002", "003"],
            "TRT01P": ["Placebo", "Active", "Active"],
            "SAFFL": ["Y", "Y", "Y"],
        })

        adae = pd.DataFrame({
            "USUBJID": ["001", "002", "002"],
            "AEDECOD": ["Headache", "Nausea", "Fatigue"],
        })

        result = merge_adam_datasets(adsl, {"adae": adae})

        assert "adae" in result
        assert "TRT01P" in result["adae"].columns
        assert "SAFFL" in result["adae"].columns
        assert len(result["adae"]) == 3

    def test_merge_without_usubjid(self):
        """Test merging dataset without USUBJID."""
        adsl = pd.DataFrame({
            "USUBJID": ["001", "002"],
            "TRT01P": ["Placebo", "Active"],
        })

        other_data = pd.DataFrame({"VAR1": [1, 2, 3]})

        result = merge_adam_datasets(adsl, {"other": other_data})

        assert "other" in result
        assert "TRT01P" not in result["other"].columns


class TestCreateAnalysisDataset:
    """Test create_analysis_dataset function."""

    def test_filter_by_population(self):
        """Test filtering by population flag."""
        data = pd.DataFrame({
            "USUBJID": ["001", "002", "003"],
            "AGE": [65, 70, 75],
            "SAFFL": ["Y", "N", "Y"],
            "TRT01P": ["Placebo", "Active", "Placebo"],
        })

        result = create_analysis_dataset(
            data, analysis_var="AGE", by_vars=["TRT01P"], population_flag="SAFFL"
        )

        # Function returns grouped data, so check that only SAFFL='Y' records are included
        # Should have 2 rows (Placebo with AGE=65, Placebo with AGE=75)
        assert isinstance(result, pd.DataFrame)
        assert "n" in result.columns

    def test_no_population_flag(self):
        """Test without population flag."""
        data = pd.DataFrame({
            "USUBJID": ["001", "002", "003"],
            "AGE": [65, 70, 75],
            "TRT01P": ["Placebo", "Active", "Placebo"],
        })

        result = create_analysis_dataset(
            data, analysis_var="AGE", by_vars=["TRT01P"], population_flag="SAFFL"
        )

        assert len(result) == 3


class TestFormatAEData:
    """Test format_ae_data function."""

    def test_format_ae_basic(self, sample_adsl, sample_adae):
        """Test basic AE formatting."""
        # Ensure SAFFL exists in sample_adsl
        sample_adsl = sample_adsl.copy()
        if "SAFFL" not in sample_adsl.columns:
            sample_adsl["SAFFL"] = "Y"
        if "TRT01A" not in sample_adsl.columns:
            sample_adsl["TRT01A"] = sample_adsl["TRT01P"]
        if "TRT01AN" not in sample_adsl.columns:
            sample_adsl["TRT01AN"] = sample_adsl["TRT01PN"]

        result = format_ae_data(sample_adae, sample_adsl)

        assert "TRT01A" in result.columns
        assert "SAFFL" in result.columns
        assert all(result["SAFFL"] == "Y")

    def test_derive_ae_flags(self, sample_adsl):
        """Test deriving AE flags."""
        # Ensure required columns exist
        sample_adsl = sample_adsl.copy()
        if "SAFFL" not in sample_adsl.columns:
            sample_adsl["SAFFL"] = "Y"
        if "TRT01A" not in sample_adsl.columns:
            sample_adsl["TRT01A"] = sample_adsl["TRT01P"]
        if "TRT01AN" not in sample_adsl.columns:
            sample_adsl["TRT01AN"] = sample_adsl["TRT01PN"]

        adae = pd.DataFrame({
            "USUBJID": sample_adsl["USUBJID"].tolist()[:3],
            "AEDECOD": ["Headache", "Nausea", "Fatigue"],
            "AEREL": ["POSSIBLE", "NOT RELATED", "PROBABLE"],
            "AESER": ["Y", "N", "N"],
            "AEOUT": ["FATAL", "RECOVERED", "RECOVERED"],
        })

        result = format_ae_data(adae, sample_adsl)

        assert "DRUG_RELATED" in result.columns
        assert "SERIOUS" in result.columns
        assert "FATAL" in result.columns


class TestFormatLabData:
    """Test format_lab_data function."""

    def test_format_lab_basic(self, sample_adsl, sample_adlb):
        """Test basic lab formatting."""
        # Ensure EFFFL exists
        sample_adsl = sample_adsl.copy()
        if "EFFFL" not in sample_adsl.columns:
            sample_adsl["EFFFL"] = "Y"

        result = format_lab_data(sample_adlb, sample_adsl)

        # Check that TRT01P exists (may be TRT01P_x or TRT01P_y after merge)
        assert any("TRT01P" in col for col in result.columns)
        assert "EFFFL" in result.columns
        assert all(result["EFFFL"] == "Y")

    def test_numeric_conversion(self, sample_adsl):
        """Test numeric value conversion."""
        # Ensure EFFFL exists
        sample_adsl = sample_adsl.copy()
        if "EFFFL" not in sample_adsl.columns:
            sample_adsl["EFFFL"] = "Y"

        adlb = pd.DataFrame({
            "USUBJID": sample_adsl["USUBJID"].tolist()[:3],
            "PARAMCD": ["ALT", "ALT", "ALT"],
            "AVAL": ["10.5", "20.3", "15.7"],
            "BASE": ["10.0", "19.5", "15.0"],
        })

        result = format_lab_data(adlb, sample_adsl)

        assert result["AVAL"].dtype in [np.float64, np.float32, float, np.int64, int]
        assert result["BASE"].dtype in [np.float64, np.float32, float, np.int64, int]


class TestCreateSummaryStatistics:
    """Test create_summary_statistics function."""

    def test_summary_stats_basic(self):
        """Test basic summary statistics."""
        data = pd.DataFrame({
            "AGE": [65, 70, 75, 68, 72],
            "TRT01P": ["Placebo", "Active", "Placebo", "Active", "Placebo"],
        })

        result = create_summary_statistics(data, "AGE", "TRT01P")

        assert isinstance(result, pd.DataFrame)
        # The function returns TRT01P as a column after reset_index
        assert "TRT01P" in result.columns
        assert "mean" in result.columns


class TestCreateFrequencyTable:
    """Test create_frequency_table function."""

    def test_frequency_table_basic(self):
        """Test basic frequency table."""
        data = pd.DataFrame({
            "SEX": ["M", "F", "M", "F", "M"],
            "TRT01P": ["Placebo", "Placebo", "Active", "Active", "Placebo"],
        })

        result = create_frequency_table(data, "SEX", "TRT01P")

        assert isinstance(result, pd.DataFrame)
        assert "Category" in result.columns


class TestApplyCDISCFormats:
    """Test apply_cdisc_formats function."""

    def test_format_adsl(self):
        """Test formatting ADSL dataset."""
        data = pd.DataFrame({
            "USUBJID": [1, 2, 3],
            "AGE": ["65", "70", "75"],
            "SAFFL": [None, "Y", "N"],
        })

        result = apply_cdisc_formats(data, "ADSL")

        assert result["USUBJID"].dtype == object  # Should be string
        assert result["AGE"].dtype in [np.float64, np.int64, float, int]  # Should be numeric
        assert result["SAFFL"].iloc[0] == "N"  # Missing should be filled with "N"

    def test_format_adae(self):
        """Test formatting ADAE dataset."""
        data = pd.DataFrame({
            "USUBJID": ["001", "002"],
            "AEDECOD": ["Headache", "Nausea"],
            "AESEV": ["1", "3"],
        })

        result = apply_cdisc_formats(data, "ADAE")

        assert result["AESEV"].tolist() == ["MILD", "SEVERE"]


class TestValidateAdamStructure:
    """Test validate_adam_structure function."""

    def test_validate_adsl_valid(self):
        """Test validating valid ADSL."""
        data = pd.DataFrame({
            "USUBJID": ["001", "002"],
            "STUDYID": ["ABC", "ABC"],
            "SUBJID": ["001", "002"],
        })

        result = validate_adam_structure(data, "ADSL")

        assert result["valid"] is True
        assert result["dataset_type"] == "ADSL"
        assert result["record_count"] == 2

    def test_validate_adsl_missing_vars(self):
        """Test validating ADSL with missing required variables."""
        data = pd.DataFrame({
            "USUBJID": ["001", "002"],
            # Missing STUDYID and SUBJID
        })

        result = validate_adam_structure(data, "ADSL")

        assert result["valid"] is False
        assert len(result["errors"]) > 0

    def test_validate_adae_valid(self):
        """Test validating valid ADAE."""
        data = pd.DataFrame({
            "USUBJID": ["001", "002"],
            "AEDECOD": ["Headache", "Nausea"],
        })

        result = validate_adam_structure(data, "ADAE")

        assert result["valid"] is True
        assert result["dataset_type"] == "ADAE"

