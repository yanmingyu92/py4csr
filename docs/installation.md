# Installation Guide

This guide will help you install py4csr and its dependencies for clinical study reporting.

## 📋 Requirements

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: 4GB RAM minimum (8GB+ recommended for large datasets)
- **Storage**: 1GB free space for installation and temporary files

### Python Dependencies
py4csr requires several Python packages that will be automatically installed:

**Core Dependencies:**
- `pandas>=1.3.0` - Data manipulation and analysis
- `numpy>=1.20.0` - Numerical computing
- `scipy>=1.7.0` - Scientific computing
- `matplotlib>=3.4.0` - Basic plotting
- `jinja2>=3.0.0` - Template engine for reports
- `pyyaml>=5.4.0` - YAML configuration files
- `openpyxl>=3.0.0` - Excel file support
- `reportlab>=3.6.0` - PDF generation
- `python-docx>=0.8.11` - Word document generation

## 🚀 Installation Methods

### Method 1: Install from PyPI (Recommended)

The easiest way to install py4csr is using pip:

```bash
pip install py4csr
```

### Method 2: Install with Optional Dependencies

For enhanced functionality, install with optional dependencies:

```bash
# Install with SAS file reading support
pip install py4csr[sas]

# Install with advanced plotting capabilities
pip install py4csr[plotting]

# Install with additional statistical functions
pip install py4csr[stats]

# Install everything
pip install py4csr[all]
```

### Method 3: Install from Source

For development or the latest features:

```bash
git clone https://github.com/your-org/py4csr.git
cd py4csr
pip install -e .
```

### Method 4: Development Installation

For contributors and developers:

```bash
git clone https://github.com/your-org/py4csr.git
cd py4csr
pip install -e ".[dev]"
```

## 🔧 Optional Dependencies

### SAS File Support
To read SAS datasets (.sas7bdat files):

```bash
pip install pyreadstat
# or alternatively
pip install sas7bdat
```

### Advanced Plotting
For enhanced clinical visualizations:

```bash
pip install plotly seaborn bokeh plotnine
```

### Statistical Analysis
For advanced statistical functions:

```bash
pip install statsmodels scikit-learn lifelines
```

## ✅ Verify Installation

Test your installation:

```python
import py4csr
print(f"py4csr version: {py4csr.__version__}")

# Test basic functionality
from py4csr.functional import ReportSession
session = ReportSession()
print("✓ py4csr installed successfully!")
```

## 🐍 Virtual Environment Setup

We recommend using a virtual environment:

### Using venv (Python 3.8+)
```bash
python -m venv py4csr-env
source py4csr-env/bin/activate  # On Windows: py4csr-env\Scripts\activate
pip install py4csr[all]
```

### Using conda
```bash
conda create -n py4csr python=3.9
conda activate py4csr
pip install py4csr[all]
```

## 🏥 Clinical Environment Setup

For pharmaceutical/clinical research environments:

### 1. Create Project Structure
```bash
mkdir my-clinical-study
cd my-clinical-study
mkdir data outputs scripts config
```

### 2. Install py4csr
```bash
pip install py4csr[all]
```

### 3. Create Configuration
```python
# config/study_config.yaml
study:
  name: "My Clinical Study"
  protocol: "PROTO-001"
  phase: "III"

populations:
  safety: "SAFFL=='Y'"
  efficacy: "EFFFL=='Y'"
  itt: "ITTFL=='Y'"

treatments:
  variable: "TRT01P"
  decode: "TRT01A"
```

### 4. Test with Sample Data
```python
# scripts/test_installation.py
from py4csr.functional import ReportSession

session = (ReportSession()
    .init_study(uri="TEST", title="Installation Test")
    .load_datasets(data_path="../data/")
)

print("✓ Clinical environment setup complete!")
```

## 🔍 Troubleshooting

### Common Issues

#### ImportError: No module named 'py4csr'
**Solution**: Ensure py4csr is installed in the correct environment
```bash
pip list | grep py4csr
```

#### SAS File Reading Issues
**Solution**: Install SAS reading dependencies
```bash
pip install pyreadstat
```

#### Memory Issues with Large Datasets
**Solution**: Increase available memory or use chunking
```python
# Use chunking for large datasets
session.load_datasets(data_path="data/", chunk_size=10000)
```

#### Permission Errors on Windows
**Solution**: Run as administrator or use user installation
```bash
pip install --user py4csr
```

### Platform-Specific Notes

#### Windows
- Use PowerShell or Command Prompt
- May need Visual C++ Build Tools for some dependencies
- Consider using Anaconda for easier dependency management

#### macOS
- May need Xcode Command Line Tools: `xcode-select --install`
- Use Homebrew for system dependencies if needed

#### Linux
- Install system dependencies: `sudo apt-get install python3-dev`
- For CentOS/RHEL: `sudo yum install python3-devel`

## 🚀 Next Steps

After successful installation:

1. **Quick Start**: Follow the [Quick Start Tutorial](quickstart.md)
2. **Load Sample Data**: Try the [Real Data Examples](examples/real-data.md)
3. **Configure Your Environment**: Read the [Configuration Guide](user-guide/configuration.md)
4. **Join the Community**: Visit our [GitHub Discussions](https://github.com/your-org/py4csr/discussions)

## 📞 Getting Help

If you encounter issues:

1. **Check the FAQ**: [Frequently Asked Questions](faq.md)
2. **Search Issues**: [GitHub Issues](https://github.com/your-org/py4csr/issues)
3. **Ask for Help**: [GitHub Discussions](https://github.com/your-org/py4csr/discussions)
4. **Email Support**: support@py4csr.org

---

**Ready to start?** Continue to the [Quick Start Tutorial](quickstart.md) to create your first clinical report! 