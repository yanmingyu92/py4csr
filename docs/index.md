# py4csr Documentation

Welcome to the **py4csr** documentation! py4csr is a comprehensive Python package for clinical study reporting that brings the power and flexibility of SAS RRG (Rapid Report Generator) to the Python ecosystem.

## 🚀 Quick Navigation

### Getting Started
- [Installation Guide](installation.md) - How to install py4csr
- [Quick Start Tutorial](quickstart.md) - Your first clinical report in 5 minutes
- [Basic Concepts](concepts.md) - Understanding the py4csr workflow

### User Guide
- [Functional Reporting System](user-guide/functional-system.md) - Core reporting functionality
- [Working with Clinical Data](user-guide/clinical-data.md) - Loading and processing CDISC datasets
- [Statistical Analysis](user-guide/statistical-analysis.md) - Built-in statistical templates
- [Output Generation](user-guide/output-generation.md) - Creating reports in multiple formats
- [Configuration](user-guide/configuration.md) - Customizing py4csr behavior

### Advanced Topics
- [Custom Statistical Functions](advanced/custom-statistics.md) - Extending statistical capabilities
- [Clinical Plotting](advanced/plotting.md) - Specialized clinical visualizations
- [Regulatory Compliance](advanced/regulatory.md) - ICH E3 and CTD compliance
- [Performance Optimization](advanced/performance.md) - Handling large datasets

### API Reference
- [Core Classes](api/core.md) - ReportSession, FunctionalConfig
- [Data Module](api/data.md) - Data loading and manipulation
- [Analysis Module](api/analysis.md) - Statistical analysis functions
- [Plotting Module](api/plotting.md) - Clinical plotting capabilities
- [Reporting Module](api/reporting.md) - Output generation

### Examples
- [Basic Demographics Table](examples/demographics.md) - Standard demographics analysis
- [Adverse Events Analysis](examples/adverse-events.md) - Safety reporting
- [Efficacy Analysis](examples/efficacy.md) - Primary and secondary endpoints
- [Real Data Examples](examples/real-data.md) - Working with actual clinical trial data

### Development
- [Contributing Guide](development/contributing.md) - How to contribute to py4csr
- [Development Setup](development/setup.md) - Setting up development environment
- [Testing](development/testing.md) - Running and writing tests
- [Release Process](development/releases.md) - How releases are made

## 🎯 What is py4csr?

py4csr is designed to bridge the gap between SAS-based clinical reporting and modern Python data science workflows. It provides:

### 📊 **SAS RRG Equivalent Functionality**
- **Functional programming approach** similar to SAS RRG macros
- **Method chaining** for building complex reports step-by-step
- **Statistical templates** for common clinical calculations
- **Multiple output formats** (RTF, PDF, HTML, Excel)

### 🏥 **Clinical Trial Focus**
- **CDISC compliance** with built-in ADaM dataset support
- **Regulatory standards** following ICH E3 and CTD guidelines
- **Real data validation** tested with actual pharmaceutical datasets
- **Industry best practices** for clinical reporting

### 🔧 **Production Ready**
- **Comprehensive testing** including real clinical trial data
- **Performance optimized** for large datasets
- **Extensible architecture** for custom requirements
- **Professional documentation** and examples

## 🏃‍♂️ Quick Example

```python
from py4csr.functional import ReportSession

# Create a complete clinical study report
result = (ReportSession()
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
    .add_demographics_table()
    .add_ae_summary()
    .add_efficacy_analysis()
    .generate_all(output_dir="clinical_reports")
    .finalize()
)

print(f"Generated {len(result.generated_files)} report files")
```

## 🧪 Tested with Real Data

py4csr has been extensively tested with real clinical trial data:

- **CDISC Pilot Study**: 254 subjects, 10 ADaM datasets (~92MB)
- **Multiple domains**: Demographics, AE, Laboratory, Vital Signs, Questionnaires
- **Complex scenarios**: Multiple visits, missing data, regulatory requirements
- **Production quality**: Ready for pharmaceutical industry use

## 🤝 Community and Support

- **GitHub Repository**: [https://github.com/your-org/py4csr](https://github.com/your-org/py4csr)
- **Issue Tracker**: [Report bugs and request features](https://github.com/your-org/py4csr/issues)
- **Discussions**: [Community discussions](https://github.com/your-org/py4csr/discussions)
- **Email Support**: support@py4csr.org

## 📄 License

py4csr is released under the MIT License. See the [LICENSE](https://github.com/your-org/py4csr/blob/main/LICENSE) file for details.

---

Ready to get started? Check out our [Installation Guide](installation.md) and [Quick Start Tutorial](quickstart.md)! 