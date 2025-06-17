"""
Report Session - Main orchestrator for functional clinical reporting.

This module implements the core ReportSession class that provides a functional programming
approach to clinical trial reporting through method chaining and composable operations.
"""

from typing import Dict, List, Optional, Any, Union
import pandas as pd
from pathlib import Path
from datetime import datetime
import warnings

from .config import FunctionalConfig
from .table_builder import TableBuilder
from .statistical_templates import StatisticalTemplates
from .output_generators import OutputGeneratorFactory
from ..data.io import read_sas, load_dataset


class ReportSession:
    """
    Main report session class implementing functional composition for clinical reporting.
    
    This class maintains state across function calls and provides method chaining
    for building complex clinical reports using a functional programming approach.
    
    The session follows a standard clinical reporting workflow:
    1. Initialize session with study metadata
    2. Define datasets and analysis populations
    3. Add variables and tables for analysis
    4. Generate reports in multiple formats
    5. Finalize output and collect results
    
    Examples
    --------
    >>> # Basic functional composition pattern
    >>> session = (ReportSession()
    ...     .init_study(uri="STUDY001", title="Phase III Study")
    ...     .load_datasets(data_path="data/")
    ...     .define_populations(safety="SAFFL=='Y'")
    ...     .define_treatments(var="TRT01P")
    ...     .add_demographics_table()
    ...     .generate_all()
    ...     .finalize())
    """
    
    def __init__(self, config: Optional[FunctionalConfig] = None):
        """
        Initialize report session.
        
        Parameters
        ----------
        config : FunctionalConfig, optional
            Configuration for report generation. If None, uses default clinical config.
        """
        self.config = config or FunctionalConfig.clinical_standard()
        
        # Session state for functional composition
        self.metadata = {}
        self.datasets = {}
        self.populations = {}
        self.treatments = {}
        self.variables = {}
        self.tables = []
        self.generated_outputs = []
        
        # Internal state tracking
        self._initialized = False
        self._finalized = False
        self._current_table_id = 0
        
        # Statistical templates
        self.templates = StatisticalTemplates(self.config)
        
    def init_study(self, uri: str, title: str, **kwargs) -> 'ReportSession':
        """
        Initialize study metadata for the reporting session.
        
        Parameters
        ----------
        uri : str
            Unique report identifier
        title : str
            Main study title
        **kwargs
            Additional metadata (protocol, compound, sponsor, etc.)
            
        Returns
        -------
        ReportSession
            Self for method chaining
        """
        self.metadata = {
            'uri': uri,
            'title': title,
            'created_by': kwargs.get('created_by', 'py4csr'),
            'created_date': kwargs.get('created_date', datetime.now()),
            'protocol': kwargs.get('protocol', ''),
            'compound': kwargs.get('compound', ''),
            'indication': kwargs.get('indication', ''),
            'sponsor': kwargs.get('sponsor', ''),
            'study_phase': kwargs.get('study_phase', ''),
            'data_cutoff': kwargs.get('data_cutoff', ''),
            **{k: v for k, v in kwargs.items() 
               if k not in ['created_by', 'created_date', 'protocol', 'compound', 
                           'indication', 'sponsor', 'study_phase', 'data_cutoff']}
        }
        
        self._initialized = True
        print(f"✓ Initialized study session: {uri}")
        return self
        
    def load_datasets(self, data_path: Union[str, Path] = None, 
                     datasets: Optional[Dict[str, Union[str, pd.DataFrame]]] = None) -> 'ReportSession':
        """
        Load clinical datasets (equivalent to SAS dataset specification).
        
        Parameters
        ----------
        data_path : str or Path, optional
            Path to directory containing SAS datasets
        datasets : dict, optional
            Dictionary of dataset names to file paths or DataFrames
            
        Returns
        -------
        ReportSession
            Self for method chaining
        """
        if not self._initialized:
            raise RuntimeError("Session must be initialized before loading datasets")
            
        if data_path:
            data_path = Path(data_path)
            # Auto-discover standard ADaM datasets
            standard_datasets = ['adsl', 'adae', 'adlb', 'adlbc', 'adlbh', 'adlbhy', 
                                'advs', 'adtte', 'adqsadas', 'adqscibc', 'adqsnpix']
            
            for dataset_name in standard_datasets:
                sas_file = data_path / f"{dataset_name}.sas7bdat"
                if sas_file.exists():
                    try:
                        df = read_sas(sas_file)
                        self.datasets[dataset_name.upper()] = {
                            'data': df,
                            'type': self._infer_dataset_type(dataset_name),
                            'source': str(sas_file),
                            'loaded_at': datetime.now()
                        }
                        print(f"✓ Loaded {dataset_name.upper()}: {len(df)} records")
                    except Exception as e:
                        warnings.warn(f"Failed to load {dataset_name}: {e}")
        
        if datasets:
            for name, source in datasets.items():
                if isinstance(source, pd.DataFrame):
                    df = source.copy()
                    source_info = "DataFrame"
                else:
                    df = load_dataset(source)
                    source_info = str(source)
                    
                self.datasets[name.upper()] = {
                    'data': df,
                    'type': self._infer_dataset_type(name),
                    'source': source_info,
                    'loaded_at': datetime.now()
                }
                print(f"✓ Loaded {name.upper()}: {len(df)} records")
        
        return self
        
    def define_populations(self, **populations) -> 'ReportSession':
        """
        Define analysis populations (equivalent to SAS population filters).
        
        Parameters
        ----------
        **populations
            Population definitions as keyword arguments
            (e.g., safety="SAFFL=='Y'", efficacy="EFFFL=='Y'")
            
        Returns
        -------
        ReportSession
            Self for method chaining
        """
        self.populations.update(populations)
        print(f"✓ Defined populations: {list(populations.keys())}")
        return self
        
    def define_treatments(self, var: str, decode: Optional[str] = None,
                         num_var: Optional[str] = None, **kwargs) -> 'ReportSession':
        """
        Define treatment variables for analysis.
        
        Parameters
        ----------
        var : str
            Treatment variable name (e.g., 'TRT01P')
        decode : str, optional
            Treatment decode variable (e.g., 'TRT01A')
        num_var : str, optional
            Numeric treatment variable (e.g., 'TRT01PN')
        **kwargs
            Additional treatment parameters
            
        Returns
        -------
        ReportSession
            Self for method chaining
        """
        # Get treatment levels from ADSL if available
        treatment_levels = []
        if 'ADSL' in self.datasets:
            adsl = self.datasets['ADSL']['data']
            if var in adsl.columns:
                treatment_levels = sorted(adsl[var].dropna().unique().tolist())
        
        self.treatments = {
            'variable': var,
            'decode': decode or var,
            'num_variable': num_var,
            'levels': treatment_levels,
            **kwargs
        }
        
        print(f"✓ Defined treatments: {var} with {len(treatment_levels)} levels")
        return self
        
    def add_variable(self, name: str, label: str = None, var_type: str = 'continuous',
                    statistics: List[str] = None, **kwargs) -> 'ReportSession':
        """
        Add a variable for analysis.
        
        Parameters
        ----------
        name : str
            Variable name
        label : str, optional
            Variable label for display
        var_type : str
            Variable type ('continuous', 'categorical', 'binary')
        statistics : list, optional
            List of statistics to calculate
        **kwargs
            Additional variable parameters
            
        Returns
        -------
        ReportSession
            Self for method chaining
        """
        var_id = len(self.variables) + 1
        
        self.variables[var_id] = {
            'name': name,
            'label': label or name,
            'type': var_type,
            'statistics': statistics or self._get_default_statistics(var_type),
            'order': var_id,
            **kwargs
        }
        
        return self
        
    def add_demographics_table(self, **kwargs) -> 'ReportSession':
        """Add demographics table."""
        return self._add_table('demographics', **kwargs)
        
    def add_disposition_table(self, **kwargs) -> 'ReportSession':
        """Add disposition table."""
        return self._add_table('disposition', **kwargs)
        
    def add_ae_summary(self, **kwargs) -> 'ReportSession':
        """Add adverse events summary table."""
        return self._add_table('ae_summary', **kwargs)
        
    def add_ae_detail(self, **kwargs) -> 'ReportSession':
        """Add detailed adverse events table."""
        return self._add_table('ae_detail', **kwargs)
        
    def add_efficacy_analysis(self, **kwargs) -> 'ReportSession':
        """Add efficacy analysis table."""
        return self._add_table('efficacy', **kwargs)
        
    def add_laboratory_analysis(self, **kwargs) -> 'ReportSession':
        """Add laboratory analysis tables."""
        return self._add_table('laboratory', **kwargs)
        
    def add_vital_signs_analysis(self, **kwargs) -> 'ReportSession':
        """Add vital signs analysis."""
        return self._add_table('vital_signs', **kwargs)
        
    def generate_all(self, output_dir: str = "output") -> 'ReportSession':
        """
        Generate all specified tables.
        
        Parameters
        ----------
        output_dir : str
            Output directory for generated files
            
        Returns
        -------
        ReportSession
            Self for method chaining
        """
        if not self.tables:
            warnings.warn("No tables defined for generation")
            return self
            
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print(f"\n🔄 Generating {len(self.tables)} tables...")
        
        for table_spec in self.tables:
            try:
                # Build table using TableBuilder
                builder = TableBuilder(self, table_spec)
                result = builder.build()
                
                # Generate outputs using configured generators
                for format_type in self.config.output_formats:
                    generator = OutputGeneratorFactory.create(format_type, self.config)
                    output_file = generator.generate(result, output_path)
                    self.generated_outputs.append(output_file)
                    
                print(f"✓ Generated {table_spec['type']}: {table_spec.get('title', 'Untitled')}")
                
            except Exception as e:
                print(f"✗ Failed to generate {table_spec['type']}: {e}")
                warnings.warn(f"Table generation failed: {e}")
        
        print(f"✓ Generated {len(self.generated_outputs)} output files")
        return self
        
    def finalize(self) -> 'ReportSessionResult':
        """
        Finalize report session and return results.
        
        Returns
        -------
        ReportSessionResult
            Final report results and summary
        """
        if self._finalized:
            warnings.warn("Session already finalized")
            
        self._finalized = True
        
        # Generate summary report
        summary = self._generate_session_summary()
        
        print("\n" + "="*60)
        print("REPORT SESSION COMPLETED")
        print("="*60)
        print(f"Study: {self.metadata.get('title', 'Unknown')}")
        print(f"URI: {self.metadata.get('uri', 'Unknown')}")
        print(f"Tables generated: {len(self.tables)}")
        print(f"Output files: {len(self.generated_outputs)}")
        print("="*60)
        
        return ReportSessionResult(
            session=self,
            summary=summary,
            generated_files=self.generated_outputs
        )
        
    def _add_table(self, table_type: str, **kwargs) -> 'ReportSession':
        """Internal method to add table specification."""
        self._current_table_id += 1
        
        table_spec = {
            'id': self._current_table_id,
            'type': table_type,
            'title': kwargs.get('title', self._get_default_title(table_type)),
            'subtitle': kwargs.get('subtitle', self._get_default_subtitle()),
            'population': kwargs.get('population', 'safety'),
            'footnotes': kwargs.get('footnotes', []),
            'variables': kwargs.get('variables', []),
            'statistics': kwargs.get('statistics', []),
            'filters': kwargs.get('filters', {}),
            **{k: v for k, v in kwargs.items() 
               if k not in ['title', 'subtitle', 'population', 'footnotes', 
                           'variables', 'statistics', 'filters']}
        }
        
        self.tables.append(table_spec)
        return self
        
    def _infer_dataset_type(self, name: str) -> str:
        """Infer dataset type from name."""
        name_lower = name.lower()
        if name_lower == 'adsl':
            return 'subject_level'
        elif name_lower.startswith('adae'):
            return 'adverse_events'
        elif name_lower.startswith('adlb'):
            return 'laboratory'
        elif name_lower.startswith('advs'):
            return 'vital_signs'
        elif name_lower.startswith('adtte'):
            return 'time_to_event'
        elif name_lower.startswith('adqs'):
            return 'questionnaire'
        else:
            return 'other'
            
    def _get_default_statistics(self, var_type: str) -> List[str]:
        """Get default statistics for variable type."""
        if var_type == 'continuous':
            return ['n', 'mean', 'std', 'median', 'min', 'max']
        elif var_type == 'categorical':
            return ['n', 'percent']
        elif var_type == 'binary':
            return ['n', 'percent']
        else:
            return ['n']
            
    def _get_default_title(self, table_type: str) -> str:
        """Get default title for table type."""
        titles = {
            'demographics': 'Baseline Demographics and Clinical Characteristics',
            'disposition': 'Subject Disposition',
            'ae_summary': 'Summary of Adverse Events',
            'ae_detail': 'Adverse Events by System Organ Class and Preferred Term',
            'efficacy': 'Efficacy Analysis',
            'laboratory': 'Laboratory Parameters',
            'vital_signs': 'Vital Signs'
        }
        return titles.get(table_type, f'{table_type.title()} Analysis')
        
    def _get_default_subtitle(self) -> str:
        """Get default subtitle based on current context."""
        return f"{self.metadata.get('title', 'Clinical Study')} - Safety Analysis Population"
        
    def _generate_session_summary(self) -> Dict[str, Any]:
        """Generate session summary."""
        return {
            'metadata': self.metadata,
            'datasets_loaded': len(self.datasets),
            'populations_defined': len(self.populations),
            'tables_generated': len(self.tables),
            'output_files': len(self.generated_outputs),
            'session_duration': datetime.now() - self.metadata.get('created_date', datetime.now()),
            'success': True
        }


class ReportSessionResult:
    """Result object from finalized report session."""
    
    def __init__(self, session: ReportSession, summary: Dict[str, Any], 
                 generated_files: List[Path]):
        self.session = session
        self.summary = summary
        self.generated_files = generated_files
        
    def __repr__(self):
        return f"ReportSessionResult(tables={len(self.session.tables)}, files={len(self.generated_files)})" 