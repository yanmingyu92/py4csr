# py4csr Clinical Trial Plotting Engine v2.0

## Overview

A robust, modular Python plotting engine specifically designed for clinical trials, based on comprehensive analysis of SAS GPROC macros. Built with functional programming principles and optimized for LLM agent integration.

## Key Features

### 🎯 **Clinical Trial Focused**
- **15+ plot types** with full SAS feature parity
- **Regulatory-quality outputs** (PNG, RTF, HTML)
- **Professional styling** for clinical reports
- **Statistical computations** built-in

### 🔧 **LLM-Optimized Architecture**
- **Clear function signatures** for easy agent integration
- **Modular design** for extensibility
- **Comprehensive validation** and error handling
- **Functional programming** principles

### 📊 **SAS Macro Compatibility**
Based on comprehensive analysis of SAS GPROC macros:
- **GBOX1/2**: Box plots with quartiles, outliers, means
- **GLINE1/2**: Line plots with trajectories and statistics
- **GKM1/2**: Kaplan-Meier survival curves
- **GFOREST1**: Forest plots for subgroup analysis
- **GBAR1/GVBAR2/GHBAR2**: Bar charts with error bars
- **GWATERFALL1/2**: Waterfall plots for response analysis
- **GDENSITY1/2**: Density plots with overlays
- **GSCATTER1/2**: Scatter plots with regression
- **GBUBBLE2**: Bubble plots for multi-dimensional data
- **GBAND2**: Band plots with confidence intervals
- **GCDF2**: Cumulative distribution functions
- **GSPAGHETTI2**: Individual subject trajectories

## Quick Start for LLM Agents

### Simple Line Plot
```python
from py4csr.plotting import quick_lineplot
import pandas as pd

# Create a line plot with individual subject trajectories
fig, ax = quick_lineplot(
    data=clinical_data,
    x_col='visit_day',
    y_col='lab_value', 
    subject_col='subject_id',
    title1='Individual Subject Trajectories',
    save_path='output.png'
)
```

### Box Plot with Groups
```python
from py4csr.plotting import quick_boxplot

fig, ax = quick_boxplot(
    data=clinical_data,
    x_col='treatment_group',
    y_col='change_from_baseline',
    group_col='visit',
    title1='Change from Baseline by Treatment Group',
    show_stats=True,
    save_path='boxplot.png'
)
```

### Kaplan-Meier Survival Plot
```python
from py4csr.plotting import quick_km_plot

fig, ax = quick_km_plot(
    data=survival_data,
    time_col='time_to_event',
    event_col='event_occurred',
    group_col='treatment_arm',
    title1='Overall Survival by Treatment',
    show_ci=True,
    save_path='km_plot.png'
)
```

### Forest Plot
```python
from py4csr.plotting import quick_forest_plot

fig, ax = quick_forest_plot(
    data=subgroup_data,
    estimate_col='hazard_ratio',
    lower_col='ci_lower',
    upper_col='ci_upper', 
    label_col='subgroup_name',
    title1='Subgroup Analysis - Hazard Ratios',
    save_path='forest_plot.png'
)
```

## Advanced Configuration

### Using PlotConfig for Full Control
```python
from py4csr.plotting import create_clinical_plot, PlotConfig, PlotType

config = PlotConfig(
    data=clinical_data,
    plot_type=PlotType.LINE,
    x_col='visit_day',
    y_col='lab_value',
    subject_col='subject_id',
    
    # Visual parameters
    width=12.0,
    height=8.0,
    dpi=300,
    
    # Statistical parameters
    show_ci=True,
    ci_level=0.95,
    
    # Output parameters
    save_path='advanced_plot.png',
    rtf_path='advanced_plot.rtf',
    html_path='advanced_plot.html',
    
    # Titles and labels
    title1='Advanced Clinical Line Plot',
    title2='Laboratory Values Over Time',
    title3='Study ABC-123 - Safety Analysis',
    x_label='Study Day',
    y_label='Lab Value (Units)',
    
    # Footnotes
    footnote1='Note: Individual subject trajectories shown',
    footnote2='Source: ADLB dataset',
    footnote3='Generated with py4csr v2.0',
    
    # Study information
    protocol='ABC-123',
    study_id='Phase III Study'
)

fig, ax = create_clinical_plot(config)
```

## Architecture Overview

### Core Components

1. **PlotConfig**: Configuration dataclass for all plot parameters
2. **PlotType**: Enum defining supported clinical plot types
3. **Validation**: Comprehensive data and parameter validation
4. **Statistics**: Built-in statistical computations
5. **Styling**: Professional clinical trial styling
6. **Output**: Multi-format output generation (PNG, RTF, HTML)

### Functional Design

```python
# Core plotting pipeline
data → validation → statistics → visualization → styling → output
```

### Plot Type Routing
```python
plot_functions = {
    PlotType.BOX: clinical_boxplot,
    PlotType.LINE: clinical_lineplot, 
    PlotType.KM: clinical_km_plot,
    PlotType.FOREST: clinical_forest_plot,
    # ... additional plot types
}
```

## SAS Macro Feature Analysis

### GBOX1/GBOX2 Features
- ✅ Quartiles, medians, means
- ✅ Outlier detection and display
- ✅ Group comparisons
- ✅ Statistical annotations
- ✅ Professional styling
- ✅ Panel layouts

### GLINE1/GLINE2 Features
- ✅ Individual subject trajectories (GLINE1)
- ✅ Group means with statistics (GLINE2)
- ✅ Confidence intervals
- ✅ Error bars
- ✅ Symbol and line customization
- ✅ Legend positioning

### GKM1/GKM2 Features
- ✅ Survival curves
- ✅ Confidence intervals
- ✅ Censoring marks
- ✅ Risk tables
- ✅ Log-rank test p-values
- ✅ Group comparisons

### GFOREST1 Features
- ✅ Effect sizes with confidence intervals
- ✅ Subgroup analysis
- ✅ Reference lines
- ✅ Statistical annotations
- ✅ Professional formatting

## Data Requirements

### Standard Clinical Data Format
```python
# Example data structure
clinical_data = pd.DataFrame({
    'subject_id': ['001', '002', '003', ...],
    'treatment_group': ['Active', 'Placebo', 'Active', ...],
    'visit_day': [0, 7, 14, 28, ...],
    'lab_value': [12.5, 11.8, 13.2, ...],
    'change_from_baseline': [0, -0.7, 0.7, ...]
})
```

### Survival Data Format
```python
survival_data = pd.DataFrame({
    'subject_id': ['001', '002', '003', ...],
    'treatment_arm': ['Arm A', 'Arm B', 'Arm A', ...],
    'time_to_event': [365, 180, 450, ...],
    'event_occurred': [1, 1, 0, ...]  # 1=event, 0=censored
})
```

### Forest Plot Data Format
```python
subgroup_data = pd.DataFrame({
    'subgroup_name': ['Overall', 'Age <65', 'Age >=65', ...],
    'hazard_ratio': [0.75, 0.68, 0.82, ...],
    'ci_lower': [0.60, 0.45, 0.65, ...],
    'ci_upper': [0.94, 0.91, 1.03, ...]
})
```

## Output Formats

### PNG Output
- **High resolution** (300 DPI default)
- **Professional styling** with clinical fonts
- **Optimized for** regulatory submissions

### RTF Output
- **Regulatory-compliant** formatting
- **Embedded images** with proper scaling
- **Professional headers** and footers
- **Study metadata** integration

### HTML Output
- **Interactive plots** using Plotly
- **Responsive design** for web viewing
- **Export capabilities** built-in

## Error Handling

### Data Validation
```python
# Automatic validation of required columns
validate_data(data, required_cols=['x_col', 'y_col'])

# Missing data handling
if data[y_col].isna().any():
    warnings.warn("Missing values detected in y_col")
```

### Parameter Validation
```python
# Enum validation for plot types
if plot_type not in PlotType:
    raise ValueError(f"Invalid plot type: {plot_type}")

# Range validation for statistical parameters
if ci_level <= 0 or ci_level >= 1:
    raise ValueError("ci_level must be between 0 and 1")
```

## Extension Guide

### Adding New Plot Types

1. **Define the plot type**:
```python
class PlotType(Enum):
    NEW_PLOT = "new_plot"
```

2. **Create the plot function**:
```python
def clinical_new_plot(config: PlotConfig) -> Tuple[plt.Figure, plt.Axes]:
    validate_data(config.data, [config.x_col, config.y_col])
    apply_clinical_style()
    
    fig, ax = plt.subplots(figsize=(config.width, config.height))
    # ... plot implementation
    return fig, ax
```

3. **Add to routing**:
```python
plot_functions = {
    PlotType.NEW_PLOT: clinical_new_plot,
    # ... existing plot types
}
```

4. **Create convenience function**:
```python
def quick_new_plot(data, x_col, y_col, **kwargs):
    config = PlotConfig(
        data=data,
        plot_type=PlotType.NEW_PLOT,
        x_col=x_col,
        y_col=y_col,
        **kwargs
    )
    return create_clinical_plot(config)
```

## Performance Considerations

### Memory Optimization
- **Lazy loading** of large datasets
- **Efficient data structures** for statistical computations
- **Memory cleanup** after plot generation

### Parallel Processing
- **Batch plot generation** for multiple outputs
- **Concurrent file writing** for different formats
- **Optimized statistical** computations

## Integration with LLM Agents

### Clear Function Signatures
```python
def quick_lineplot(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    group_col: Optional[str] = None,
    subject_col: Optional[str] = None,
    **kwargs
) -> Tuple[plt.Figure, plt.Axes]:
```

### Comprehensive Documentation
- **Type hints** for all parameters
- **Clear descriptions** of functionality
- **Example usage** for each plot type
- **Error messages** with actionable guidance

### Validation and Feedback
- **Immediate validation** of inputs
- **Helpful error messages** for debugging
- **Warnings** for potential issues
- **Success confirmations** with file paths

## Migration from v1.0

### Legacy Compatibility
The engine maintains backward compatibility with existing code:

```python
# Old v1.0 syntax still works
_create_clinical_lineplot(
    data=data,
    x_col='visit',
    y_col='value',
    save_path='output.png'
)

# New v2.0 syntax (recommended)
quick_lineplot(
    data=data,
    x_col='visit', 
    y_col='value',
    save_path='output.png'
)
```

### Parameter Mapping
Old parameters are automatically mapped to new structure:
- `plot_type='gline1'` → handled internally
- `show_trajectories=True` → `subject_col` detection
- `legend_x/y` → internal legend positioning
- `x_format` → internal formatting

## Best Practices

### For LLM Agents
1. **Use quick_* functions** for simple plots
2. **Use PlotConfig** for complex requirements
3. **Always specify output paths** for file generation
4. **Include titles and footnotes** for professional output
5. **Validate data** before plotting

### For Clinical Reports
1. **Use high DPI** (300+) for print quality
2. **Include protocol information** in metadata
3. **Add appropriate footnotes** for data sources
4. **Use consistent styling** across all plots
5. **Generate multiple formats** (PNG + RTF) for flexibility

### For Regulatory Submissions
1. **Follow ICH guidelines** for statistical presentations
2. **Include comprehensive metadata** in RTF outputs
3. **Use professional color palettes** only
4. **Validate all statistical computations** independently
5. **Document all plot specifications** thoroughly

## Support and Development

### Version Information
```python
from py4csr.plotting import __version__, print_system_status

print(f"py4csr version: {__version__}")
print_system_status()
```

### Feature Requests
The modular architecture makes it easy to add new features:
- New plot types based on additional SAS macros
- Enhanced statistical computations
- Additional output formats
- Custom styling themes
- Integration with other clinical data standards

### Contributing
1. Follow functional programming principles
2. Maintain comprehensive type hints
3. Include thorough documentation
4. Add appropriate validation
5. Ensure backward compatibility 