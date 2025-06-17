"""
Table generator factory for py4csr functional reporting system.

This module provides the factory pattern for creating table generators,
similar to the SAS RRG system's template selection mechanism.
"""

from typing import Dict, Type, Optional
from .base_generator import BaseTableGenerator


class TableGeneratorFactory:
    """
    Factory for creating table generators.
    
    This class manages the registry of available table generators and
    creates instances on demand based on table type.
    """
    
    _generators: Dict[str, Type[BaseTableGenerator]] = {}
    
    @classmethod
    def register(cls, table_type: str, generator_class: Type[BaseTableGenerator]) -> None:
        """
        Register a generator class for a table type.
        
        Parameters
        ----------
        table_type : str
            Type of table (e.g., 'demographics', 'ae_summary')
        generator_class : type
            Generator class to register
        """
        cls._generators[table_type] = generator_class
    
    @classmethod
    def create(cls, table_type: str) -> BaseTableGenerator:
        """
        Create generator for specified table type.
        
        Parameters
        ----------
        table_type : str
            Type of table to generate
            
        Returns
        -------
        BaseTableGenerator
            Generator instance for the table type
            
        Raises
        ------
        ValueError
            If table type is not registered
        """
        if table_type not in cls._generators:
            # Try to import and register common generators
            cls._register_default_generators()
            
            if table_type not in cls._generators:
                available_types = list(cls._generators.keys())
                raise ValueError(
                    f"Unknown table type: '{table_type}'. "
                    f"Available types: {available_types}"
                )
        
        generator_class = cls._generators[table_type]
        return generator_class()
    
    @classmethod
    def list_available_types(cls) -> list:
        """
        List all available table types.
        
        Returns
        -------
        list
            Available table type names
        """
        cls._register_default_generators()
        return list(cls._generators.keys())
    
    @classmethod
    def is_registered(cls, table_type: str) -> bool:
        """
        Check if a table type is registered.
        
        Parameters
        ----------
        table_type : str
            Table type to check
            
        Returns
        -------
        bool
            True if registered, False otherwise
        """
        return table_type in cls._generators
    
    @classmethod
    def _register_default_generators(cls) -> None:
        """Register default generators if not already registered."""
        if cls._generators:
            return  # Already registered
        
        try:
            # Import and register all default generators
            from .demographics_generator import DemographicsGenerator
            from .disposition_generator import DispositionGenerator
            from .ae_summary_generator import AESummaryGenerator
            from .ae_detail_generator import AEDetailGenerator
            from .efficacy_generator import EfficacyGenerator
            from .laboratory_generator import LaboratoryGenerator
            from .survival_generator import SurvivalGenerator
            from .vital_signs_generator import VitalSignsGenerator
            from .concomitant_meds_generator import ConcomitantMedsGenerator
            from .medical_history_generator import MedicalHistoryGenerator
            from .exposure_generator import ExposureGenerator
            
            # Register all generators
            cls.register('demographics', DemographicsGenerator)
            cls.register('disposition', DispositionGenerator)
            cls.register('ae_summary', AESummaryGenerator)
            cls.register('ae_detail', AEDetailGenerator)
            cls.register('efficacy', EfficacyGenerator)
            cls.register('laboratory', LaboratoryGenerator)
            cls.register('survival', SurvivalGenerator)
            cls.register('vital_signs', VitalSignsGenerator)
            cls.register('concomitant_meds', ConcomitantMedsGenerator)
            cls.register('medical_history', MedicalHistoryGenerator)
            cls.register('exposure', ExposureGenerator)
            
        except ImportError:
            # Some generators may not be implemented yet
            # Register the ones that are available
            try:
                from .demographics_generator import DemographicsGenerator
                cls.register('demographics', DemographicsGenerator)
            except ImportError:
                pass
            
            try:
                from .disposition_generator import DispositionGenerator
                cls.register('disposition', DispositionGenerator)
            except ImportError:
                pass
            
            try:
                from .ae_summary_generator import AESummaryGenerator
                cls.register('ae_summary', AESummaryGenerator)
            except ImportError:
                pass
            
            try:
                from .ae_detail_generator import AEDetailGenerator
                cls.register('ae_detail', AEDetailGenerator)
            except ImportError:
                pass
            
            try:
                from .efficacy_generator import EfficacyGenerator
                cls.register('efficacy', EfficacyGenerator)
            except ImportError:
                pass
            
            try:
                from .laboratory_generator import LaboratoryGenerator
                cls.register('laboratory', LaboratoryGenerator)
            except ImportError:
                pass
            
            try:
                from .survival_generator import SurvivalGenerator
                cls.register('survival', SurvivalGenerator)
            except ImportError:
                pass 