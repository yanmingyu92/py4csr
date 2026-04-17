# py4csr: Python for Clinical Study Reporting

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)
[![Tests](https://img.shields.io/badge/tests-710%20passing-success.svg)](tests/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Documentation](https://img.shields.io/badge/docs-sphinx-blue.svg)](docs/)
[![CDISC Compliant](https://img.shields.io/badge/CDISC-compliant-purple.svg)](examples/)
[![RTF Ready](https://img.shields.io/badge/RTF-regulatory%20ready-red.svg)](examples/sample_outputs/)
[![Interactive HTML](https://img.shields.io/badge/HTML-interactive%20plots-brightgreen.svg)](examples/sample_outputs/figures/)

**py4csr** is a Python framework for clinical study reporting, designed for pharmaceutical and biotech companies. Built on functional programming principles and modular architecture, it enables efficient generation of regulatory-compliant clinical reports from reusable, combinable components.

---

## Key Features

**Functional Composition & Modularity**
- Build complex reports through intuitive method chaining and function composition
- Combine reusable statistical components (demographics, safety, efficacy) dynamically
- Immutable data transformations ensure reproducibility and audit trails
- Pre-built statistical templates for common clinical endpoints

**Regulatory Compliance**
- ICH E3 and CTD-ready outputs meeting FDA submission standards
- Built-in data quality checks and validation
- Dual-format output: regulatory RTF and interactive HTML from the same code

**Production-Grade Analytics**
- Specialized clinical plots: Kaplan-Meier, Forest, Waterfall, Box, Line
- Interactive HTML plots with zoom, hover, and filter capabilities
- Multiple output formats: RTF, PDF, HTML, Excel
- Performance-optimized for large clinical datasets

> **16 Professional Sample Outputs** — 7 Clinical Tables, 8 Clinical Figures (RTF + Interactive HTML), 1 Safety Listing

---

## Installation

**Basic**
```bash
pip install py4csr
```

**With PDF support**
```bash
pip install py4csr[pdf]
```

**Development**
```bash
git clone https://github.com/yanmingyu92/py4csr.git
cd py4csr
pip install -e ".[dev]"
```

**Requirements**: Python 3.9+, pandas, numpy, scipy, matplotlib, seaborn. Optional: reportlab (PDF), openpyxl (Excel).

---

## Quick Start

### Clinical Session Interface

```python
from py4csr.clinical import ClinicalSession
import pandas as pd

adsl = pd.read_csv("data/adsl.csv")

session = ClinicalSession(uri="STUDY001")
session.define_report(
    dataset=adsl,
    subjid="USUBJID",
    title="Table 14.1.1 Demographics and Baseline Characteristics"
)

# Configure treatment groups and variables
session.add_trt(name="TRT01PN", decode="TRT01P", across="Y")
session.add_var(name="AGE", label="Age (years)", stats="n mean+sd median q1q3 min+max")
session.add_catvar(name="SEX", label="Sex, n (%)", stats="npct", codelist="M='Male',F='Female'")
session.add_catvar(name="RACE", label="Race, n (%)", stats="npct")

session.generate()
session.finalize(output_path="demographics.rtf", format="rtf")
```

### Functional Interface (Method Chaining)

```python
from py4csr.functional import ReportSession

session = (ReportSession()
    .init_study(uri="STUDY001", title="Phase III Efficacy and Safety Study",
                protocol="ABC-123-2024")
    .load_datasets(data_path="data/")
    .define_populations(safety="SAFFL=='Y'", efficacy="EFFFL=='Y'")
    .define_treatments(var="TRT01P")
    .add_demographics_table()
    .add_disposition_table()
    .add_ae_summary()
    .add_efficacy_analysis()
    .create_kaplan_meier_plot(time_var="AVAL", event_var="CNSR")
    .create_forest_plot(endpoint="CHG", subgroups=["SEX", "AGEGR1"])
    .generate_all()
    .finalize()
)
```

### Advanced Configuration

```python
from py4csr.functional import ReportSession, FunctionalConfig

config = FunctionalConfig.clinical_standard()
config.add_statistic("geometric_mean", "Geometric Mean")
config.set_format("p_value", "{:.4f}")

session = (ReportSession(config)
    .init_study(uri="ADVANCED-001", title="Advanced Analysis")
    .load_datasets(data_path="data/")
    .define_populations(safety="SAFFL=='Y'", efficacy="EFFFL=='Y'")
    .define_treatments(var="TRT01P")
    .add_grouping("age_group", "AGEGR1", {"<65": "Young", ">=65": "Elderly"})
    .add_conditional_formatting("p_value", lambda x: x < 0.05, "highlight")
    .add_demographics_table(by_group="age_group")
    .add_ae_summary(include_severity=True)
    .add_efficacy_analysis(endpoints=["AVAL", "CHG"])
    .create_kaplan_meier_plot(time_var="AVAL", event_var="CNSR")
    .create_forest_plot(endpoint="CHG", subgroups=["SEX", "AGEGR1"])
    .generate_all()
    .finalize()
)
```

For more examples, see the [Quick Start Guide](docs/quickstart.rst) and [Examples](examples/).

---

## Sample Outputs

All sample outputs are available in `examples/sample_outputs/`. Generated from synthetic data only — no real patient data is used.

### Clinical Tables (7)

| Table | File | Description |
|-------|------|-------------|
| Demographics | `t_dem.rtf` | Baseline characteristics with statistical comparisons |
| Adverse Events | `t_ae_sum.rtf` | Safety analysis by SOC/PT |
| Vital Signs | `t_vs_sum.rtf` | Change from baseline with clinical significance |
| Subject Disposition | `t_disp.rtf` | Patient flow and completion rates |
| Drug Exposure | `t_exposure.rtf` | Treatment compliance and duration |
| Laboratory Chemistry | `t_lb_sum_chem.rtf` | Clinical chemistry with shift tables |
| Efficacy Response | `t_eff_response.rtf` | Primary endpoint analysis with statistics |

### Clinical Figures (8 — RTF + Interactive HTML)

| Figure | RTF | HTML | Description |
|--------|-----|------|-------------|
| Kaplan-Meier | `km_enhanced_example.rtf` | `km_enhanced_example.html` | Survival analysis with risk tables |
| Forest Plot | `forest_enhanced_example.rtf` | `forest_enhanced_example.html` | Subgroup efficacy analysis |
| Box Plot | `box_plot_clinical_example.rtf` | `box_plot_clinical_example.html` | Distribution by treatment group |
| Line Plot | `line_plot_clinical_example.rtf` | `line_plot_clinical_example.html` | Longitudinal trends over time |

### Clinical Listings (1)

| Listing | File | Description |
|---------|------|-------------|
| AE Deaths | `l_ae_death.rtf` | Individual patient safety listings |

---

## Architecture

```
py4csr/
├── functional/              # Functional programming interface
│   ├── session.py           # ReportSession class
│   ├── config.py            # Configuration management
│   └── templates.py         # Statistical templates
├── clinical/                # Direct clinical interface
│   ├── session.py           # ClinicalSession class
│   ├── statistical_engine.py       # Statistics calculations
│   └── enhanced_rtf_formatter.py   # Professional RTF output
├── data/                    # Data I/O and manipulation
├── analysis/                # Statistical analysis
├── plotting/                # Clinical plotting
├── reporting/               # Output generation
├── validation/              # Quality checks
└── examples/                # Example scripts and data
```

### Core Modules

| Module | Description |
|--------|-------------|
| `py4csr.functional` | Functional reporting interface with method chaining |
| `py4csr.clinical` | Direct clinical reporting system |
| `py4csr.data` | Data loading and manipulation utilities |
| `py4csr.analysis` | Statistical analysis functions |
| `py4csr.plotting` | Clinical plot generation (Kaplan-Meier, Forest, etc.) |
| `py4csr.reporting` | Report generation and formatting |
| `py4csr.validation` | Data quality and compliance checking |

### Key Classes

- **`ReportSession`** — Main orchestrator for functional reporting
- **`ClinicalSession`** — Direct clinical reporting interface
- **`FunctionalConfig`** — Configuration management for reports
- **`TableBuilder`** — Functional table construction
- **`StatisticalTemplates`** — Reusable statistical calculations
- **`PlottingEngine`** — Clinical plot generation

---

## Testing

Tested with real clinical trial data including the CDISC Pilot Study (254 subjects, 10 ADaM datasets, ~92 MB) covering demographics, adverse events, laboratory, vital signs, and questionnaires with complex scenarios (multiple visits, missing data, regulatory requirements).

```python
from py4csr.examples import load_cdisc_pilot_data

datasets = load_cdisc_pilot_data()
for name, df in datasets.items():
    print(f"  {name}: {len(df)} records")

session = create_regulatory_report_session(datasets)
result = session.generate_all().finalize()
```

---

## Citation

If you use **py4csr** in your research or clinical reporting workflows, please cite:

> Jaime Yan. (2026). py4csr: Python for Clinical Study Reporting. Zenodo. https://doi.org/10.5281/zenodo.19621900

```bibtex
@software{yan_py4csr,
  author       = {Jaime Yan},
  title        = {py4csr: Python for Clinical Study Reporting},
  year         = {2026},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.19621900},
  url          = {https://doi.org/10.5281/zenodo.19621900}
}
```

---

## Contributing

We welcome contributions. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [py4csr.readthedocs.io](https://py4csr.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/yanmingyu92/py4csr/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yanmingyu92/py4csr/discussions)
- **Email**: yanmingyunmt@gmail.com

## Roadmap

**v1.1** — Enhanced CDISC metadata integration, additional statistical tests, interactive dashboard generation, cloud deployment templates

**v1.2** — Real-time data monitoring, advanced ML integration, multi-language support, enterprise features
