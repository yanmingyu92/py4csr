"""
Plot result for py4csr functional plotting system.

This module defines the PlotResult class that holds generated plots
and associated metadata.
"""

from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.figure
from datetime import datetime


class PlotResult:
    """
    Result of plot generation.
    
    This class holds the generated plot figure, metadata, and provides
    methods for saving and managing plot outputs.
    """
    
    def __init__(self, 
                 figure: matplotlib.figure.Figure,
                 metadata: Dict[str, Any],
                 validation_results: Optional[Dict[str, Any]] = None):
        """
        Initialize plot result.
        
        Parameters
        ----------
        figure : matplotlib.figure.Figure
            Generated plot figure
        metadata : dict
            Plot metadata
        validation_results : dict, optional
            Data validation results
        """
        self.figure = figure
        self.metadata = metadata
        self.validation_results = validation_results or {}
        self.file_paths = {}
        
    def save(self, filepath: Union[str, Path], 
             formats: Optional[List[str]] = None,
             **kwargs) -> Dict[str, str]:
        """
        Save plot to file(s).
        
        Parameters
        ----------
        filepath : str or Path
            Base filepath (without extension)
        formats : list, optional
            Output formats (e.g., ['png', 'pdf'])
        **kwargs
            Additional arguments for matplotlib savefig
            
        Returns
        -------
        dict
            Dictionary mapping format to saved filepath
        """
        if formats is None:
            formats = ['png', 'pdf']
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        saved_files = {}
        
        # Default save parameters
        save_params = {
            'dpi': 300,
            'bbox_inches': 'tight',
            'facecolor': 'white',
            'edgecolor': 'none'
        }
        save_params.update(kwargs)
        
        for fmt in formats:
            output_path = filepath.with_suffix(f'.{fmt}')
            self.figure.savefig(output_path, format=fmt, **save_params)
            saved_files[fmt] = str(output_path)
            self.file_paths[fmt] = str(output_path)
        
        return saved_files
    
    def show(self):
        """Display the plot."""
        plt.figure(self.figure.number)
        plt.show()
    
    def close(self):
        """Close the plot figure to free memory."""
        plt.close(self.figure)
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get plot metadata."""
        return self.metadata.copy()
    
    def get_file_summary(self) -> Dict[str, Any]:
        """Get summary of saved files."""
        total_size = 0
        file_details = {}
        
        for fmt, filepath in self.file_paths.items():
            path = Path(filepath)
            if path.exists():
                size_mb = path.stat().st_size / (1024 * 1024)
                total_size += size_mb
                file_details[fmt] = {
                    'path': str(path),
                    'size_mb': size_mb,
                    'exists': True
                }
            else:
                file_details[fmt] = {
                    'path': str(path),
                    'size_mb': 0,
                    'exists': False
                }
        
        return {
            'total_files': len(self.file_paths),
            'total_size_mb': total_size,
            'files': file_details
        }
    
    def print_summary(self):
        """Print a summary of the plot result."""
        print(f"Plot Type: {self.metadata.get('plot_type', 'Unknown')}")
        print(f"Title: {self.metadata.get('title', 'No title')}")
        print(f"Generation Time: {self.metadata.get('generation_time', 'Unknown')}")
        
        if self.file_paths:
            print("Saved Files:")
            for fmt, path in self.file_paths.items():
                print(f"  {fmt.upper()}: {path}")
        
        if self.validation_results and not self.validation_results.get('passed', True):
            print("Validation Issues:")
            for error in self.validation_results.get('errors', []):
                print(f"  Error: {error}")
            for warning in self.validation_results.get('warnings', []):
                print(f"  Warning: {warning}")


class PlotCollection:
    """
    Collection of multiple plot results.
    
    This class manages multiple plots generated as part of a complete
    plotting session or report.
    """
    
    def __init__(self):
        """Initialize empty plot collection."""
        self.plots = {}
        self.metadata = {
            'creation_time': datetime.now(),
            'total_plots': 0
        }
    
    def add_plot(self, name: str, plot_result: PlotResult):
        """
        Add a plot to the collection.
        
        Parameters
        ----------
        name : str
            Plot identifier
        plot_result : PlotResult
            Plot result to add
        """
        self.plots[name] = plot_result
        self.metadata['total_plots'] = len(self.plots)
    
    def get_plot(self, name: str) -> Optional[PlotResult]:
        """
        Get a plot by name.
        
        Parameters
        ----------
        name : str
            Plot identifier
            
        Returns
        -------
        PlotResult or None
            Plot result if found
        """
        return self.plots.get(name)
    
    def list_plots(self) -> List[str]:
        """Get list of plot names."""
        return list(self.plots.keys())
    
    def save_all(self, output_dir: Union[str, Path], 
                 formats: Optional[List[str]] = None) -> Dict[str, Dict[str, str]]:
        """
        Save all plots to directory.
        
        Parameters
        ----------
        output_dir : str or Path
            Output directory
        formats : list, optional
            Output formats
            
        Returns
        -------
        dict
            Dictionary mapping plot name to saved files
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        saved_files = {}
        
        for name, plot_result in self.plots.items():
            filepath = output_dir / name
            saved_files[name] = plot_result.save(filepath, formats)
        
        return saved_files
    
    def close_all(self):
        """Close all plot figures to free memory."""
        for plot_result in self.plots.values():
            plot_result.close()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all plots."""
        total_files = 0
        total_size = 0
        plot_summaries = {}
        
        for name, plot_result in self.plots.items():
            file_summary = plot_result.get_file_summary()
            total_files += file_summary['total_files']
            total_size += file_summary['total_size_mb']
            plot_summaries[name] = file_summary
        
        return {
            'total_plots': len(self.plots),
            'total_files': total_files,
            'total_size_mb': total_size,
            'plots': plot_summaries,
            'creation_time': self.metadata['creation_time']
        }
    
    def print_summary(self):
        """Print summary of all plots."""
        print(f"Plot Collection Summary:")
        print(f"Total Plots: {len(self.plots)}")
        
        summary = self.get_summary()
        print(f"Total Files: {summary['total_files']}")
        print(f"Total Size: {summary['total_size_mb']:.2f} MB")
        
        print("\nIndividual Plots:")
        for name, plot_result in self.plots.items():
            plot_type = plot_result.metadata.get('plot_type', 'Unknown')
            print(f"  {name}: {plot_type}") 