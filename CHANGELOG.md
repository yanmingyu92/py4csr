# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-01-XX

### Added
- Initial release of py4csr package
- Core data processing functionality for CDISC ADaM datasets
- RTF table generation equivalent to R r2rtf package
- Demographics analysis similar to R table1 package
- Statistical analysis functions (ANCOVA, survival analysis)
- Safety analysis for adverse events and laboratory data
- Data validation functions for clinical datasets
- TLF (Tables, Listings, Figures) generator
- Command-line interface for common tasks
- Comprehensive documentation and examples
- Support for SAS (.sas7bdat) and XPT file formats
- Template system for consistent report formatting

### Features
- **Data Processing**: Read SAS files, validate CDISC standards, handle missing data
- **Statistical Analysis**: Demographics tables, ANCOVA, Kaplan-Meier survival analysis
- **Safety Analysis**: Adverse events summaries, laboratory data analysis
- **Report Generation**: RTF tables with professional formatting
- **Validation**: Built-in QC checks for clinical data quality
- **Templates**: Predefined templates for common clinical reports

### Dependencies
- pandas >= 1.5.0
- numpy >= 1.21.0
- scipy >= 1.7.0
- statsmodels >= 0.13.0
- pyreadstat >= 1.1.5
- And other scientific Python packages

### Documentation
- Comprehensive README with installation and usage instructions
- Example scripts demonstrating key functionality
- API documentation for all modules
- Clinical data standards compliance notes 