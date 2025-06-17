"""
Standard clinical trial configuration for py4csr.

This module provides the default configuration for clinical study reports,
equivalent to the SAS RRG system's config.ini file.
"""

from .report_config import ReportConfig, StatisticConfig, PageSettings


def get_clinical_standard_config() -> ReportConfig:
    """
    Get standard clinical trial configuration.
    
    This configuration follows ICH E3 and CTD guidelines and provides
    standard statistical displays and formats used in clinical study reports.
    
    Returns
    -------
    ReportConfig
        Standard clinical configuration
    """
    
    # Statistical definitions (equivalent to [A1] section in SAS RRG)
    statistics = {
        'n': StatisticConfig(
            name='n',
            display='n',
            label='Number of subjects',
            precision=0
        ),
        'mean': StatisticConfig(
            name='mean',
            display='Mean',
            label='Mean',
            precision=1
        ),
        'std': StatisticConfig(
            name='std',
            display='SD',
            label='Standard Deviation',
            precision=2
        ),
        'stderr': StatisticConfig(
            name='stderr',
            display='SE',
            label='Standard Error',
            precision=2
        ),
        'mean_sd': StatisticConfig(
            name='mean_sd',
            display='Mean (SD)',
            label='Mean (Standard Deviation)',
            precision=1,
            format_func='format_mean_sd'
        ),
        'mean_se': StatisticConfig(
            name='mean_se',
            display='Mean (SE)',
            label='Mean (Standard Error)',
            precision=1,
            format_func='format_mean_se'
        ),
        'median': StatisticConfig(
            name='median',
            display='Median',
            label='Median',
            precision=1
        ),
        'min': StatisticConfig(
            name='min',
            display='Min',
            label='Minimum',
            precision=0
        ),
        'max': StatisticConfig(
            name='max',
            display='Max',
            label='Maximum',
            precision=0
        ),
        'min_max': StatisticConfig(
            name='min_max',
            display='Min, Max',
            label='Minimum, Maximum',
            precision=0,
            format_func='format_min_max'
        ),
        'q1': StatisticConfig(
            name='q1',
            display='Q1',
            label='First Quartile',
            precision=1
        ),
        'q3': StatisticConfig(
            name='q3',
            display='Q3',
            label='Third Quartile',
            precision=1
        ),
        'q1_q3': StatisticConfig(
            name='q1_q3',
            display='Q1, Q3',
            label='First and Third Quartiles',
            precision=1,
            format_func='format_q1_q3'
        ),
        'cv': StatisticConfig(
            name='cv',
            display='CV%',
            label='Coefficient of Variation (%)',
            precision=1
        ),
        'gmean': StatisticConfig(
            name='gmean',
            display='Geometric Mean',
            label='Geometric Mean',
            precision=2
        ),
        'nmiss': StatisticConfig(
            name='nmiss',
            display='Missing',
            label='Number of Missing Values',
            precision=0
        )
    }
    
    # Format definitions (equivalent to [A3], [A4] sections in SAS RRG)
    formats = {
        'percent': '({:.1f}%)',
        'percent_no_paren': '{:.1f}%',
        'pvalue': '<.0001',  # for p < 0.0001
        'pvalue_format': '{:.4f}',
        'confidence_interval': '({:.2f}, {:.2f})',
        'n_percent': '{} ({:.1f}%)',
        'mean_sd_format': '{:.1f} ({:.2f})',
        'mean_se_format': '{:.1f} ({:.2f})',
        'min_max_format': '{:.0f}, {:.0f}',
        'q1_q3_format': '{:.1f}, {:.1f}'
    }
    
    # Page settings (equivalent to [C1] section in SAS RRG)
    page_settings = PageSettings(
        orientation='portrait',
        margins={
            'top': 1.0,
            'bottom': 1.0,
            'left': 1.0,
            'right': 1.0
        },
        font_size=10,
        font_family='Times New Roman',
        col_width=6.5
    )
    
    # Template mappings
    templates = {
        'demographics': 'demographics_template',
        'disposition': 'disposition_template',
        'ae_summary': 'ae_summary_template',
        'ae_detail': 'ae_detail_template',
        'efficacy': 'efficacy_template',
        'laboratory': 'laboratory_template',
        'survival': 'survival_template',
        'vital_signs': 'vital_signs_template',
        'concomitant_meds': 'conmed_template',
        'medical_history': 'medical_history_template',
        'exposure': 'exposure_template'
    }
    
    # Standard population definitions
    populations = {
        'safety': "SAFFL=='Y'",
        'efficacy': "EFFFL=='Y'",
        'itt': "ITTFL=='Y'",
        'pp': "PPROTFL=='Y'",
        'randomized': "RANDFL=='Y'",
        'treated': "TRTFL=='Y'"
    }
    
    # Standard treatment definitions
    treatments = {
        'planned_var': 'TRT01P',
        'actual_var': 'TRT01A',
        'planned_num': 'TRT01PN',
        'actual_num': 'TRT01AN',
        'decode_var': 'TRT01A'
    }
    
    return ReportConfig(
        statistics=statistics,
        formats=formats,
        page_settings=page_settings,
        templates=templates,
        populations=populations,
        treatments=treatments
    )


def get_regulatory_submission_config() -> ReportConfig:
    """
    Get enhanced configuration for regulatory submissions.
    
    This configuration includes additional statistical displays and
    formatting options required for comprehensive regulatory submissions.
    
    Returns
    -------
    ReportConfig
        Enhanced regulatory submission configuration
    """
    
    # Start with clinical standard
    config = get_clinical_standard_config()
    
    # Add additional statistics for regulatory submissions
    additional_stats = {
        'lclm': StatisticConfig(
            name='lclm',
            display='Lower 95% CI',
            label='Lower 95% Confidence Limit',
            precision=2
        ),
        'uclm': StatisticConfig(
            name='uclm',
            display='Upper 95% CI',
            label='Upper 95% Confidence Limit',
            precision=2
        ),
        'ci_95': StatisticConfig(
            name='ci_95',
            display='95% CI',
            label='95% Confidence Interval',
            precision=2,
            format_func='format_confidence_interval'
        ),
        'p25': StatisticConfig(
            name='p25',
            display='25th percentile',
            label='25th Percentile',
            precision=1
        ),
        'p75': StatisticConfig(
            name='p75',
            display='75th percentile',
            label='75th Percentile',
            precision=1
        ),
        'range': StatisticConfig(
            name='range',
            display='Range',
            label='Range (Min - Max)',
            precision=1,
            format_func='format_range'
        )
    }
    
    # Add to existing statistics
    config.statistics.update(additional_stats)
    
    # Add additional formats
    additional_formats = {
        'scientific': '{:.2e}',
        'percentage_1dec': '{:.1f}%',
        'percentage_2dec': '{:.2f}%',
        'fold_change': '{:.2f}-fold',
        'ratio': '{:.3f}',
        'odds_ratio': '{:.2f} ({:.2f}, {:.2f})',
        'hazard_ratio': '{:.2f} ({:.2f}, {:.2f})',
        'difference': '{:.2f} ({:.2f}, {:.2f})'
    }
    
    config.formats.update(additional_formats)
    
    # Add additional templates for regulatory submissions
    additional_templates = {
        'pk_parameters': 'pk_parameters_template',
        'immunogenicity': 'immunogenicity_template',
        'biomarkers': 'biomarkers_template',
        'dose_intensity': 'dose_intensity_template',
        'protocol_deviations': 'protocol_deviations_template',
        'prior_therapy': 'prior_therapy_template',
        'ecg_parameters': 'ecg_parameters_template',
        'laboratory_shifts': 'laboratory_shifts_template',
        'laboratory_outliers': 'laboratory_outliers_template'
    }
    
    config.templates.update(additional_templates)
    
    return config


def get_oncology_config() -> ReportConfig:
    """
    Get specialized configuration for oncology studies.
    
    This configuration includes oncology-specific statistical displays
    and analysis templates.
    
    Returns
    -------
    ReportConfig
        Oncology-specific configuration
    """
    
    # Start with regulatory submission config
    config = get_regulatory_submission_config()
    
    # Add oncology-specific statistics
    oncology_stats = {
        'response_rate': StatisticConfig(
            name='response_rate',
            display='Response Rate (%)',
            label='Overall Response Rate',
            precision=1,
            format_func='format_response_rate'
        ),
        'median_survival': StatisticConfig(
            name='median_survival',
            display='Median (95% CI)',
            label='Median Survival Time with 95% CI',
            precision=1,
            format_func='format_median_survival'
        ),
        'hazard_ratio': StatisticConfig(
            name='hazard_ratio',
            display='HR (95% CI)',
            label='Hazard Ratio with 95% CI',
            precision=2,
            format_func='format_hazard_ratio'
        )
    }
    
    config.statistics.update(oncology_stats)
    
    # Add oncology-specific templates
    oncology_templates = {
        'tumor_response': 'tumor_response_template',
        'survival_summary': 'survival_summary_template',
        'time_to_event': 'time_to_event_template',
        'biomarker_efficacy': 'biomarker_efficacy_template',
        'dose_limiting_toxicity': 'dlt_template'
    }
    
    config.templates.update(oncology_templates)
    
    return config 