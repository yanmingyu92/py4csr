"""
AE detail table generator for py4csr functional reporting system.
"""

import pandas as pd
from .base_generator import BaseTableGenerator
from ..table_specification import TableSpecification
from ..table_result import TableResult


class AEDetailGenerator(BaseTableGenerator):
    """Generator for detailed adverse event tables."""
    
    def generate(self, spec: TableSpecification) -> TableResult:
        """Generate AE detail table."""
        data = spec.get_data()
        validation_result = self.validate_data(data, spec)
        
        # Create placeholder table
        placeholder_data = pd.DataFrame({
            'System Organ Class': ['GASTROINTESTINAL DISORDERS', 'NERVOUS SYSTEM DISORDERS'],
            'Preferred Term': ['NAUSEA', 'HEADACHE'],
            'Placebo': ['5 (10.0%)', '3 (6.0%)'],
            'Drug A 10mg': ['8 (16.0%)', '6 (12.0%)'],
            'Drug A 20mg': ['12 (24.0%)', '9 (18.0%)'],
            'Total': ['25 (16.7%)', '18 (12.0%)']
        })
        
        rtf_table = self.create_rtf_table(placeholder_data, spec)
        metadata = self.generate_metadata(spec)
        
        return TableResult(
            data=placeholder_data,
            rtf_table=rtf_table,
            metadata=metadata,
            validation_results=validation_result
        ) 