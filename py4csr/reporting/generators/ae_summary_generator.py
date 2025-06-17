"""
AE summary table generator for py4csr functional reporting system.

This module generates adverse event summary tables showing overall
AE incidence by treatment group.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any

from .base_generator import BaseTableGenerator
from ..table_specification import TableSpecification
from ..table_result import TableResult


class AESummaryGenerator(BaseTableGenerator):
    """
    Generator for adverse event summary tables.
    
    This generator creates AE summary tables showing incidence of
    any AE, serious AEs, drug-related AEs, etc. by treatment group.
    """
    
    def generate(self, spec: TableSpecification) -> TableResult:
        """
        Generate AE summary table.
        
        Parameters
        ----------
        spec : TableSpecification
            Table specification
            
        Returns
        -------
        TableResult
            Generated AE summary table
        """
        # Get and validate data
        data = spec.get_data()
        validation_result = self.validate_data(data, spec)
        
        if not validation_result['passed']:
            raise ValueError(f"Data validation failed: {validation_result['errors']}")
        
        trt_var = spec.get_treatment_variable()
        
        # Generate AE summary
        ae_summary = self._generate_ae_summary(data, trt_var, spec)
        
        # Post-process data
        ae_summary = self.post_process_data(ae_summary, spec)
        
        # Create RTF table
        rtf_table = self.create_rtf_table(ae_summary, spec)
        
        # Generate metadata
        metadata = self.generate_metadata(spec)
        metadata.update({
            'n_subjects': len(data['USUBJID'].unique()) if 'USUBJID' in data.columns else len(data),
            'n_events': len(data),
            'treatment_groups': data[trt_var].value_counts().to_dict()
        })
        
        return TableResult(
            data=ae_summary,
            rtf_table=rtf_table,
            metadata=metadata,
            validation_results=validation_result
        )
    
    def _generate_ae_summary(self, data: pd.DataFrame, trt_var: str,
                           spec: TableSpecification) -> pd.DataFrame:
        """Generate AE summary statistics."""
        
        summary_data = []
        
        # Get unique subjects per treatment (for denominators)
        if 'USUBJID' in data.columns:
            subject_counts = data.groupby(trt_var)['USUBJID'].nunique()
        else:
            # Fallback if no subject ID
            subject_counts = data[trt_var].value_counts()
        
        treatments = sorted(subject_counts.index)
        
        # Header row
        header_row = {
            'AE Category': 'Adverse Event Category',
            'Statistic': 'n (%)'
        }
        
        for trt in treatments:
            header_row[trt] = trt
        
        if spec.include_total:
            header_row['Total'] = 'Total'
        
        summary_data.append(header_row)
        
        # Any AE
        any_ae_row = self._calculate_ae_category(
            data, trt_var, subject_counts, 'Any Adverse Event', 
            lambda df: df, spec.include_total
        )
        summary_data.append(any_ae_row)
        
        # Serious AEs
        if 'AESER' in data.columns:
            serious_ae_row = self._calculate_ae_category(
                data, trt_var, subject_counts, 'Serious Adverse Events',
                lambda df: df[df['AESER'] == 'Y'], spec.include_total
            )
            summary_data.append(serious_ae_row)
        
        # Drug-related AEs
        if 'AEREL' in data.columns:
            related_ae_row = self._calculate_ae_category(
                data, trt_var, subject_counts, 'Drug-Related Adverse Events',
                lambda df: df[df['AEREL'].isin(['POSSIBLE', 'PROBABLE', 'RELATED'])],
                spec.include_total
            )
            summary_data.append(related_ae_row)
        
        # Severe AEs
        if 'AESEV' in data.columns:
            severe_ae_row = self._calculate_ae_category(
                data, trt_var, subject_counts, 'Severe Adverse Events',
                lambda df: df[df['AESEV'] == 'SEVERE'], spec.include_total
            )
            summary_data.append(severe_ae_row)
        
        # AEs leading to discontinuation
        if 'AEACN' in data.columns:
            disc_ae_row = self._calculate_ae_category(
                data, trt_var, subject_counts, 'AEs Leading to Discontinuation',
                lambda df: df[df['AEACN'].str.contains('DRUG WITHDRAWN', na=False)],
                spec.include_total
            )
            summary_data.append(disc_ae_row)
        
        # Deaths
        if 'AEOUT' in data.columns:
            death_row = self._calculate_ae_category(
                data, trt_var, subject_counts, 'Deaths',
                lambda df: df[df['AEOUT'] == 'FATAL'], spec.include_total
            )
            summary_data.append(death_row)
        
        return pd.DataFrame(summary_data)
    
    def _calculate_ae_category(self, data: pd.DataFrame, trt_var: str,
                             subject_counts: pd.Series, category_name: str,
                             filter_func, include_total: bool) -> Dict[str, str]:
        """Calculate statistics for a specific AE category."""
        
        # Apply filter
        filtered_data = filter_func(data)
        
        row = {
            'AE Category': category_name,
            'Statistic': ''
        }
        
        # Calculate for each treatment
        for trt in subject_counts.index:
            trt_filtered = filtered_data[filtered_data[trt_var] == trt]
            
            if 'USUBJID' in trt_filtered.columns:
                n_subjects_with_ae = trt_filtered['USUBJID'].nunique()
            else:
                n_subjects_with_ae = len(trt_filtered)
            
            n_total_subjects = subject_counts[trt]
            
            if n_total_subjects > 0:
                pct = (n_subjects_with_ae / n_total_subjects) * 100
                row[trt] = f"{n_subjects_with_ae} ({pct:.1f}%)"
            else:
                row[trt] = "0"
        
        # Total column
        if include_total:
            if 'USUBJID' in filtered_data.columns:
                n_subjects_total = filtered_data['USUBJID'].nunique()
                n_total_subjects_total = data['USUBJID'].nunique()
            else:
                n_subjects_total = len(filtered_data)
                n_total_subjects_total = len(data)
            
            if n_total_subjects_total > 0:
                pct_total = (n_subjects_total / n_total_subjects_total) * 100
                row['Total'] = f"{n_subjects_total} ({pct_total:.1f}%)"
            else:
                row['Total'] = "0"
        
        return row 