"""
Disposition table generator for py4csr functional reporting system.

This module generates subject disposition tables showing study completion
and discontinuation reasons.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any

from .base_generator import BaseTableGenerator
from ..table_specification import TableSpecification
from ..table_result import TableResult


class DispositionGenerator(BaseTableGenerator):
    """
    Generator for subject disposition tables.
    
    This generator creates disposition summaries showing completion rates
    and reasons for discontinuation by treatment group.
    """
    
    def generate(self, spec: TableSpecification) -> TableResult:
        """
        Generate disposition table.
        
        Parameters
        ----------
        spec : TableSpecification
            Table specification
            
        Returns
        -------
        TableResult
            Generated disposition table
        """
        # Get and validate data
        data = spec.get_data()
        validation_result = self.validate_data(data, spec)
        
        if not validation_result['passed']:
            raise ValueError(f"Data validation failed: {validation_result['errors']}")
        
        trt_var = spec.get_treatment_variable()
        
        # Generate disposition summary
        disposition_summary = self._generate_disposition_summary(data, trt_var, spec)
        
        # Post-process data
        disposition_summary = self.post_process_data(disposition_summary, spec)
        
        # Create RTF table
        rtf_table = self.create_rtf_table(disposition_summary, spec)
        
        # Generate metadata
        metadata = self.generate_metadata(spec)
        metadata.update({
            'n_subjects': len(data),
            'treatment_groups': data[trt_var].value_counts().to_dict()
        })
        
        return TableResult(
            data=disposition_summary,
            rtf_table=rtf_table,
            metadata=metadata,
            validation_results=validation_result
        )
    
    def _generate_disposition_summary(self, data: pd.DataFrame, trt_var: str,
                                    spec: TableSpecification) -> pd.DataFrame:
        """Generate disposition summary statistics."""
        
        summary_data = []
        treatments = sorted(data[trt_var].unique())
        
        # Disposition categories
        disposition_vars = ['DCSREAS', 'DCREASCD']
        disp_var = None
        
        # Find available disposition variable
        for var in disposition_vars:
            if var in data.columns:
                disp_var = var
                break
        
        if disp_var is None:
            # Create basic disposition based on available flags
            if 'RANDFL' in data.columns:
                data = data.copy()
                data['DISPOSITION'] = 'RANDOMIZED'
            else:
                raise ValueError("No disposition variables found")
            disp_var = 'DISPOSITION'
        
        # Get disposition categories
        if disp_var in data.columns:
            categories = data[disp_var].dropna().unique()
        else:
            categories = ['COMPLETED', 'DISCONTINUED']
        
        # Header row
        header_row = {
            'Disposition Category': 'Disposition Category',
            'Statistic': 'n (%)'
        }
        
        for trt in treatments:
            header_row[trt] = trt
        
        if spec.include_total:
            header_row['Total'] = 'Total'
        
        summary_data.append(header_row)
        
        # Generate statistics for each category
        for category in sorted(categories):
            if pd.isna(category):
                continue
            
            row = {
                'Disposition Category': category,
                'Statistic': ''
            }
            
            # Calculate for each treatment
            for trt in treatments:
                trt_data = data[data[trt_var] == trt]
                n_category = len(trt_data[trt_data[disp_var] == category])
                n_total = len(trt_data)
                
                if n_total > 0:
                    pct = (n_category / n_total) * 100
                    row[trt] = f"{n_category} ({pct:.1f}%)"
                else:
                    row[trt] = "0"
            
            # Total column
            if spec.include_total:
                n_category_total = len(data[data[disp_var] == category])
                n_total_total = len(data)
                
                if n_total_total > 0:
                    pct_total = (n_category_total / n_total_total) * 100
                    row['Total'] = f"{n_category_total} ({pct_total:.1f}%)"
                else:
                    row['Total'] = "0"
            
            summary_data.append(row)
        
        return pd.DataFrame(summary_data) 