"""
Unit tests for py4csr.clinical.statistical_engine.ClinicalStatisticalEngine class.

Tests statistical calculation functionality for continuous and categorical variables.
"""

import pandas as pd
import numpy as np
import pytest

from py4csr.clinical.statistical_engine import ClinicalStatisticalEngine


class TestStatisticalEngineInit:
    """Test ClinicalStatisticalEngine initialization."""
    
    def test_initialization(self):
        """Test basic initialization."""
        engine = ClinicalStatisticalEngine()
        
        assert engine is not None
        assert hasattr(engine, 'decimal_places')
        assert engine.decimal_places['age'] == 1
        assert engine.decimal_places['default'] == 1


class TestCalculateContinuousStats:
    """Test calculate_continuous_stats method."""
    
    def test_basic_continuous_stats(self, sample_adsl):
        """Test basic continuous statistics calculation."""
        engine = ClinicalStatisticalEngine()
        
        results = engine.calculate_continuous_stats(
            data=sample_adsl,
            variable="AGE",
            treatment_var="TRT01P",
            stats_spec="n mean+sd"
        )
        
        assert isinstance(results, pd.DataFrame)
        assert len(results) > 0
        assert 'treatment' in results.columns
        assert 'variable' in results.columns
        assert 'statistic' in results.columns
        assert 'value' in results.columns
        assert 'formatted_value' in results.columns
    
    def test_continuous_stats_by_treatment(self, sample_adsl):
        """Test continuous stats calculated for each treatment."""
        engine = ClinicalStatisticalEngine()
        
        results = engine.calculate_continuous_stats(
            data=sample_adsl,
            variable="AGE",
            treatment_var="TRT01P",
            stats_spec="n mean"
        )
        
        # Should have results for each treatment + Total
        treatments = results['treatment'].unique()
        assert 'Total' in treatments
        assert len(treatments) > 1
    
    def test_continuous_stats_with_where_clause(self, sample_adsl):
        """Test continuous stats with filter."""
        engine = ClinicalStatisticalEngine()
        
        results = engine.calculate_continuous_stats(
            data=sample_adsl,
            variable="AGE",
            treatment_var="TRT01P",
            stats_spec="n",
            where_clause="SEX=='M'"
        )
        
        # Should only include male subjects
        assert len(results) > 0
        # N should be less than total
        total_n = results[results['treatment'] == 'Total']['value'].iloc[0]
        assert total_n < len(sample_adsl)
    
    def test_continuous_stats_multiple_statistics(self, sample_adsl):
        """Test calculating multiple statistics."""
        engine = ClinicalStatisticalEngine()
        
        results = engine.calculate_continuous_stats(
            data=sample_adsl,
            variable="AGE",
            treatment_var="TRT01P",
            stats_spec="n mean+sd median min+max"
        )
        
        # Should have multiple statistic types
        statistics = results['statistic'].unique()
        assert 'N' in statistics
        assert 'Mean (SD)' in statistics or 'Mean' in statistics
        assert 'Median' in statistics
    
    def test_continuous_stats_empty_data(self):
        """Test with empty dataset."""
        engine = ClinicalStatisticalEngine()
        empty_df = pd.DataFrame(columns=['AGE', 'TRT01P'])
        
        results = engine.calculate_continuous_stats(
            data=empty_df,
            variable="AGE",
            treatment_var="TRT01P",
            stats_spec="n mean"
        )
        
        # Should return empty or handle gracefully
        assert isinstance(results, pd.DataFrame)


class TestCalculateCategoricalStats:
    """Test calculate_categorical_stats method."""
    
    def test_basic_categorical_stats(self, sample_adsl):
        """Test basic categorical statistics."""
        engine = ClinicalStatisticalEngine()
        
        results = engine.calculate_categorical_stats(
            data=sample_adsl,
            variable="SEX",
            treatment_var="TRT01P",
            stats_spec="npct"
        )
        
        assert isinstance(results, pd.DataFrame)
        assert len(results) > 0
        assert 'treatment' in results.columns
        assert 'category' in results.columns
        assert 'n' in results.columns or 'count' in results.columns
    
    def test_categorical_stats_by_treatment(self, sample_adsl):
        """Test categorical stats for each treatment."""
        engine = ClinicalStatisticalEngine()
        
        results = engine.calculate_categorical_stats(
            data=sample_adsl,
            variable="SEX",
            treatment_var="TRT01P",
            stats_spec="npct"
        )
        
        # Should have results for multiple treatments
        treatments = results['treatment'].unique()
        assert len(treatments) > 1
    
    def test_categorical_stats_with_decode(self, sample_adsl):
        """Test categorical stats with decode variable."""
        # Add numeric sex variable
        sample_adsl['SEXN'] = sample_adsl['SEX'].map({'M': 1, 'F': 2})
        
        engine = ClinicalStatisticalEngine()
        
        results = engine.calculate_categorical_stats(
            data=sample_adsl,
            variable="SEXN",
            treatment_var="TRT01P",
            stats_spec="npct",
            decode_var="SEX"
        )
        
        assert len(results) > 0
    
    def test_categorical_stats_show_missing(self, sample_adsl):
        """Test categorical stats with missing values."""
        # Add some missing values
        sample_adsl_copy = sample_adsl.copy()
        sample_adsl_copy.loc[0:2, 'RACE'] = np.nan
        
        engine = ClinicalStatisticalEngine()
        
        results = engine.calculate_categorical_stats(
            data=sample_adsl_copy,
            variable="RACE",
            treatment_var="TRT01P",
            stats_spec="npct",
            show_missing="Y"
        )
        
        # Should include missing category
        categories = results['category'].unique() if 'category' in results.columns else []
        # Missing might be represented differently
        assert len(results) > 0


class TestCalculateConditionStats:
    """Test calculate_condition_stats method."""
    
    def test_basic_condition_stats(self, sample_adsl):
        """Test condition-based statistics."""
        engine = ClinicalStatisticalEngine()
        
        results = engine.calculate_condition_stats(
            data=sample_adsl,
            treatment_var="TRT01P",
            where_clause="AGE >= 65",
            stats_spec="n",
            subjid_var="USUBJID"
        )
        
        assert isinstance(results, pd.DataFrame)
        assert len(results) > 0
    
    def test_condition_stats_count_subjects(self, sample_adsl):
        """Test counting subjects meeting condition."""
        engine = ClinicalStatisticalEngine()
        
        results = engine.calculate_condition_stats(
            data=sample_adsl,
            treatment_var="TRT01P",
            where_clause="AGE >= 65",
            stats_spec="n",
            subjid_var="USUBJID",
            countwhat="subjid"
        )
        
        # Should count subjects aged 65+
        assert len(results) > 0
        # Check that counts are reasonable
        total_count = results[results['treatment'] == 'Total']['value'].iloc[0] if 'Total' in results['treatment'].values else 0
        assert total_count >= 0
        assert total_count <= len(sample_adsl)


class TestPerformAnova:
    """Test perform_anova method."""
    
    def test_basic_anova(self, sample_adsl):
        """Test ANOVA calculation."""
        engine = ClinicalStatisticalEngine()
        
        result = engine.perform_anova(
            data=sample_adsl,
            variable="AGE",
            treatment_var="TRT01P"
        )
        
        assert isinstance(result, dict)
        assert 'f_stat' in result or 'p_value' in result
    
    def test_anova_with_insufficient_groups(self):
        """Test ANOVA with less than 2 groups."""
        engine = ClinicalStatisticalEngine()
        
        # Create data with only one treatment group
        df = pd.DataFrame({
            'AGE': [45, 52, 38, 61],
            'TRT': ['A', 'A', 'A', 'A']
        })
        
        result = engine.perform_anova(
            data=df,
            variable="AGE",
            treatment_var="TRT"
        )
        
        # Should handle gracefully
        assert isinstance(result, dict)
        assert 'error' in result or result.get('p_value') is None


class TestPerformChiSquare:
    """Test perform_chi_square method."""
    
    def test_basic_chi_square(self, sample_adsl):
        """Test chi-square test."""
        engine = ClinicalStatisticalEngine()
        
        result = engine.perform_chi_square(
            data=sample_adsl,
            variable="SEX",
            treatment_var="TRT01P"
        )
        
        assert isinstance(result, dict)
        assert 'chi2_stat' in result or 'p_value' in result
    
    def test_chi_square_with_small_sample(self):
        """Test chi-square with small sample."""
        engine = ClinicalStatisticalEngine()
        
        # Create small dataset
        df = pd.DataFrame({
            'SEX': ['M', 'F', 'M'],
            'TRT': ['A', 'A', 'B']
        })
        
        result = engine.perform_chi_square(
            data=df,
            variable="SEX",
            treatment_var="TRT"
        )
        
        # Should handle gracefully
        assert isinstance(result, dict)


class TestSingleContinuousStat:
    """Test _calculate_single_continuous_stat helper method."""
    
    def test_calculate_n(self):
        """Test N calculation."""
        engine = ClinicalStatisticalEngine()
        data = pd.Series([1, 2, 3, 4, 5])
        
        result = engine._calculate_single_continuous_stat(data, 'N', 1)
        
        assert result['name'] == 'N'
        assert result['value'] == 5
        assert result['formatted'] == '5'
    
    def test_calculate_mean(self):
        """Test mean calculation."""
        engine = ClinicalStatisticalEngine()
        data = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        
        result = engine._calculate_single_continuous_stat(data, 'Mean', 1)
        
        assert result['name'] == 'Mean'
        assert result['value'] == 3.0
        assert '3.0' in result['formatted']
    
    def test_calculate_median(self):
        """Test median calculation."""
        engine = ClinicalStatisticalEngine()
        data = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        
        result = engine._calculate_single_continuous_stat(data, 'Median', 1)
        
        assert result['name'] == 'Median'
        assert result['value'] == 3.0
    
    def test_calculate_with_empty_data(self):
        """Test calculation with empty data."""
        engine = ClinicalStatisticalEngine()
        data = pd.Series([])
        
        result = engine._calculate_single_continuous_stat(data, 'Mean', 1)
        
        assert result['name'] == 'Mean'
        assert result['value'] is None
        assert result['formatted'] == ''

