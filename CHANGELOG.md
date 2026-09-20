# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **Default p-value tests now match gtsummary's `add_p()` defaults.** Continuous
  variables use Wilcoxon rank-sum (2 groups, scipy `mannwhitneyu` two-sided) or
  Kruskal-Wallis (>2 groups) instead of ANOVA; categorical variables use Pearson
  chi-square without continuity correction, switching to Fisher's exact test when
  any expected cell count < 5. The old behavior remains available via explicit
  `test="anova"` / `test="ttest"` / `test="chisq"` options on `add_var()` /
  `add_catvar()`. The test actually used per variable is recorded in
  `ClinicalSession.p_value_tests` and reflected in the output methodology footnote.
- Unknown keywords in `stats=` strings now raise a clear `ValueError` listing the
  valid statistics (previously silently produced "N/A" cells).
- Missing (NaN) values in the treatment variable now raise a clear, actionable
  `ValueError` instead of crashing or silently contaminating group/Total columns.
- Empty analysis frames (e.g. a `where` clause that removes all rows) now raise a
  clear `ValueError` instead of returning empty results.

### Added
- `ClinicalStatisticalEngine.perform_wilcoxon`, `perform_kruskal`, `perform_ttest`,
  and `perform_continuous_test` / `perform_categorical_test` dispatchers with
  explicit, documented test selection (`test="auto"` follows gtsummary behavior).
- Fisher's exact test supports RxC tables via a fixed-seed Monte Carlo
  (deterministic), in addition to analytic 2x2.
- `py4csr.tbl_summary(data, by=..., include=..., statistic=..., label=...,
  where=..., total=..., type=..., test=...)` convenience API (ARCHITECTURE.md §6
  sketch), returning a `TblSummaryResult` with `.ard` (long-format results),
  `.to_table()`, `.preview()`, `.p_values` and `.p_value_tests`.

### Fixed
- pandas 3.0 compatibility: `fillna(method="ffill")` replaced with `.ffill()` in
  `data/preprocessing.py`; `apply_cdisc_formats` keeps USUBJID as object-dtype
  strings (`astype(str)` yields StringDtype in pandas >= 3); `read_sas`/`read_xpt`
  now raise `FileNotFoundError` for missing files before checking the optional
  `pyreadstat` dependency.
- N statistic for empty/all-missing groups now reports 0 instead of a blank cell.
- Performance: `generate()` on a 100k-row × 10-variable ADSL is ~40% faster
  (1.5s → 0.9s) after vectorizing categorical counting (single groupby pass
  instead of per-cell boolean scans), grouping continuous stats once per variable,
  and removing per-variable full-frame copies in p-value collection.

### Validation
- Cross-validation harness (`validation/compare_gtsummary.py` in the development
  workspace) against gtsummary's `trial` dataset: **99/99 compared cells match
  the independent reference (100%), including Wilcoxon/chi-square p-values**, and
  40/40 published gtsummary vignette values are reproduced.

### In Progress
- JSS manuscript preparation
- Additional example notebooks

---

## [0.1.1] - 2025-10-29

### Fixed
- Made `pyreadstat` import optional to fix import errors when SAS support is not installed
- Added proper error messages directing users to install `py4csr[sas]` for SAS file support
- Fixed `read_sas()` and `read_xpt()` functions to check for pyreadstat availability

### Changed
- `pyreadstat` is now truly optional - only required when reading SAS files
- Improved error messages for missing optional dependencies

---

## [0.1.0] - 2025-10-29

### Added

#### Core Functionality
- **Clinical Session Interface**: Workflow-based clinical reporting system
  - `ClinicalSession` class for creating clinical tables
  - Support for demographics, adverse events, efficacy, and laboratory tables
  - Multiple output formats: RTF, PDF, HTML, CSV
- **Functional Interface**: Composable functional programming interface
  - `FunctionalConfig` for configuration management
  - `StatisticalTemplates` for statistical calculations
  - `ReportBuilder` for method chaining report construction
  - `TableBuilder` for flexible table creation
- **Statistical Engine**: Comprehensive statistical analysis
  - Continuous statistics (n, mean, SD, median, min, max, Q1, Q3)
  - Categorical statistics (n, percentage)
  - Statistical tests (ANOVA, chi-square, Fisher's exact)
  - Custom statistic support
- **Data Processing**: CDISC ADaM dataset handling
  - Data validation for required variables
  - Support for ADSL, ADAE, ADLB, ADVS, ADEFF datasets
  - Data preprocessing and transformation utilities
  - Multiple input formats: CSV, SAS, Excel

#### Output Formats
- **RTF Output**: Professional RTF table generation
  - SAS-compatible RTF formatting
  - Customizable fonts, borders, alignment
  - Page orientation and margins control
- **PDF Output**: High-quality PDF reports
  - ReportLab-based PDF generation
  - Professional formatting and layout
- **HTML Output**: Interactive HTML tables
  - Responsive design
  - Sortable and filterable tables
- **CSV Output**: Data export for further analysis

#### Plotting & Visualization
- **Clinical Plots**: Comprehensive clinical visualizations
  - Kaplan-Meier survival plots
  - Forest plots for subgroup analysis
  - Box plots for distribution analysis
  - Interactive HTML plots with Plotly
- **Plot Results**: Unified plot result interface
  - Multiple format export (PNG, PDF, HTML)
  - Customizable styling and themes

#### Quality & Testing
- **Test Suite**: 710 comprehensive tests
  - 697 unit tests
  - 10 integration tests
  - 3 package tests
  - 46% code coverage
- **Code Quality Tools**:
  - Black for code formatting
  - isort for import sorting
  - flake8 for linting
  - mypy for type checking
  - pre-commit hooks configured
- **Custom Exceptions**: Comprehensive error handling
  - `Py4csrError` base exception
  - `DataValidationError` for data issues
  - `ConfigurationError` for config problems
  - `OutputFormatError` for output issues
  - `StatisticalError` for statistical problems
  - `MetadataError` for metadata issues
  - `SessionError` for session problems

#### Documentation
- **Sphinx Documentation**: Professional documentation system
  - 20 documentation files
  - 8 API reference pages
  - 5 user guide tutorials
  - 3 example files
  - 4 advanced topic guides
  - 3 development documentation files
- **User Guides**:
  - Functional system tutorial
  - Clinical data handling guide
  - Statistical analysis guide
  - Output generation guide
  - Configuration and customization guide
- **Examples**:
  - Demographics table examples
  - Adverse events analysis examples
  - Efficacy analysis examples
- **Advanced Topics**:
  - Custom statistics creation
  - Clinical plotting guide
  - Regulatory compliance (ICH E3, CDISC)
  - Performance optimization
- **Development Guides**:
  - Contributing guide
  - Testing guide
  - Release process guide

### Dependencies

#### Core Dependencies
- pandas >= 1.3.0
- numpy >= 1.20.0
- scipy >= 1.7.0
- matplotlib >= 3.4.0
- jinja2 >= 3.0.0
- pyyaml >= 5.4.0
- openpyxl >= 3.0.0
- python-docx >= 0.8.11
- xlsxwriter >= 3.0.0
- tabulate >= 0.8.9
- click >= 8.0.0
- tqdm >= 4.60.0

#### Optional Dependencies
- **PDF Support**: reportlab >= 3.6.0
- **SAS Files**: pyreadstat >= 1.1.0, sas7bdat >= 2.2.0
- **Advanced Plotting**: plotly >= 5.0, bokeh >= 2.0, seaborn >= 0.11, plotnine >= 0.8
- **Advanced Statistics**: statsmodels >= 0.12.0, scikit-learn >= 1.0.0, lifelines >= 0.26.0
- **Development**: pytest, black, flake8, mypy, sphinx, and more

### Changed
- Updated Python version requirement to >= 3.8
- Improved error messages with custom exceptions
- Enhanced type hints throughout codebase
- Optimized statistical calculations for performance

### Fixed
- Data validation edge cases
- RTF formatting issues
- Unicode handling in outputs
- Memory efficiency improvements

### Infrastructure
- **CI/CD**: GitHub Actions workflows (planned)
- **Pre-commit Hooks**: Automated code quality checks
- **Package Structure**: Clean, modular architecture
- **Type Hints**: Comprehensive type annotations
- **License**: MIT License

### Compliance
- **CDISC Standards**: ADaM dataset support
- **ICH E3 Guidelines**: Clinical study report standards
- **FDA Submission**: RTF format compatibility
- **Regulatory Ready**: Professional output quality

### Performance
- Efficient pandas-based data processing
- Optimized statistical calculations
- Memory-efficient large dataset handling
- Batch processing support

### Documentation Links
- Homepage: https://github.com/yanmingyu92/py4csr
- Documentation: https://py4csr.readthedocs.io
- Bug Tracker: https://github.com/yanmingyu92/py4csr/issues
- Discussions: https://github.com/yanmingyu92/py4csr/discussions

---

## Release Notes

### Version 0.1.0 Highlights

This is the initial release of py4csr, a professional Python package for clinical study reporting. The package provides:

1. **Two Interfaces**: Choose between workflow-based `ClinicalSession` or functional `ReportBuilder`
2. **Comprehensive Statistics**: All standard clinical trial statistics with extensibility
3. **Multiple Outputs**: RTF, PDF, HTML, and CSV formats
4. **CDISC Compliance**: Full support for ADaM datasets
5. **Production Ready**: 710 tests, 46% coverage, comprehensive documentation
6. **Regulatory Focus**: ICH E3 and FDA submission compatible

### Getting Started

```python
# Install
pip install py4csr

# Quick example
from py4csr.clinical import ClinicalSession
import pandas as pd

# Load data
adsl = pd.read_csv("adsl.csv")

# Create demographics table
session = ClinicalSession(uri="STUDY001")
session.define_report(dataset=adsl, subjid="USUBJID")
session.add_trt(name="TRT01PN", decode="TRT01P")
session.add_var(name="AGE", stats="n mean+sd median min max")
session.add_var(name="SEX", stats="n pct")
session.generate()
session.finalize(output_path="demographics.rtf", format="rtf")
```

### Future Plans

- Additional statistical tests
- More visualization options
- Enhanced PDF formatting
- Jupyter notebook integration
- Real-time collaboration features

---

[Unreleased]: https://github.com/yanmingyu92/py4csr/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yanmingyu92/py4csr/releases/tag/v0.1.0