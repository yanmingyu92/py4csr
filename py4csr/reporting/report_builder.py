"""
Functional report builder for py4csr.

This module provides a functional programming approach to building clinical
study reports, inspired by the SAS RRG system's macro chaining pattern.
"""

from typing import Dict, List, Optional, Any, Union
import pandas as pd
from pathlib import Path
from datetime import datetime
import warnings

from ..config import ReportConfig
from .table_specification import TableSpecification
from .generators import TableGeneratorFactory
from .table_result import TableResult, ReportResult


class ReportBuilder:
    """
    Functional report builder using method chaining.
    
    This class implements a functional programming approach similar to the
    SAS RRG system, where each method returns self to enable chaining.
    
    Examples
    --------
    >>> from py4csr.reporting import ReportBuilder
    >>> from py4csr.config import ReportConfig
    >>> 
    >>> config = ReportConfig.clinical_standard()
    >>> report = (ReportBuilder(config)
    ...     .init_study(uri="STUDY001", title="Phase III Study")
    ...     .add_dataset(adsl, "adsl", "subject_level")
    ...     .add_dataset(adae, "adae", "adverse_events")
    ...     .define_populations(safety="SAFFL=='Y'", efficacy="EFFFL=='Y'")
    ...     .define_treatments(var="TRT01P", decode="TRT01A")
    ...     .add_demographics_table()
    ...     .add_ae_summary_table()
    ...     .generate_all()
    ...     .finalize())
    """
    
    def __init__(self, config: ReportConfig):
        """
        Initialize report builder.
        
        Parameters
        ----------
        config : ReportConfig
            Configuration for the report generation
        """
        self.config = config
        self.datasets = {}
        self.populations = {}
        self.treatments = {}
        self.tables = []
        self.metadata = {}
        self.generated_files = []
        self._finalized = False
        
    def init_study(self, uri: str, title: str, **kwargs) -> 'ReportBuilder':
        """
        Initialize study metadata.
        
        Parameters
        ----------
        uri : str
            Unique report identifier
        title : str
            Main report title
        **kwargs
            Additional metadata (protocol, compound, etc.)
            
        Returns
        -------
        ReportBuilder
            Self for method chaining
        """
        self.metadata.update({
            'uri': uri,
            'title': title,
            'created_by': kwargs.get('created_by', 'py4csr'),
            'created_date': kwargs.get('created_date', datetime.now()),
            'protocol': kwargs.get('protocol', ''),
            'compound': kwargs.get('compound', ''),
            'indication': kwargs.get('indication', ''),
            'sponsor': kwargs.get('sponsor', ''),
            **{k: v for k, v in kwargs.items() 
               if k not in ['created_by', 'created_date', 'protocol', 'compound', 'indication', 'sponsor']}
        })
        return self
    
    def add_dataset(self, data: pd.DataFrame, name: str, type: str) -> 'ReportBuilder':
        """
        Add dataset to the report context.
        
        Parameters
        ----------
        data : pd.DataFrame
            Dataset to add
        name : str
            Dataset name (e.g., 'adsl', 'adae')
        type : str
            Dataset type (e.g., 'subject_level', 'adverse_events')
            
        Returns
        -------
        ReportBuilder
            Self for method chaining
        """
        self.datasets[name] = {
            'data': data.copy(),
            'type': type,
            'metadata': self._extract_dataset_metadata(data, type)
        }
        return self
    
    def define_populations(self, **populations) -> 'ReportBuilder':
        """
        Define analysis populations.
        
        Parameters
        ----------
        **populations
            Population definitions as keyword arguments
            (e.g., safety="SAFFL=='Y'", efficacy="EFFFL=='Y'")
            
        Returns
        -------
        ReportBuilder
            Self for method chaining
        """
        self.populations.update(populations)
        return self
    
    def define_treatments(self, var: str, decode: Optional[str] = None, 
                         num_var: Optional[str] = None) -> 'ReportBuilder':
        """
        Define treatment variables.
        
        Parameters
        ----------
        var : str
            Treatment variable name
        decode : str, optional
            Treatment decode variable name
        num_var : str, optional
            Numeric treatment variable name
            
        Returns
        -------
        ReportBuilder
            Self for method chaining
        """
        self.treatments = {
            'variable': var,
            'decode': decode or var,
            'num_variable': num_var,
            'levels': self._get_treatment_levels(var)
        }
        return self
    
    def add_table(self, table_type: str, **kwargs) -> 'ReportBuilder':
        """
        Add a table specification.
        
        Parameters
        ----------
        table_type : str
            Type of table to generate
        **kwargs
            Additional table parameters
            
        Returns
        -------
        ReportBuilder
            Self for method chaining
        """
        table_spec = TableSpecification(
            type=table_type,
            config=self.config,
            datasets=self.datasets,
            populations=self.populations,
            treatments=self.treatments,
            **kwargs
        )
        self.tables.append(table_spec)
        return self
    
    # Convenience methods for common tables (equivalent to SAS RRG addvar, addcatvar, etc.)
    def add_demographics_table(self, **kwargs) -> 'ReportBuilder':
        """Add demographics table (equivalent to SAS RRG addvar for demographics)"""
        defaults = {
            'title': 'Baseline Demographics and Clinical Characteristics',
            'subtitle': 'Safety Analysis Population',
            'population': 'safety',
            'variables': ['AGE', 'AGEGR1', 'SEX', 'RACE', 'WEIGHT', 'HEIGHT', 'BMI']
        }
        defaults.update(kwargs)
        return self.add_table('demographics', **defaults)
    
    def add_disposition_table(self, **kwargs) -> 'ReportBuilder':
        """Add disposition table"""
        defaults = {
            'title': 'Subject Disposition',
            'subtitle': 'All Randomized Subjects',
            'population': 'randomized'
        }
        defaults.update(kwargs)
        return self.add_table('disposition', **defaults)
    
    def add_ae_summary_table(self, **kwargs) -> 'ReportBuilder':
        """Add AE summary table"""
        defaults = {
            'title': 'Summary of Adverse Events',
            'subtitle': 'Safety Analysis Population',
            'population': 'safety'
        }
        defaults.update(kwargs)
        return self.add_table('ae_summary', **defaults)
    
    def add_ae_detail_table(self, **kwargs) -> 'ReportBuilder':
        """Add detailed AE table"""
        defaults = {
            'title': 'Adverse Events by System Organ Class and Preferred Term',
            'subtitle': 'Safety Analysis Population',
            'population': 'safety',
            'grouping': ['AEBODSYS', 'AEDECOD']
        }
        defaults.update(kwargs)
        return self.add_table('ae_detail', **defaults)
    
    def add_efficacy_table(self, **kwargs) -> 'ReportBuilder':
        """Add efficacy analysis table"""
        defaults = {
            'title': 'Analysis of Primary Efficacy Endpoint',
            'subtitle': 'Efficacy Analysis Population',
            'population': 'efficacy',
            'analysis_type': 'ancova'
        }
        defaults.update(kwargs)
        return self.add_table('efficacy', **defaults)
    
    def add_laboratory_tables(self, **kwargs) -> 'ReportBuilder':
        """Add laboratory analysis tables"""
        defaults = {
            'title': 'Laboratory Parameters - Summary Statistics',
            'subtitle': 'Safety Analysis Population',
            'population': 'safety'
        }
        defaults.update(kwargs)
        return self.add_table('laboratory', **defaults)
    
    def add_survival_analysis(self, **kwargs) -> 'ReportBuilder':
        """Add survival analysis table and plot"""
        defaults = {
            'title': 'Kaplan-Meier Analysis of Time to Event',
            'subtitle': 'Efficacy Analysis Population',
            'population': 'efficacy'
        }
        defaults.update(kwargs)
        return self.add_table('survival', **defaults)
    
    def add_vital_signs_table(self, **kwargs) -> 'ReportBuilder':
        """Add vital signs analysis table"""
        defaults = {
            'title': 'Vital Signs - Summary Statistics',
            'subtitle': 'Safety Analysis Population',
            'population': 'safety'
        }
        defaults.update(kwargs)
        return self.add_table('vital_signs', **defaults)
    
    def add_concomitant_meds_table(self, **kwargs) -> 'ReportBuilder':
        """Add concomitant medications table"""
        defaults = {
            'title': 'Concomitant Medications',
            'subtitle': 'Safety Analysis Population',
            'population': 'safety'
        }
        defaults.update(kwargs)
        return self.add_table('concomitant_meds', **defaults)
    
    def add_medical_history_table(self, **kwargs) -> 'ReportBuilder':
        """Add medical history table"""
        defaults = {
            'title': 'Medical History',
            'subtitle': 'Safety Analysis Population',
            'population': 'safety'
        }
        defaults.update(kwargs)
        return self.add_table('medical_history', **defaults)
    
    def add_exposure_table(self, **kwargs) -> 'ReportBuilder':
        """Add exposure analysis table"""
        defaults = {
            'title': 'Extent of Exposure',
            'subtitle': 'Safety Analysis Population',
            'population': 'safety'
        }
        defaults.update(kwargs)
        return self.add_table('exposure', **defaults)
    
    def generate_all(self, output_dir: str = "output") -> 'ReportBuilder':
        """
        Generate all specified tables.
        
        Parameters
        ----------
        output_dir : str
            Output directory for generated files
            
        Returns
        -------
        ReportBuilder
            Self for method chaining
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)
        
        self.generated_files = []
        
        print(f"Generating {len(self.tables)} tables...")
        
        for i, table_spec in enumerate(self.tables, 1):
            try:
                print(f"  {i}/{len(self.tables)}: Generating {table_spec.type} table...")
                
                # Create generator and generate table
                generator = TableGeneratorFactory.create(table_spec.type)
                result = generator.generate(table_spec)
                
                # Write RTF file
                rtf_file = output_path / f"{table_spec.get_filename()}.rtf"
                result.write_rtf(rtf_file)
                self.generated_files.append(rtf_file)
                
                # Generate any associated figures
                if hasattr(result, 'figures') and result.figures:
                    for fig_name, figure in result.figures.items():
                        fig_file = output_path / f"{fig_name}.png"
                        figure.savefig(fig_file, dpi=300, bbox_inches='tight')
                        self.generated_files.append(fig_file)
                        
                print(f"    ✓ Generated {rtf_file.name}")
                
            except Exception as e:
                warnings.warn(f"Failed to generate {table_spec.type} table: {str(e)}")
                continue
        
        print(f"✅ Generated {len(self.generated_files)} files in {output_dir}/")
        return self
    
    def finalize(self) -> ReportResult:
        """
        Finalize report and return results.
        
        Returns
        -------
        ReportResult
            Final report results with metadata and file list
        """
        if self._finalized:
            warnings.warn("Report already finalized")
            
        self._finalized = True
        
        return ReportResult(
            metadata=self.metadata,
            generated_files=self.generated_files,
            summary=self._generate_summary(),
            config=self.config
        )
    
    def _extract_dataset_metadata(self, data: pd.DataFrame, type: str) -> Dict[str, Any]:
        """Extract metadata from dataset"""
        return {
            'n_records': len(data),
            'n_variables': len(data.columns),
            'variables': list(data.columns),
            'type': type,
            'memory_usage': data.memory_usage(deep=True).sum()
        }
    
    def _get_treatment_levels(self, var: str) -> List[str]:
        """Get treatment levels from datasets"""
        levels = []
        for dataset_info in self.datasets.values():
            data = dataset_info['data']
            if var in data.columns:
                levels.extend(data[var].dropna().unique().tolist())
        
        # Remove duplicates and sort
        return sorted(list(set(levels)))
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary of report generation"""
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
            'tables_generated': len(self.tables),
            'datasets_used': len(self.datasets),
            'populations_defined': len(self.populations),
            'generation_time': datetime.now()
        } 