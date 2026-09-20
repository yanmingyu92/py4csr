# py4csr: Python for Clinical Study Reporting

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**py4csr is a Python engine for clinical summary tables — ADaM data in, submission-ready table out, with the Analysis Results Dataset (ARD) as the interchange format.** It is the Python counterpart of the summary-table layer R users know from gtsummary's `tbl_summary()`: you declare variables and statistics, py4csr computes a tidy results dataset and a display-ready table.

Rendering is being delegated to external backends ([great_tables](https://posit-dev.github.io/great-tables/) for HTML/Word, [rtflite](https://merck.github.io/rtflite/) for RTF). py4csr focuses on the part that must be deterministic and verifiable: the statistics and the table structure. See [ARCHITECTURE.md](ARCHITECTURE.md) for the full design.

---

## What it does

- **Declarative table specification** — add continuous variables (`add_var`) and categorical variables (`add_catvar`) with a compact stats-spec language: `"n mean+sd median q1q3 min+max"`, `"npct"`, codelists, denominator and population controls.
- **Statistical engine** — continuous and categorical summaries, shift tables, condition rows, and common tests (ANOVA, chi-square, Fisher's exact), computed per treatment group with raw and formatted values side by side.
- **Tidy results dataset (proto-ARD)** — every table is first produced as a long-format DataFrame keyed by treatment × variable × statistic, aligned with CDISC Analysis Results Standard concepts. Numbers are inspectable and testable before any rendering happens.
- **Output** — RTF, PDF, and CSV today; external rendering backends on the roadmap (see below).

py4csr works with CDISC ADaM datasets (ADSL, ADAE, ADLB, ADVS, …) and reads CSV, SAS (`.sas7bdat`, XPT), and Excel inputs.

## Installation

**Basic**
```bash
pip install py4csr
```

**With PDF or SAS support**
```bash
pip install py4csr[pdf]
pip install py4csr[sas]
```

**Development**
```bash
git clone https://github.com/yanmingyu92/py4csr.git
cd py4csr
pip install -e ".[dev]"
```

**Requirements**: Python 3.9+, pandas, numpy, scipy. Optional: reportlab (PDF), pyreadstat (SAS), openpyxl (Excel).

---

## Quick Start

A demographics table from an ADSL dataset:

```python
from py4csr.clinical import ClinicalSession
import pandas as pd

adsl = pd.read_csv("data/adsl.csv")

session = ClinicalSession(uri="STUDY001")
session.define_report(
    dataset=adsl,
    subjid="USUBJID",
    title1="Table 14.1.1 Demographics and Baseline Characteristics",
)
session.add_trt(name="TRT01PN", decode="TRT01P", across="Y")
session.add_var(name="AGE", label="Age (years)", stats="n mean+sd median q1q3 min+max")
session.add_catvar(name="SEX", label="Sex, n (%)", stats="npct", codelist="M='Male',F='Female'")
session.add_catvar(name="RACE", label="Race, n (%)", stats="npct")

session.generate()
session.finalize(output_file="demographics.rtf", output_format="rtf")
```

The same session exposes the results before rendering. `session.generated_data` is
the long-format results dataset (proto-ARD); `session.generated_table` is the wide
display table:

```python
session.generate()
ard = session.generated_data      # one row per treatment × variable × statistic
print(ard[["treatment", "variable", "statistic", "value", "formatted_value"]].head())
```

More runnable scripts live in [`examples/`](examples/), using synthetic data only.

---

## Evidence, not claims

Clinical reporting is a regulated domain, so this project shows its work instead of asserting compliance:

- **Test suite** — unit and integration tests under [`tests/`](tests/), covering the statistical engine, table builders, data handling, and output generators. Run it yourself:
  ```bash
  pip install -e ".[dev]"
  pytest tests
  ```
- **CDISC Pilot validation script** — [`tests/test_real_data.py`](tests/test_real_data.py) runs the reporting flow against the CDISC Pilot Study ADaM datasets (254 subjects, 10 datasets). The data is not shipped in this repository; place the `.sas7bdat` files in a `data/` directory to run it.
- **Examples** — runnable scripts in [`examples/`](examples/) (synthetic data only; no real patient data in this repo).

If you find a number py4csr computes incorrectly, that is a bug — please [open an issue](https://github.com/yanmingyu92/py4csr/issues).

## Beyond tables

The package also contains plotting (Kaplan-Meier, forest, and other clinical figures), patient listings, and an end-to-end report orchestration interface. These remain available and tested, but they are extras — the project's focus is the summary table engine. See [ARCHITECTURE.md](ARCHITECTURE.md) for the core/legacy breakdown.

## Architecture

```
py4csr/
├── clinical/          # ClinicalSession table workflow + statistical engine
├── functional/        # Functional interface (config, templates, table builder)
├── analysis/          # Statistical functions
├── reporting/         # Table specs, results, per-table generators, formatters
├── data/              # ADaM input, validation, preprocessing
├── plotting/          # Clinical figures (extra)
└── core/, config/, tables/
```

Full inventory, including what becomes the v2 core and what is legacy: [ARCHITECTURE.md](ARCHITECTURE.md).

## Roadmap

The live, detailed version of this roadmap is a public GitHub Project: [py4csr Roadmap](https://github.com/users/yanmingyu92/projects/1) — including what's in progress now and where contributions are most welcome.

1. **ARD-first table engine v2** — a `tbl_summary()`-style API distilled from the existing `add_var`/`add_catvar` semantics, with a documented, versioned Analysis Results Dataset schema as the output contract.
2. **External rendering backends** — render tables via great_tables (HTML/Word) and rtflite (RTF); keep the in-repo formatters for backward compatibility during the transition.
3. **Reproducibility evidence** — end-to-end CDISC Pilot reproduction with snapshot tests in CI, so results are continuously checked, not just claimed.

## Contributing

Contributions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). Good starting points are the table engine core and the ARD schema discussion.

## License

MIT — see [LICENSE](LICENSE).

## Citation

If you use **py4csr** in your work, please cite:

> Jaime Yan. (2025). py4csr: Python for Clinical Study Reporting. Zenodo. https://doi.org/10.5281/zenodo.19621900

```bibtex
@software{yan_py4csr_2025,
  author       = {Jaime Yan},
  title        = {py4csr: Python for Clinical Study Reporting},
  year         = {2025},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.19621900},
  url          = {https://doi.org/10.5281/zenodo.19621900}
}
```

## Support

- **Issues**: [GitHub Issues](https://github.com/yanmingyu92/py4csr/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yanmingyu92/py4csr/discussions)
