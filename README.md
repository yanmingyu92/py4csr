# py4csr: Python for Clinical Study Reporting

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Documentation Status](https://img.shields.io/badge/docs-latest-brightgreen.svg)](docs/)

**py4csr** is a comprehensive Python package for clinical study reporting that provides a functional programming approach to clinical trial data analysis and reporting, designed specifically for pharmaceutical and biotech companies conducting clinical research.

## 🚀 Key Features

### 📊 **Functional Reporting System**
- **Intuitive workflow**: Clean, pythonic patterns for clinical reporting
- **Method chaining**: Fluent API for building complex reports step-by-step
- **Configuration-driven**: Flexible templates and statistical definitions
- **CDISC compliance**: Built-in support for ADaM datasets and CDISC standards

### 📈 **Advanced Analytics**
- **Statistical templates**: Pre-built calculations for clinical endpoints
- **Multiple output formats**: RTF, PDF, HTML, Excel generation
- **Clinical plotting**: Specialized plots (Kaplan-Meier, Forest, Waterfall, etc.)
- **Real data validation**: Tested with actual clinical trial datasets

### 🔧 **Production Ready**
- **Regulatory compliance**: ICH E3 and CTD-ready outputs
- **Data quality checks**: Built-in validation and quality assessment
- **Performance optimized**: Handles large clinical datasets efficiently
- **Extensible architecture**: Easy to customize and extend

## 📦 Installation

### From PyPI (Recommended)
```bash
pip install py4csr
```

### From Source
```bash
git clone https://github.com/your-org/py4csr.git
cd py4csr
pip install -e .
```

### Dependencies
```bash
# Core dependencies
pip install pandas numpy scipy matplotlib seaborn
pip install reportlab jinja2 openpyxl

# For SAS data reading
pip install pyreadstat  # or sas7bdat
```

## 🏃‍♂️ Quick Start

### Basic Usage
```python
from py4csr.functional import ReportSession

# Initialize a clinical study report session
session = (ReportSession()
    .init_study(
        uri="STUDY001", 
        title="Phase III Efficacy and Safety Study",
        protocol="ABC-123-2024"
    )
    .load_datasets(data_path="data/")
    .define_populations(
        safety="SAFFL=='Y'", 
        efficacy="EFFFL=='Y'"
    )
    .define_treatments(var="TRT01P")
)

# Generate standard clinical tables
session = (session
    .add_demographics_table()
    .add_disposition_table()
    .add_ae_summary()
    .add_efficacy_analysis()
)

# Generate all outputs
result = session.generate_all().finalize()
print(f"Generated {len(result.generated_files)} report files")
```

### Working with Real Clinical Data
```python
# Load CDISC ADaM datasets
datasets = {
    'ADSL': 'data/adsl.sas7bdat',
    'ADAE': 'data/adae.sas7bdat',
    'ADLB': 'data/adlb.sas7bdat'
}

session = (ReportSession()
    .init_study(uri="REAL-STUDY", title="Real Clinical Data Analysis")
    .load_datasets(datasets=datasets)
    .define_populations(safety="SAFFL=='Y'")
    .define_treatments(var="TRT01P")
    .add_demographics_table()
    .add_ae_summary()
    .generate_all(output_dir="clinical_reports")
    .finalize()
)
```

### Advanced Features
```python
from py4csr.functional import ReportSession, FunctionalConfig

# Custom configuration
config = FunctionalConfig.clinical_standard()
config.add_statistic("geometric_mean", "Geometric Mean")
config.set_format("p_value", "{:.4f}")

# Advanced session with custom features
session = (ReportSession(config)
    .init_study(uri="ADVANCED-001", title="Advanced Analysis")
    .load_datasets(data_path="data/")
    .define_populations(safety="SAFFL=='Y'", efficacy="EFFFL=='Y'")
    .define_treatments(var="TRT01P")
    
    # Add custom grouping and formatting
    .add_grouping("age_group", "AGEGR1", {"<65": "Young", ">=65": "Elderly"})
    .add_conditional_formatting("p_value", lambda x: x < 0.05, "highlight")
    
    # Generate tables with advanced features
    .add_demographics_table(by_group="age_group")
    .add_ae_summary(include_severity=True)
    .add_efficacy_analysis(endpoints=["AVAL", "CHG"])
    
    # Generate plots
    .create_kaplan_meier_plot(time_var="AVAL", event_var="CNSR")
    .create_forest_plot(endpoint="CHG", subgroups=["SEX", "AGEGR1"])
    
    .generate_all()
    .finalize()
)
```

## 📚 Documentation

### Core Modules

| Module | Description |
|--------|-------------|
| `py4csr.functional` | Main functional reporting interface |
| `py4csr.clinical` | Direct clinical reporting system |
| `py4csr.data` | Data loading and manipulation utilities |
| `py4csr.analysis` | Statistical analysis functions |
| `py4csr.plotting` | Clinical plotting capabilities |
| `py4csr.reporting` | Report generation and formatting |
| `py4csr.validation` | Data quality and compliance checking |

### Key Classes

- **`ReportSession`**: Main orchestrator for functional reporting
- **`ClinicalSession`**: Direct clinical reporting interface
- **`FunctionalConfig`**: Configuration management for reports
- **`TableBuilder`**: Functional table construction
- **`StatisticalTemplates`**: Reusable statistical calculations
- **`PlottingEngine`**: Clinical plot generation

## 🧪 Testing with Real Data

py4csr has been tested with real clinical trial data including:

- **CDISC Pilot Study**: 254 subjects, 10 ADaM datasets (~92MB)
- **Multiple domains**: Demographics, AE, Laboratory, Vital Signs, Questionnaires
- **Complex scenarios**: Multiple visits, missing data, regulatory requirements

```python
# Example with real CDISC data
from py4csr.examples import load_cdisc_pilot_data

datasets = load_cdisc_pilot_data()
print(f"Loaded {len(datasets)} datasets:")
for name, df in datasets.items():
    print(f"  {name}: {len(df)} records")

# Generate standard regulatory tables
session = create_regulatory_report_session(datasets)
result = session.generate_all().finalize()
```

## 🏗️ Architecture

py4csr follows a modular, functional architecture:

```
py4csr/
├── functional/          # Functional programming interface
│   ├── session.py      # ReportSession class
│   ├── config.py       # Configuration management
│   └── templates.py    # Statistical templates
├── clinical/           # Direct clinical interface
│   ├── session.py      # ClinicalSession class
│   ├── statistical_engine.py  # Statistics calculations
│   └── enhanced_rtf_formatter.py  # Professional RTF output
├── data/               # Data I/O and manipulation
├── analysis/           # Statistical analysis
├── plotting/           # Clinical plotting
├── reporting/          # Output generation
├── validation/         # Quality checks
└── examples/           # Example scripts and data
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Documentation**: [docs/](docs/)
- **Examples**: [examples/](examples/)
- **Issues**: [GitHub Issues](https://github.com/your-org/py4csr/issues)
- **PyPI**: [https://pypi.org/project/py4csr/](https://pypi.org/project/py4csr/)

## 🙏 Acknowledgments

- Inspired by the clinical reporting needs of the pharmaceutical industry
- Built for regulatory compliance and professional clinical research
- Designed with input from biostatisticians and clinical data managers

## 📞 Support

- **Documentation**: [https://py4csr.readthedocs.io](https://py4csr.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/your-org/py4csr/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/py4csr/discussions)
- **Email**: support@py4csr.org

## 🗺️ Roadmap

### Version 1.1 (Next Release)
- [ ] Enhanced CDISC metadata integration
- [ ] Additional statistical tests
- [ ] Interactive dashboard generation
- [ ] Cloud deployment templates

### Version 1.2 (Future)
- [ ] Real-time data monitoring
- [ ] Advanced machine learning integration
- [ ] Multi-language support
- [ ] Enterprise features

---

**py4csr** - Bringing the power of clinical reporting to Python 🐍📊 