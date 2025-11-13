"""
Pytest configuration and shared fixtures for py4csr tests.

This module provides common fixtures and configuration for all tests.
"""

import os
import sys
from pathlib import Path

import pandas as pd
import pytest

# Add py4csr to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_adsl():
    """
    Create a sample ADSL (Subject-Level Analysis Dataset) for testing.
    
    Returns
    -------
    pandas.DataFrame
        Sample ADSL dataset with typical clinical trial subject data
    """
    return pd.DataFrame({
        'STUDYID': ['STUDY001'] * 10,
        'USUBJID': [f'SUBJ{i:03d}' for i in range(1, 11)],
        'SUBJID': [f'{i:03d}' for i in range(1, 11)],
        'SITEID': ['001', '001', '002', '002', '003', '003', '004', '004', '005', '005'],
        'AGE': [45, 52, 38, 61, 29, 55, 48, 42, 67, 34],
        'AGEGR1': ['45-64', '45-64', '18-44', '>=65', '18-44', '45-64', '45-64', '45-64', '>=65', '18-44'],
        'SEX': ['M', 'F', 'M', 'F', 'M', 'F', 'M', 'F', 'M', 'F'],
        'RACE': ['WHITE', 'WHITE', 'BLACK', 'WHITE', 'ASIAN', 'WHITE', 'BLACK', 'WHITE', 'WHITE', 'ASIAN'],
        'ETHNIC': ['NOT HISPANIC', 'NOT HISPANIC', 'HISPANIC', 'NOT HISPANIC', 'NOT HISPANIC', 
                   'HISPANIC', 'NOT HISPANIC', 'NOT HISPANIC', 'NOT HISPANIC', 'HISPANIC'],
        'ARM': ['Placebo', 'Treatment A', 'Placebo', 'Treatment A', 'Treatment B',
                'Placebo', 'Treatment A', 'Treatment B', 'Placebo', 'Treatment A'],
        'TRT01P': ['Placebo', 'Treatment A', 'Placebo', 'Treatment A', 'Treatment B',
                   'Placebo', 'Treatment A', 'Treatment B', 'Placebo', 'Treatment A'],
        'TRT01PN': [0, 1, 0, 1, 2, 0, 1, 2, 0, 1],
        'SAFFL': ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
        'ITTFL': ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
        'EFFFL': ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'N', 'Y'],
        'COMP24FL': ['Y', 'Y', 'Y', 'N', 'Y', 'Y', 'Y', 'Y', 'N', 'Y'],
        'DTHFL': ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'Y', 'N'],
    })


@pytest.fixture
def sample_adae():
    """
    Create a sample ADAE (Adverse Events Analysis Dataset) for testing.
    
    Returns
    -------
    pandas.DataFrame
        Sample ADAE dataset with typical adverse event data
    """
    return pd.DataFrame({
        'STUDYID': ['STUDY001'] * 15,
        'USUBJID': ['SUBJ001', 'SUBJ001', 'SUBJ002', 'SUBJ003', 'SUBJ003', 'SUBJ004', 
                    'SUBJ005', 'SUBJ006', 'SUBJ007', 'SUBJ007', 'SUBJ008', 'SUBJ009', 
                    'SUBJ009', 'SUBJ010', 'SUBJ010'],
        'AEDECOD': ['Headache', 'Nausea', 'Headache', 'Dizziness', 'Fatigue', 'Nausea',
                    'Headache', 'Rash', 'Headache', 'Nausea', 'Dizziness', 'Fatigue',
                    'Headache', 'Nausea', 'Rash'],
        'AEBODSYS': ['Nervous system disorders', 'Gastrointestinal disorders', 
                     'Nervous system disorders', 'Nervous system disorders',
                     'General disorders', 'Gastrointestinal disorders',
                     'Nervous system disorders', 'Skin disorders',
                     'Nervous system disorders', 'Gastrointestinal disorders',
                     'Nervous system disorders', 'General disorders',
                     'Nervous system disorders', 'Gastrointestinal disorders', 'Skin disorders'],
        'AESEV': ['MILD', 'MODERATE', 'MILD', 'MILD', 'MODERATE', 'SEVERE',
                  'MILD', 'MILD', 'MODERATE', 'MILD', 'MILD', 'MODERATE',
                  'MILD', 'MODERATE', 'MILD'],
        'AESER': ['N', 'N', 'N', 'N', 'N', 'Y', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N'],
        'AEREL': ['RELATED', 'RELATED', 'NOT RELATED', 'RELATED', 'RELATED', 'RELATED',
                  'NOT RELATED', 'RELATED', 'RELATED', 'RELATED', 'NOT RELATED', 'RELATED',
                  'RELATED', 'RELATED', 'NOT RELATED'],
        'AOCCFL': ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
        'TRTA': ['Placebo', 'Placebo', 'Treatment A', 'Placebo', 'Placebo', 'Treatment A',
                 'Treatment B', 'Treatment A', 'Treatment B', 'Treatment B', 'Treatment A', 'Placebo',
                 'Placebo', 'Treatment A', 'Treatment A'],
        'TRTAN': [0, 0, 1, 0, 0, 1, 2, 1, 2, 2, 1, 0, 0, 1, 1],
        'AEOUT': ['RECOVERED', 'RECOVERED', 'RECOVERED', 'RECOVERED', 'RECOVERING', 'RECOVERED',
                  'RECOVERED', 'RECOVERED', 'RECOVERED', 'RECOVERED', 'RECOVERED', 'RECOVERING',
                  'RECOVERED', 'RECOVERED', 'RECOVERED'],
        'TRTEMFL': ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
        'TRT01P': ['Placebo', 'Placebo', 'Treatment A', 'Placebo', 'Placebo', 'Treatment A',
                   'Treatment B', 'Placebo', 'Treatment A', 'Treatment A', 'Treatment B',
                   'Placebo', 'Placebo', 'Treatment A', 'Treatment A'],
        'TRT01PN': [0, 0, 1, 0, 0, 1, 2, 0, 1, 1, 2, 0, 0, 1, 1],
    })


@pytest.fixture
def sample_adlb():
    """
    Create a sample ADLB (Laboratory Analysis Dataset) for testing.
    
    Returns
    -------
    pandas.DataFrame
        Sample ADLB dataset with typical laboratory data
    """
    return pd.DataFrame({
        'STUDYID': ['STUDY001'] * 20,
        'USUBJID': ['SUBJ001', 'SUBJ001', 'SUBJ002', 'SUBJ002', 'SUBJ003', 'SUBJ003',
                    'SUBJ004', 'SUBJ004', 'SUBJ005', 'SUBJ005', 'SUBJ006', 'SUBJ006',
                    'SUBJ007', 'SUBJ007', 'SUBJ008', 'SUBJ008', 'SUBJ009', 'SUBJ009',
                    'SUBJ010', 'SUBJ010'],
        'PARAM': ['Hemoglobin', 'Hemoglobin', 'Hemoglobin', 'Hemoglobin', 'Hemoglobin', 'Hemoglobin',
                  'Glucose', 'Glucose', 'Glucose', 'Glucose', 'Glucose', 'Glucose',
                  'Creatinine', 'Creatinine', 'Creatinine', 'Creatinine', 'Creatinine', 'Creatinine',
                  'ALT', 'ALT'],
        'PARAMCD': ['HGB', 'HGB', 'HGB', 'HGB', 'HGB', 'HGB',
                    'GLUC', 'GLUC', 'GLUC', 'GLUC', 'GLUC', 'GLUC',
                    'CREAT', 'CREAT', 'CREAT', 'CREAT', 'CREAT', 'CREAT',
                    'ALT', 'ALT'],
        'AVAL': [14.2, 14.5, 13.8, 14.1, 15.2, 15.0, 95, 98, 102, 105, 88, 92,
                 0.9, 0.95, 1.1, 1.05, 0.85, 0.88, 25, 28],
        'BASE': [14.2, 14.2, 13.8, 13.8, 15.2, 15.2, 95, 95, 102, 102, 88, 88,
                 0.9, 0.9, 1.1, 1.1, 0.85, 0.85, 25, 25],
        'CHG': [0, 0.3, 0, 0.3, 0, -0.2, 0, 3, 0, 3, 0, 4, 0, 0.05, 0, -0.05, 0, 0.03, 0, 3],
        'AVISITN': [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        'AVISIT': ['Baseline', 'Week 4', 'Baseline', 'Week 4', 'Baseline', 'Week 4',
                   'Baseline', 'Week 4', 'Baseline', 'Week 4', 'Baseline', 'Week 4',
                   'Baseline', 'Week 4', 'Baseline', 'Week 4', 'Baseline', 'Week 4',
                   'Baseline', 'Week 4'],
        'TRT01P': ['Placebo', 'Placebo', 'Treatment A', 'Treatment A', 'Placebo', 'Placebo',
                   'Treatment A', 'Treatment A', 'Treatment B', 'Treatment B', 'Placebo', 'Placebo',
                   'Treatment A', 'Treatment A', 'Treatment B', 'Treatment B', 'Placebo', 'Placebo',
                   'Treatment A', 'Treatment A'],
        'TRT01PN': [0, 0, 1, 1, 0, 0, 1, 1, 2, 2, 0, 0, 1, 1, 2, 2, 0, 0, 1, 1],
        'ANRLO': [12.0, 12.0, 12.0, 12.0, 12.0, 12.0, 70, 70, 70, 70, 70, 70,
                  0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 10, 10],
        'ANRHI': [16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 110, 110, 110, 110, 110, 110,
                  1.2, 1.2, 1.2, 1.2, 1.2, 1.2, 40, 40],
    })


@pytest.fixture
def temp_output_dir(tmp_path):
    """
    Create a temporary directory for test outputs.
    
    Parameters
    ----------
    tmp_path : pathlib.Path
        Pytest's built-in temporary directory fixture
    
    Returns
    -------
    pathlib.Path
        Path to temporary output directory
    """
    output_dir = tmp_path / "outputs"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def sample_metadata():
    """
    Create sample metadata for testing.
    
    Returns
    -------
    dict
        Sample metadata dictionary
    """
    return {
        'title': 'Test Clinical Table',
        'footnote': 'Test footnote for clinical table',
        'program': 'test_program.py',
        'output': 'test_output.rtf',
        'population': 'Safety Population',
        'dataset': 'ADSL',
    }


@pytest.fixture(autouse=True)
def reset_environment():
    """
    Reset environment variables before each test.
    
    This fixture runs automatically before each test to ensure
    a clean environment.
    """
    # Store original environment
    original_env = os.environ.copy()
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "real_data: marks tests that require real clinical data"
    )

