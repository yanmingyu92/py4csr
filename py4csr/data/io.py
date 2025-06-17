"""
Input/Output functions for clinical trial datasets.

This module provides functions for reading various clinical data formats
including SAS (.sas7bdat), XPT, and other common formats.
"""

import pandas as pd
import pyreadstat
from pathlib import Path
from typing import Optional, Union, Dict, Any
import warnings


def read_sas(filepath: Union[str, Path], 
             encoding: Optional[str] = None,
             **kwargs) -> pd.DataFrame:
    """
    Read a SAS dataset (.sas7bdat) file.
    
    This function provides a unified interface for reading SAS datasets,
    which are commonly used in clinical trials following CDISC standards.
    
    Parameters
    ----------
    filepath : str or Path
        Path to the SAS dataset file
    encoding : str, optional
        Character encoding for the file (default: None for auto-detection)
    **kwargs
        Additional arguments passed to pyreadstat.read_sas7bdat
        
    Returns
    -------
    pd.DataFrame
        DataFrame containing the clinical data
        
    Examples
    --------
    >>> adsl = read_sas("data/adsl.sas7bdat")
    >>> adae = read_sas("data/adae.sas7bdat", encoding="utf-8")
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
        
    if not filepath.suffix.lower() == '.sas7bdat':
        warnings.warn(f"Expected .sas7bdat file, got {filepath.suffix}")
    
    try:
        df, meta = pyreadstat.read_sas7bdat(str(filepath), encoding=encoding, **kwargs)
        
        # Store metadata as DataFrame attributes
        if hasattr(df, 'attrs'):
            df.attrs['variable_labels'] = meta.column_labels or {}
            df.attrs['value_labels'] = meta.variable_value_labels or {}
            df.attrs['source_file'] = str(filepath)
            
        return df
        
    except Exception as e:
        raise RuntimeError(f"Error reading SAS file {filepath}: {str(e)}")


def read_xpt(filepath: Union[str, Path], 
             encoding: Optional[str] = None,
             **kwargs) -> pd.DataFrame:
    """
    Read an XPT (SAS Transport) file.
    
    Parameters
    ----------
    filepath : str or Path
        Path to the XPT file
    encoding : str, optional
        Character encoding for the file
    **kwargs
        Additional arguments passed to pyreadstat.read_xport
        
    Returns
    -------
    pd.DataFrame
        DataFrame containing the clinical data
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
        
    try:
        df, meta = pyreadstat.read_xport(str(filepath), encoding=encoding, **kwargs)
        
        # Store metadata as DataFrame attributes
        if hasattr(df, 'attrs'):
            df.attrs['variable_labels'] = meta.column_labels or {}
            df.attrs['value_labels'] = meta.variable_value_labels or {}
            df.attrs['source_file'] = str(filepath)
            
        return df
        
    except Exception as e:
        raise RuntimeError(f"Error reading XPT file {filepath}: {str(e)}")


def load_dataset(filepath: Union[str, Path], 
                 dataset_type: Optional[str] = None,
                 **kwargs) -> pd.DataFrame:
    """
    Load a clinical dataset with automatic format detection.
    
    This function automatically detects the file format and uses the
    appropriate reader function.
    
    Parameters
    ----------
    filepath : str or Path
        Path to the dataset file
    dataset_type : str, optional
        Force a specific dataset type ('sas', 'xpt', 'csv', 'excel')
    **kwargs
        Additional arguments passed to the specific reader
        
    Returns
    -------
    pd.DataFrame
        DataFrame containing the clinical data
        
    Examples
    --------
    >>> # Automatic detection
    >>> adsl = load_dataset("data/adsl.sas7bdat")
    >>> 
    >>> # Force specific type
    >>> adae = load_dataset("data/adae.csv", dataset_type="csv")
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    # Determine file type
    if dataset_type is None:
        suffix = filepath.suffix.lower()
        if suffix == '.sas7bdat':
            dataset_type = 'sas'
        elif suffix == '.xpt':
            dataset_type = 'xpt'
        elif suffix == '.csv':
            dataset_type = 'csv'
        elif suffix in ['.xlsx', '.xls']:
            dataset_type = 'excel'
        else:
            raise ValueError(f"Cannot determine dataset type for file: {filepath}")
    
    # Load using appropriate function
    if dataset_type == 'sas':
        return read_sas(filepath, **kwargs)
    elif dataset_type == 'xpt':
        return read_xpt(filepath, **kwargs)
    elif dataset_type == 'csv':
        df = pd.read_csv(filepath, **kwargs)
    elif dataset_type == 'excel':
        df = pd.read_excel(filepath, **kwargs)
    else:
        raise ValueError(f"Unsupported dataset type: {dataset_type}")
    
    # Add source file attribute
    if hasattr(df, 'attrs'):
        df.attrs['source_file'] = str(filepath)
    
    return df


def get_dataset_info(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get information about a clinical dataset.
    
    Parameters
    ----------
    df : pd.DataFrame
        Clinical dataset
        
    Returns
    -------
    dict
        Dictionary containing dataset information
    """
    info = {
        'shape': df.shape,
        'columns': list(df.columns),
        'dtypes': df.dtypes.to_dict(),
        'missing_counts': df.isnull().sum().to_dict(),
        'source_file': getattr(df, 'attrs', {}).get('source_file', 'Unknown')
    }
    
    # Add variable labels if available
    attrs = getattr(df, 'attrs', {})
    if 'variable_labels' in attrs:
        info['variable_labels'] = attrs['variable_labels']
    
    return info 


def read_xpt(file_path: str) -> pd.DataFrame:
    """
    Read SAS transport (XPT) file.
    
    Parameters
    ----------
    file_path : str
        Path to the XPT file
        
    Returns
    -------
    pd.DataFrame
        Data from XPT file
    """
    try:
        import pyreadstat
        df, meta = pyreadstat.read_xport(file_path)
        return df
    except ImportError:
        raise ImportError("pyreadstat package is required to read XPT files. Install with: pip install pyreadstat")
    except Exception as e:
        print(f"Error reading XPT file {file_path}: {e}")
        return pd.DataFrame()


def load_adam_data(data_dir: str, datasets: list = None) -> Dict[str, pd.DataFrame]:
    """
    Load multiple ADAM datasets from a directory.
    
    Parameters
    ----------
    data_dir : str
        Directory containing ADAM datasets
    datasets : list, optional
        List of dataset names to load (e.g., ['adsl', 'adae', 'adlb'])
        If None, attempts to load common ADAM datasets
        
    Returns
    -------
    dict
        Dictionary of dataset name -> DataFrame
    """
    from pathlib import Path
    
    if datasets is None:
        datasets = ['adsl', 'adae', 'adlb', 'adcm', 'adex', 'advs']
    
    data_path = Path(data_dir)
    loaded_data = {}
    
    for dataset in datasets:
        # Try different file extensions
        for ext in ['.sas7bdat', '.xpt', '.csv']:
            file_path = data_path / f"{dataset}{ext}"
            if file_path.exists():
                try:
                    if ext == '.sas7bdat':
                        df = read_sas(str(file_path))
                    elif ext == '.xpt':
                        df = read_xpt(str(file_path))
                    elif ext == '.csv':
                        df = pd.read_csv(str(file_path))
                    
                    if not df.empty:
                        loaded_data[dataset.upper()] = df
                        print(f"Loaded {dataset.upper()}: {len(df)} records")
                        break
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
                    continue
    
    return loaded_data 