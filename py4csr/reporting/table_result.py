"""
Table result classes for py4csr functional reporting.

This module defines the result objects returned by table generators.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
import pandas as pd
from pathlib import Path
from datetime import datetime

from .rtf_table import RTFTable
from ..config import ReportConfig


@dataclass
class TableResult:
    """
    Result of table generation.
    
    This class holds the generated table data, RTF output, and metadata.
    
    Parameters
    ----------
    data : pd.DataFrame
        The processed data used to generate the table
    rtf_table : RTFTable
        The RTF table object
    metadata : dict
        Table generation metadata
    figures : dict, optional
        Associated figures (e.g., plots)
    validation_results : dict, optional
        Data validation results
    """
    
    data: pd.DataFrame
    rtf_table: RTFTable
    metadata: Dict[str, Any]
    figures: Optional[Dict[str, Any]] = None
    validation_results: Optional[Dict[str, Any]] = None
    
    def write_rtf(self, filepath: Union[str, Path]) -> None:
        """
        Write RTF table to file.
        
        Parameters
        ----------
        filepath : str or Path
            Output file path
        """
        self.rtf_table.write_rtf(filepath)
    
    def to_rtf(self, filepath: Union[str, Path]) -> None:
        """
        Alias for write_rtf.
        
        Parameters
        ----------
        filepath : str or Path
            Output file path
        """
        self.write_rtf(filepath)
    
    def get_rtf_content(self) -> str:
        """
        Get RTF content as string.
        
        Returns
        -------
        str
            RTF formatted content
        """
        return self.rtf_table.rtf_encode()
    
    def save_data(self, filepath: Union[str, Path], format: str = 'csv') -> None:
        """
        Save the processed data to file.
        
        Parameters
        ----------
        filepath : str or Path
            Output file path
        format : str
            Output format ('csv', 'excel', 'sas')
        """
        filepath = Path(filepath)
        
        if format.lower() == 'csv':
            self.data.to_csv(filepath, index=False)
        elif format.lower() in ['excel', 'xlsx']:
            self.data.to_excel(filepath, index=False)
        elif format.lower() == 'sas':
            # Would implement SAS export if pyreadstat supports it
            raise NotImplementedError("SAS export not yet implemented")
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of table results.
        
        Returns
        -------
        dict
            Summary information
        """
        return {
            'table_type': self.metadata.get('table_type', 'unknown'),
            'n_rows': len(self.data),
            'n_columns': len(self.data.columns),
            'generation_time': self.metadata.get('generation_time'),
            'has_figures': bool(self.figures),
            'n_figures': len(self.figures) if self.figures else 0,
            'validation_passed': self.validation_results.get('passed', True) if self.validation_results else True
        }


@dataclass
class ReportResult:
    """
    Final result of complete report generation.
    
    This class holds the overall results of generating a complete report
    with multiple tables and associated metadata.
    
    Parameters
    ----------
    metadata : dict
        Report metadata
    generated_files : list
        List of generated file paths
    summary : dict
        Report generation summary
    config : ReportConfig
        Configuration used for generation
    table_results : dict, optional
        Individual table results
    errors : list, optional
        Any errors encountered during generation
    """
    
    metadata: Dict[str, Any]
    generated_files: List[Path]
    summary: Dict[str, Any]
    config: ReportConfig
    table_results: Optional[Dict[str, TableResult]] = None
    errors: Optional[List[str]] = None
    
    def get_file_summary(self) -> Dict[str, Any]:
        """
        Get summary of generated files.
        
        Returns
        -------
        dict
            File summary information
        """
        if not self.generated_files:
            return {
                'total_files': 0,
                'total_size_bytes': 0,
                'file_types': {}
            }
        
        total_size = sum(f.stat().st_size for f in self.generated_files if f.exists())
        
        file_types = {}
        for f in self.generated_files:
            ext = f.suffix.lower()
            file_types[ext] = file_types.get(ext, 0) + 1
        
        return {
            'total_files': len(self.generated_files),
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'file_types': file_types,
            'files': [str(f) for f in self.generated_files]
        }
    
    def print_summary(self) -> None:
        """Print a formatted summary of the report generation."""
        print("=" * 60)
        print("REPORT GENERATION SUMMARY")
        print("=" * 60)
        
        # Basic info
        print(f"Report URI: {self.metadata.get('uri', 'Unknown')}")
        print(f"Title: {self.metadata.get('title', 'Unknown')}")
        print(f"Generated: {self.metadata.get('created_date', 'Unknown')}")
        print(f"Created by: {self.metadata.get('created_by', 'Unknown')}")
        
        # Generation summary
        print(f"\nGeneration Summary:")
        print(f"  Tables generated: {self.summary.get('tables_generated', 0)}")
        print(f"  Datasets used: {self.summary.get('datasets_used', 0)}")
        print(f"  Populations defined: {self.summary.get('populations_defined', 0)}")
        
        # File summary
        file_summary = self.get_file_summary()
        print(f"\nFiles Generated:")
        print(f"  Total files: {file_summary['total_files']}")
        print(f"  Total size: {file_summary['total_size_mb']:.1f} MB")
        
        if file_summary['file_types']:
            print(f"  File types:")
            for ext, count in file_summary['file_types'].items():
                print(f"    {ext}: {count} files")
        
        # Errors
        if self.errors:
            print(f"\nErrors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
        
        # Individual files
        if self.generated_files:
            print(f"\nGenerated Files:")
            for f in self.generated_files:
                size_kb = f.stat().st_size / 1024 if f.exists() else 0
                print(f"  • {f.name} ({size_kb:.1f} KB)")
        
        print("=" * 60)
    
    def save_metadata(self, filepath: Union[str, Path]) -> None:
        """
        Save report metadata to JSON file.
        
        Parameters
        ----------
        filepath : str or Path
            Output file path
        """
        import json
        from datetime import datetime
        
        # Prepare metadata for JSON serialization
        metadata_copy = self.metadata.copy()
        
        # Convert datetime objects to strings
        for key, value in metadata_copy.items():
            if isinstance(value, datetime):
                metadata_copy[key] = value.isoformat()
        
        # Add file summary
        metadata_copy['file_summary'] = self.get_file_summary()
        metadata_copy['generation_summary'] = self.summary
        
        # Convert Path objects to strings
        if 'generated_files' in metadata_copy:
            metadata_copy['generated_files'] = [str(f) for f in self.generated_files]
        
        with open(filepath, 'w') as f:
            json.dump(metadata_copy, f, indent=2, default=str)
    
    def create_combined_rtf(self, output_path: Union[str, Path]) -> None:
        """
        Create a combined RTF file with all tables.
        
        Parameters
        ----------
        output_path : str or Path
            Output file path for combined RTF
        """
        output_path = Path(output_path)
        
        # Collect all RTF files
        rtf_files = [f for f in self.generated_files if f.suffix.lower() == '.rtf']
        
        if not rtf_files:
            raise ValueError("No RTF files found to combine")
        
        combined_content = []
        
        # RTF header
        combined_content.append(r"{\rtf1\ansi\deff0")
        combined_content.append(r"{\fonttbl{\f0 Times New Roman;}}")
        
        # Title page
        combined_content.append(r"\qc\b\fs24 " + self.metadata.get('title', 'Clinical Study Report') + r"\b0\par")
        combined_content.append(r"\qc\fs20 " + self.metadata.get('protocol', '') + r"\par")
        combined_content.append(r"\qc\fs18 Generated: " + str(self.metadata.get('created_date', '')) + r"\par")
        combined_content.append(r"\page")
        
        # Add each table
        for i, rtf_file in enumerate(rtf_files, 1):
            if rtf_file.exists():
                with open(rtf_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract content between RTF tags
                start_idx = content.find(r"{\rtf1")
                end_idx = content.rfind("}")
                
                if start_idx != -1 and end_idx != -1:
                    # Remove RTF wrapper and add content
                    table_content = content[start_idx + len(r"{\rtf1\ansi\deff0"):end_idx]
                    # Remove font table if present
                    if table_content.startswith(r"{\fonttbl"):
                        font_end = table_content.find("}")
                        if font_end != -1:
                            table_content = table_content[font_end + 1:]
                    
                    combined_content.append(table_content)
                    
                    # Add page break except for last table
                    if i < len(rtf_files):
                        combined_content.append(r"\page")
        
        # RTF footer
        combined_content.append("}")
        
        # Write combined file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("".join(combined_content))
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Get summary of validation results across all tables.
        
        Returns
        -------
        dict
            Validation summary
        """
        if not self.table_results:
            return {'total_tables': 0, 'validated_tables': 0, 'validation_errors': []}
        
        total_tables = len(self.table_results)
        validated_tables = 0
        all_errors = []
        
        for table_name, result in self.table_results.items():
            if result.validation_results:
                if result.validation_results.get('passed', True):
                    validated_tables += 1
                else:
                    errors = result.validation_results.get('errors', [])
                    all_errors.extend([f"{table_name}: {error}" for error in errors])
        
        return {
            'total_tables': total_tables,
            'validated_tables': validated_tables,
            'validation_rate': validated_tables / total_tables if total_tables > 0 else 0,
            'validation_errors': all_errors
        } 