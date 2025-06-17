from typing import Dict, List, Optional, Any, Union
import pandas as pd
from pathlib import Path
from ..core.data_processor import DataProcessor
from ..reporting.rtf_table import RTFTable
from ..clinical.enhanced_rtf_formatter import EnhancedClinicalRTFFormatter

class WorkflowEnhancement:
    """
    Workflow enhancement functions following RRG functional programming style.
    
    Provides advanced data processing, validation, and output generation
    capabilities that integrate seamlessly with existing RTF infrastructure.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.data_processor = DataProcessor()
        self.rtf_formatter = EnhancedClinicalRTFFormatter()
    
    def advanced_data_validation(self, 
                               data: pd.DataFrame,
                               validation_rules: Dict[str, Any]) -> Dict[str, Any]:
        """
        Advanced data validation with comprehensive reporting.
        
        Equivalent to RRG's data validation macros.
        """
        validation_results = {
            'passed': True,
            'warnings': [],
            'errors': [],
            'summary': {}
        }
        
        # Missing value validation
        if 'required_columns' in validation_rules:
            for col in validation_rules['required_columns']:
                if col in data.columns:
                    missing_count = data[col].isnull().sum()
                    if missing_count > 0:
                        validation_results['warnings'].append(
                            f"Column '{col}' has {missing_count} missing values"
                        )
        
        # Data type validation
        if 'column_types' in validation_rules:
            for col, expected_type in validation_rules['column_types'].items():
                if col in data.columns:
                    if not data[col].dtype == expected_type:
                        validation_results['errors'].append(
                            f"Column '{col}' expected type {expected_type}, got {data[col].dtype}"
                        )
                        validation_results['passed'] = False
        
        # Range validation
        if 'value_ranges' in validation_rules:
            for col, (min_val, max_val) in validation_rules['value_ranges'].items():
                if col in data.columns:
                    out_of_range = data[(data[col] < min_val) | (data[col] > max_val)]
                    if len(out_of_range) > 0:
                        validation_results['warnings'].append(
                            f"Column '{col}' has {len(out_of_range)} values outside range [{min_val}, {max_val}]"
                        )
        
        validation_results['summary'] = {
            'total_rows': len(data),
            'total_columns': len(data.columns),
            'validation_passed': validation_results['passed'],
            'warning_count': len(validation_results['warnings']),
            'error_count': len(validation_results['errors'])
        }
        
        return validation_results
    
    def enhanced_data_processing(self, 
                               data: pd.DataFrame,
                               processing_steps: List[Dict]) -> pd.DataFrame:
        """
        Enhanced data processing pipeline.
        
        Equivalent to RRG's data manipulation macros.
        """
        processed_data = data.copy()
        
        for step in processing_steps:
            step_type = step.get('type')
            
            if step_type == 'filter':
                condition = step.get('condition')
                if condition:
                    processed_data = processed_data.query(condition)
            
            elif step_type == 'derive':
                new_col = step.get('column')
                expression = step.get('expression')
                if new_col and expression:
                    processed_data[new_col] = processed_data.eval(expression)
            
            elif step_type == 'aggregate':
                group_by = step.get('group_by', [])
                agg_funcs = step.get('functions', {})
                if group_by and agg_funcs:
                    processed_data = processed_data.groupby(group_by).agg(agg_funcs).reset_index()
            
            elif step_type == 'sort':
                sort_cols = step.get('columns', [])
                ascending = step.get('ascending', True)
                if sort_cols:
                    processed_data = processed_data.sort_values(sort_cols, ascending=ascending)
        
        return processed_data
    
    def multi_format_output_generation(self, 
                                     data: pd.DataFrame,
                                     output_config: Dict[str, Any]) -> Dict[str, Path]:
        """
        Generate multiple output formats simultaneously.
        
        Equivalent to RRG's multi-format output capabilities.
        """
        output_files = {}
        base_filename = output_config.get('filename', 'output')
        output_dir = Path(output_config.get('output_dir', '.'))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        formats = output_config.get('formats', ['rtf'])
        
        for fmt in formats:
            if fmt == 'rtf':
                rtf_file = output_dir / f"{base_filename}.rtf"
                rtf_table = RTFTable()
                rtf_table.rtf_title(output_config.get('title', 'Clinical Table'))
                rtf_table.rtf_colheader(list(data.columns))
                rtf_table.rtf_body(data)
                if 'footnotes' in output_config:
                    rtf_table.rtf_footnote(output_config['footnotes'])
                rtf_table.write_rtf(rtf_file)
                output_files['rtf'] = rtf_file
            
            elif fmt == 'csv':
                csv_file = output_dir / f"{base_filename}.csv"
                data.to_csv(csv_file, index=False)
                output_files['csv'] = csv_file
            
            elif fmt == 'excel':
                excel_file = output_dir / f"{base_filename}.xlsx"
                data.to_excel(excel_file, index=False)
                output_files['excel'] = excel_file
        
        return output_files

# Functional interface functions (RRG style)
def validate_data(data: pd.DataFrame, rules: Dict[str, Any]) -> Dict[str, Any]:
    """Functional interface for data validation."""
    enhancer = WorkflowEnhancement()
    return enhancer.advanced_data_validation(data, rules)

def process_data(data: pd.DataFrame, steps: List[Dict]) -> pd.DataFrame:
    """Functional interface for data processing."""
    enhancer = WorkflowEnhancement()
    return enhancer.enhanced_data_processing(data, steps)

def generate_outputs(data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Path]:
    """Functional interface for multi-format output generation."""
    enhancer = WorkflowEnhancement()
    return enhancer.multi_format_output_generation(data, config)