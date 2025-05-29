"""
Advanced Features for Functional Clinical Reporting

This module provides advanced functionality equivalent to SAS RRG advanced features
like grouping variables, conditional formatting, custom code injection, etc.
"""

from typing import Dict, List, Optional, Any, Callable, Union
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import re
from pathlib import Path

from .config import FunctionalConfig


@dataclass
class GroupingSpecification:
    """
    Grouping variable specification (equivalent to SAS RRG %rrg_addgroup).
    
    Defines how variables should be grouped and displayed in tables.
    """
    name: str
    label: str = ""
    decode: str = ""
    across: bool = True
    sort_order: str = "ascending"
    total_text: str = "Total"
    show_total: bool = True
    indent_subgroups: bool = True
    page_break: bool = False
    custom_order: List[str] = field(default_factory=list)


@dataclass
class ConditionalFormat:
    """
    Conditional formatting specification (equivalent to SAS RRG %rrg_addcond).
    
    Defines conditional formatting rules for table cells.
    """
    name: str
    condition: str  # Python expression
    format_type: str  # 'highlight', 'bold', 'italic', 'color', 'custom'
    format_value: str  # Color, style, or custom format string
    applies_to: List[str] = field(default_factory=list)  # Statistics to apply to
    description: str = ""


@dataclass
class CustomLabel:
    """
    Custom label specification (equivalent to SAS RRG %rrg_addlabel).
    
    Defines custom labels and formatting for table rows.
    """
    name: str
    label: str
    position: str = "after"  # 'before', 'after', 'replace'
    indent: int = 0
    skip_line: bool = True
    bold: bool = False
    italic: bool = False
    custom_style: str = ""


class CodeHook(ABC):
    """
    Base class for custom code hooks (equivalent to SAS RRG %rrg_codebefore/%rrg_codeafter).
    
    Allows injection of custom processing logic at various points in the workflow.
    """
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the custom code hook."""
        pass


class DataTransformHook(CodeHook):
    """Hook for custom data transformations."""
    
    def __init__(self, transform_function: Callable[[pd.DataFrame], pd.DataFrame]):
        self.transform_function = transform_function
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data transformation."""
        if 'data' in context:
            context['data'] = self.transform_function(context['data'])
        return context


class StatisticHook(CodeHook):
    """Hook for custom statistic calculations."""
    
    def __init__(self, statistic_function: Callable[[pd.DataFrame], Dict[str, Any]]):
        self.statistic_function = statistic_function
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute custom statistic calculation."""
        if 'data' in context:
            custom_stats = self.statistic_function(context['data'])
            context.setdefault('custom_statistics', {}).update(custom_stats)
        return context


class FormattingHook(CodeHook):
    """Hook for custom formatting logic."""
    
    def __init__(self, formatting_function: Callable[[pd.DataFrame], pd.DataFrame]):
        self.formatting_function = formatting_function
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute custom formatting."""
        if 'table_data' in context:
            context['table_data'] = self.formatting_function(context['table_data'])
        return context


class AdvancedGroupingEngine:
    """
    Advanced grouping engine (equivalent to SAS RRG grouping functionality).
    
    Handles complex grouping scenarios with multiple levels, custom ordering,
    and sophisticated display logic.
    """
    
    def __init__(self, config: FunctionalConfig):
        self.config = config
        self.grouping_specs: Dict[str, GroupingSpecification] = {}
    
    def add_grouping(self, spec: GroupingSpecification) -> 'AdvancedGroupingEngine':
        """Add a grouping specification."""
        self.grouping_specs[spec.name] = spec
        return self
    
    def apply_grouping(self, data: pd.DataFrame, statistics_df: pd.DataFrame,
                      grouping_vars: List[str]) -> pd.DataFrame:
        """
        Apply grouping to statistics data.
        
        Parameters
        ----------
        data : pd.DataFrame
            Original data
        statistics_df : pd.DataFrame
            Statistics results
        grouping_vars : list
            List of grouping variables
            
        Returns
        -------
        pd.DataFrame
            Grouped and formatted statistics
        """
        if not grouping_vars:
            return statistics_df
        
        grouped_results = []
        
        # Process each grouping variable
        for group_var in grouping_vars:
            if group_var not in self.grouping_specs:
                continue
                
            spec = self.grouping_specs[group_var]
            
            # Get unique group values
            if group_var in data.columns:
                group_values = self._get_ordered_group_values(data[group_var], spec)
                
                for group_value in group_values:
                    # Filter data for this group
                    group_data = data[data[group_var] == group_value]
                    
                    if len(group_data) == 0:
                        continue
                    
                    # Add group header
                    group_header = self._create_group_header(group_value, spec)
                    grouped_results.append(group_header)
                    
                    # Add statistics for this group
                    group_stats = statistics_df.copy()
                    group_stats['GROUP_VALUE'] = group_value
                    group_stats['GROUP_VAR'] = group_var
                    
                    if spec.indent_subgroups:
                        group_stats['INDENT'] = group_stats.get('INDENT', 0) + 1
                    
                    grouped_results.append(group_stats)
                    
                    # Add page break if specified
                    if spec.page_break:
                        page_break_row = pd.DataFrame([{
                            'PARAMETER': '__PAGE_BREAK__',
                            'STATISTIC': '',
                            'FORMATTED_VALUE': ''
                        }])
                        grouped_results.append(page_break_row)
                
                # Add total if specified
                if spec.show_total:
                    total_header = self._create_group_header(spec.total_text, spec, is_total=True)
                    grouped_results.append(total_header)
                    
                    total_stats = statistics_df.copy()
                    total_stats['GROUP_VALUE'] = 'Total'
                    total_stats['GROUP_VAR'] = group_var
                    grouped_results.append(total_stats)
        
        if grouped_results:
            return pd.concat(grouped_results, ignore_index=True)
        else:
            return statistics_df
    
    def _get_ordered_group_values(self, series: pd.Series, spec: GroupingSpecification) -> List:
        """Get group values in specified order."""
        unique_values = series.unique()
        
        if spec.custom_order:
            # Use custom order, then add any remaining values
            ordered_values = []
            for value in spec.custom_order:
                if value in unique_values:
                    ordered_values.append(value)
            
            # Add remaining values
            for value in unique_values:
                if value not in ordered_values:
                    ordered_values.append(value)
            
            return ordered_values
        
        elif spec.sort_order == "ascending":
            return sorted(unique_values)
        elif spec.sort_order == "descending":
            return sorted(unique_values, reverse=True)
        else:
            return list(unique_values)
    
    def _create_group_header(self, group_value: str, spec: GroupingSpecification,
                           is_total: bool = False) -> pd.DataFrame:
        """Create group header row."""
        label = spec.label if spec.label else spec.name
        display_value = f"{label}: {group_value}" if not is_total else group_value
        
        return pd.DataFrame([{
            'PARAMETER': display_value,
            'STATISTIC': '__GROUP_HEADER__',
            'FORMATTED_VALUE': '',
            'GROUP_VAR': spec.name,
            'GROUP_VALUE': group_value,
            'IS_TOTAL': is_total,
            'INDENT': 0
        }])


class ConditionalFormattingEngine:
    """
    Conditional formatting engine (equivalent to SAS RRG conditional formatting).
    
    Applies conditional formatting rules to table cells based on data values.
    """
    
    def __init__(self, config: FunctionalConfig):
        self.config = config
        self.format_rules: Dict[str, ConditionalFormat] = {}
    
    def add_format_rule(self, rule: ConditionalFormat) -> 'ConditionalFormattingEngine':
        """Add a conditional formatting rule."""
        self.format_rules[rule.name] = rule
        return self
    
    def apply_formatting(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Apply conditional formatting to data.
        
        Parameters
        ----------
        data : pd.DataFrame
            Data to format
            
        Returns
        -------
        pd.DataFrame
            Data with formatting applied
        """
        formatted_data = data.copy()
        
        # Add formatting columns
        formatted_data['CELL_FORMAT'] = ''
        formatted_data['CELL_STYLE'] = ''
        formatted_data['CELL_COLOR'] = ''
        
        for rule_name, rule in self.format_rules.items():
            # Apply rule to each row
            for idx, row in formatted_data.iterrows():
                if self._evaluate_condition(rule.condition, row):
                    # Apply formatting based on rule type
                    if rule.format_type == 'highlight':
                        formatted_data.at[idx, 'CELL_COLOR'] = rule.format_value
                    elif rule.format_type == 'bold':
                        formatted_data.at[idx, 'CELL_STYLE'] += 'bold;'
                    elif rule.format_type == 'italic':
                        formatted_data.at[idx, 'CELL_STYLE'] += 'italic;'
                    elif rule.format_type == 'color':
                        formatted_data.at[idx, 'CELL_COLOR'] = rule.format_value
                    elif rule.format_type == 'custom':
                        formatted_data.at[idx, 'CELL_FORMAT'] = rule.format_value
        
        return formatted_data
    
    def _evaluate_condition(self, condition: str, row: pd.Series) -> bool:
        """
        Evaluate conditional formatting condition.
        
        Parameters
        ----------
        condition : str
            Python expression to evaluate
        row : pd.Series
            Data row
            
        Returns
        -------
        bool
            Whether condition is met
        """
        try:
            # Create safe evaluation context
            context = {
                'value': row.get('VALUE', 0),
                'formatted_value': row.get('FORMATTED_VALUE', ''),
                'statistic': row.get('STATISTIC', ''),
                'parameter': row.get('PARAMETER', ''),
                'treatment': row.get('TREATMENT', ''),
                'np': np,
                'pd': pd
            }
            
            # Add all row values to context
            for col, val in row.items():
                if isinstance(col, str) and col.isidentifier():
                    context[col.lower()] = val
            
            return bool(eval(condition, {"__builtins__": {}}, context))
        
        except Exception:
            return False


class CustomLabelEngine:
    """
    Custom label engine (equivalent to SAS RRG %rrg_addlabel).
    
    Manages custom labels and their positioning in tables.
    """
    
    def __init__(self, config: FunctionalConfig):
        self.config = config
        self.custom_labels: Dict[str, CustomLabel] = {}
    
    def add_label(self, label: CustomLabel) -> 'CustomLabelEngine':
        """Add a custom label."""
        self.custom_labels[label.name] = label
        return self
    
    def apply_labels(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Apply custom labels to data.
        
        Parameters
        ----------
        data : pd.DataFrame
            Data to apply labels to
            
        Returns
        -------
        pd.DataFrame
            Data with custom labels applied
        """
        result_data = []
        
        for idx, row in data.iterrows():
            # Check if any custom labels apply to this row
            applicable_labels = self._get_applicable_labels(row)
            
            # Add "before" labels
            for label in applicable_labels:
                if label.position == "before":
                    label_row = self._create_label_row(label, row)
                    result_data.append(label_row)
            
            # Add original row (or replace if specified)
            replace_labels = [l for l in applicable_labels if l.position == "replace"]
            if replace_labels:
                # Use the last replace label
                label_row = self._create_label_row(replace_labels[-1], row)
                result_data.append(label_row)
            else:
                result_data.append(row.to_dict())
            
            # Add "after" labels
            for label in applicable_labels:
                if label.position == "after":
                    label_row = self._create_label_row(label, row)
                    result_data.append(label_row)
        
        return pd.DataFrame(result_data)
    
    def _get_applicable_labels(self, row: pd.Series) -> List[CustomLabel]:
        """Get custom labels that apply to this row."""
        applicable = []
        
        for label in self.custom_labels.values():
            # Simple matching - could be enhanced with more sophisticated logic
            if label.name in str(row.get('PARAMETER', '')):
                applicable.append(label)
        
        return applicable
    
    def _create_label_row(self, label: CustomLabel, original_row: pd.Series) -> Dict[str, Any]:
        """Create a row for a custom label."""
        label_row = original_row.to_dict()
        label_row['PARAMETER'] = label.label
        label_row['STATISTIC'] = '__CUSTOM_LABEL__'
        label_row['FORMATTED_VALUE'] = ''
        label_row['INDENT'] = label.indent
        label_row['SKIP_LINE'] = label.skip_line
        label_row['BOLD'] = label.bold
        label_row['ITALIC'] = label.italic
        label_row['CUSTOM_STYLE'] = label.custom_style
        
        return label_row


class CodeHookManager:
    """
    Code hook manager (equivalent to SAS RRG %rrg_codebefore/%rrg_codeafter).
    
    Manages custom code hooks that can be executed at various points
    in the reporting workflow.
    """
    
    def __init__(self, config: FunctionalConfig):
        self.config = config
        self.hooks: Dict[str, List[CodeHook]] = {
            'before_data_load': [],
            'after_data_load': [],
            'before_statistics': [],
            'after_statistics': [],
            'before_formatting': [],
            'after_formatting': [],
            'before_output': [],
            'after_output': []
        }
    
    def add_hook(self, hook_point: str, hook: CodeHook) -> 'CodeHookManager':
        """
        Add a code hook at specified point.
        
        Parameters
        ----------
        hook_point : str
            When to execute the hook
        hook : CodeHook
            Hook to execute
            
        Returns
        -------
        CodeHookManager
            Self for method chaining
        """
        if hook_point not in self.hooks:
            raise ValueError(f"Unknown hook point: {hook_point}")
        
        self.hooks[hook_point].append(hook)
        return self
    
    def execute_hooks(self, hook_point: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute all hooks at specified point.
        
        Parameters
        ----------
        hook_point : str
            Hook point to execute
        context : dict
            Execution context
            
        Returns
        -------
        dict
            Updated context
        """
        if hook_point not in self.hooks:
            return context
        
        for hook in self.hooks[hook_point]:
            try:
                context = hook.execute(context)
            except Exception as e:
                print(f"Warning: Hook execution failed at {hook_point}: {e}")
        
        return context
    
    def add_data_transform(self, hook_point: str, 
                          transform_func: Callable[[pd.DataFrame], pd.DataFrame]) -> 'CodeHookManager':
        """Add a data transformation hook."""
        hook = DataTransformHook(transform_func)
        return self.add_hook(hook_point, hook)
    
    def add_statistic_hook(self, hook_point: str,
                          statistic_func: Callable[[pd.DataFrame], Dict[str, Any]]) -> 'CodeHookManager':
        """Add a custom statistic hook."""
        hook = StatisticHook(statistic_func)
        return self.add_hook(hook_point, hook)
    
    def add_formatting_hook(self, hook_point: str,
                           formatting_func: Callable[[pd.DataFrame], pd.DataFrame]) -> 'CodeHookManager':
        """Add a formatting hook."""
        hook = FormattingHook(formatting_func)
        return self.add_hook(hook_point, hook)


class DatasetJoiner:
    """
    Dataset joining utility (equivalent to SAS RRG %rrg_joinds).
    
    Provides sophisticated dataset joining capabilities for clinical data.
    """
    
    def __init__(self, config: FunctionalConfig):
        self.config = config
    
    def join_datasets(self, left_ds: pd.DataFrame, right_ds: pd.DataFrame,
                     join_type: str = 'left', join_keys: List[str] = None,
                     suffixes: tuple = ('_left', '_right')) -> pd.DataFrame:
        """
        Join two datasets with clinical data considerations.
        
        Parameters
        ----------
        left_ds : pd.DataFrame
            Left dataset
        right_ds : pd.DataFrame
            Right dataset
        join_type : str
            Type of join ('left', 'right', 'inner', 'outer')
        join_keys : list
            Keys to join on
        suffixes : tuple
            Suffixes for overlapping columns
            
        Returns
        -------
        pd.DataFrame
            Joined dataset
        """
        # Default join keys for clinical data
        if join_keys is None:
            # Try common clinical join keys
            common_keys = ['USUBJID', 'SUBJID', 'STUDYID']
            join_keys = []
            
            for key in common_keys:
                if key in left_ds.columns and key in right_ds.columns:
                    join_keys.append(key)
            
            if not join_keys:
                raise ValueError("No common join keys found between datasets")
        
        # Perform join
        if join_type == 'left':
            result = left_ds.merge(right_ds, on=join_keys, how='left', suffixes=suffixes)
        elif join_type == 'right':
            result = left_ds.merge(right_ds, on=join_keys, how='right', suffixes=suffixes)
        elif join_type == 'inner':
            result = left_ds.merge(right_ds, on=join_keys, how='inner', suffixes=suffixes)
        elif join_type == 'outer':
            result = left_ds.merge(right_ds, on=join_keys, how='outer', suffixes=suffixes)
        else:
            raise ValueError(f"Unknown join type: {join_type}")
        
        return result
    
    def smart_join(self, datasets: Dict[str, pd.DataFrame], 
                  join_hierarchy: List[str] = None) -> pd.DataFrame:
        """
        Smart join multiple datasets based on clinical data relationships.
        
        Parameters
        ----------
        datasets : dict
            Dictionary of datasets to join
        join_hierarchy : list
            Order of datasets to join (if None, uses smart ordering)
            
        Returns
        -------
        pd.DataFrame
            Joined dataset
        """
        if not datasets:
            raise ValueError("No datasets provided")
        
        if len(datasets) == 1:
            return list(datasets.values())[0]
        
        # Determine join order if not provided
        if join_hierarchy is None:
            join_hierarchy = self._determine_join_order(datasets)
        
        # Start with first dataset
        result = datasets[join_hierarchy[0]]
        
        # Join remaining datasets
        for ds_name in join_hierarchy[1:]:
            if ds_name in datasets:
                result = self.join_datasets(result, datasets[ds_name])
        
        return result
    
    def _determine_join_order(self, datasets: Dict[str, pd.DataFrame]) -> List[str]:
        """Determine optimal join order for clinical datasets."""
        # Clinical dataset hierarchy (most comprehensive first)
        clinical_hierarchy = ['ADSL', 'ADAE', 'ADLB', 'ADVS', 'ADTTE', 'ADCM']
        
        ordered_names = []
        
        # Add datasets in clinical hierarchy order
        for ds_type in clinical_hierarchy:
            for ds_name in datasets.keys():
                if ds_type in ds_name.upper() and ds_name not in ordered_names:
                    ordered_names.append(ds_name)
        
        # Add remaining datasets
        for ds_name in datasets.keys():
            if ds_name not in ordered_names:
                ordered_names.append(ds_name)
        
        return ordered_names


class AdvancedFeaturesManager:
    """
    Manager for all advanced features (equivalent to SAS RRG advanced functionality).
    
    Coordinates grouping, conditional formatting, custom labels, and code hooks.
    """
    
    def __init__(self, config: FunctionalConfig):
        self.config = config
        self.grouping_engine = AdvancedGroupingEngine(config)
        self.formatting_engine = ConditionalFormattingEngine(config)
        self.label_engine = CustomLabelEngine(config)
        self.hook_manager = CodeHookManager(config)
        self.dataset_joiner = DatasetJoiner(config)
    
    def add_grouping(self, **kwargs) -> 'AdvancedFeaturesManager':
        """Add grouping specification."""
        spec = GroupingSpecification(**kwargs)
        self.grouping_engine.add_grouping(spec)
        return self
    
    def add_conditional_format(self, **kwargs) -> 'AdvancedFeaturesManager':
        """Add conditional formatting rule."""
        rule = ConditionalFormat(**kwargs)
        self.formatting_engine.add_format_rule(rule)
        return self
    
    def add_custom_label(self, **kwargs) -> 'AdvancedFeaturesManager':
        """Add custom label."""
        label = CustomLabel(**kwargs)
        self.label_engine.add_label(label)
        return self
    
    def add_hook(self, hook_point: str, hook: CodeHook) -> 'AdvancedFeaturesManager':
        """Add code hook."""
        self.hook_manager.add_hook(hook_point, hook)
        return self
    
    def process_table_data(self, data: pd.DataFrame, statistics_df: pd.DataFrame,
                          grouping_vars: List[str] = None, 
                          context: Dict[str, Any] = None) -> pd.DataFrame:
        """
        Process table data with all advanced features.
        
        Parameters
        ----------
        data : pd.DataFrame
            Original data
        statistics_df : pd.DataFrame
            Statistics results
        grouping_vars : list
            Grouping variables
        context : dict
            Processing context
            
        Returns
        -------
        pd.DataFrame
            Processed table data
        """
        if context is None:
            context = {}
        
        context['data'] = data
        context['statistics_df'] = statistics_df
        
        # Execute before formatting hooks
        context = self.hook_manager.execute_hooks('before_formatting', context)
        
        # Apply grouping
        if grouping_vars:
            processed_data = self.grouping_engine.apply_grouping(
                context['data'], context['statistics_df'], grouping_vars
            )
        else:
            processed_data = context['statistics_df']
        
        # Apply custom labels
        processed_data = self.label_engine.apply_labels(processed_data)
        
        # Apply conditional formatting
        processed_data = self.formatting_engine.apply_formatting(processed_data)
        
        context['table_data'] = processed_data
        
        # Execute after formatting hooks
        context = self.hook_manager.execute_hooks('after_formatting', context)
        
        return context['table_data'] 