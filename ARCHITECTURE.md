# py4csr Architecture

> Status: living document, written for the v2 repositioning (see `CHANGELOG.md` and the
> project roadmap). It inventories the codebase as it actually exists at v0.1.1 and
> separates the **table engine core** (the v2 focus) from **rendering/output** code
> (to be replaced by external backends) and **legacy** modules (kept working, but out
> of the main narrative).
>
> v2 direction: py4csr becomes a **Python summary table engine, ARD-first** — the
> layer equivalent to gtsummary's `tbl_summary()` in R. Statistics and table
> structure live here; rendering is delegated to external backends
> (`great_tables` for HTML/Word, `rtflite` for RTF).

---

## 1. How the code actually flows today

The most complete path is the `ClinicalSession` workflow in
`py4csr/clinical/session.py`:

```
define_report(dataset, pop_where, titles, footnotes, ...)
add_trt(name, decode, across, ...)                # treatment/column definition
add_var(name, label, stats="n mean+sd ...")       # continuous variables
add_catvar(name, label, stats="npct", codelist=)  # categorical variables
add_cond(...) / add_group(...)                    # condition rows, shift-table groups
        │
        ▼
generate()                                        # session.py:852
        │  1. applies pop_where / tab_where filters
        │  2. calls ClinicalStatisticalEngine per variable
        │  3. concatenates results into self.generated_data
        │     — a long/tidy DataFrame, one row per
        │       treatment × variable × statistic, with raw `value`
        │       and `formatted_value`
        │  4. pivots to display form via _format_for_display()
        ▼
finalize(output_file, output_format)              # session.py:1547
        └─► EnhancedClinicalRTFFormatter / ClinicalPDFFormatter / CSV
```

Two observations drive the v2 design:

1. **`generated_data` is already a proto-ARD.** It is a long-format results
   dataset keyed by `(treatment, variable, statistic)` with both raw and formatted
   values — the same shape the CDISC Analysis Results Standard (ARS) and R's
   `{cards}` package converge on. v2 formalizes this instead of inventing it.
2. **Statistics and rendering are separable in practice.** Everything up to
   `_format_for_display()` is presentation-independent; only `finalize()` touches
   RTF/PDF. That seam is where external rendering backends plug in.

---

## 2. Table engine core (v2 focus)

| Module | What it does | Notes |
|---|---|---|
| `py4csr/clinical/session.py` | `ClinicalSession`: variable-accumulation table builder. `add_var` / `add_catvar` semantics (stats spec strings like `"n mean+sd median q1q3 min+max"`, `"npct"`, codelists, denominators, population filters) are the source semantics for the future `tbl_summary()` API. | 1815 lines; mixes orchestration and display formatting — to be split in v2. |
| `py4csr/clinical/statistical_engine.py` | `ClinicalStatisticalEngine`: the actual math. `calculate_continuous_stats`, `calculate_categorical_stats`, `calculate_shift_table_stats`, `calculate_condition_stats`, plus `perform_anova` / `perform_chi_square` / `perform_fisher_exact`. Parses stats-spec strings and produces formatted values. | The statistical heart of the package. |
| `py4csr/functional/statistical_templates.py` | `StatisticalTemplates`: reusable stat calculators used by the functional interface. | Overlaps with `statistical_engine.py`; v2 should converge on one stats layer. |
| `py4csr/functional/table_builder.py` | `TableBuilder`: functional table construction from statistical components. | Distinct from `tables/table_builder.py` (see §5). |
| `py4csr/reporting/table_specification.py` | Declarative table spec model (variables, treatments, titles, footnotes). | Natural home for a v2 "table shell" object. |
| `py4csr/reporting/table_result.py` | `TableResult` / `ReportResult` containers. | Natural home for the v2 ARD-carrying result object. |
| `py4csr/reporting/generators/` | Per-table-type generators: demographics, AE summary/detail, disposition, laboratory, efficacy, survival (`factory.py` dispatches). | Domain templates built on the core; kept, but layered above the engine. |
| `py4csr/analysis/` (subset) | Statistical helpers feeding tables: `demographics.py`, `categorical.py`, `binomial.py`, `odds_ratio.py`, `population.py`, `safety.py`, `utils.py` (e.g. `format_pvalue`). | Continuous/categorical summary stats are core; efficacy/survival modeling is legacy (§4). |
| `py4csr/data/` | Input layer: `io.py` (CSV/SAS/XPT/Excel readers), `validation.py` (ADaM checks), `adam_utils.py`, `preprocessing.py`. | Stays: the engine needs a clean ADaM-facing input layer. |
| `py4csr/config/`, `py4csr/functional/config.py` | `ReportConfig`, `FunctionalConfig.clinical_standard()`, statistic/format definitions. | Configuration for the core. |
| `py4csr/exceptions.py` | Error taxonomy (`DataValidationError`, `StatisticalError`, …). | Core. |

## 3. Rendering / output (to be replaced by external backends)

These modules exist only to turn finished tables into files. In v2 this layer is
replaced by `great_tables` (HTML/Word) and `rtflite` (RTF); the in-repo formatters
are kept working until the backends land, then deprecated.

| Module | What it does |
|---|---|
| `py4csr/clinical/enhanced_rtf_formatter.py` | RTF output for `ClinicalSession.finalize()`. |
| `py4csr/clinical/pdf_formatter.py` | ReportLab-based PDF output (partially implemented; tests mark it "not fully implemented"). |
| `py4csr/reporting/rtf_table.py` | Second RTF implementation ("compatible with r2rtf"). |
| `py4csr/reporting/rtf_document.py` | RTF document wrapper. |
| `py4csr/reporting/formatters.py` | Output formatting helpers. |
| `py4csr/tables/rtf_formatter.py` | Third RTF implementation ("publication-quality"). |
| `py4csr/tables/table_builder.py` | Table builder wired to `tables/rtf_formatter.py`. |
| `py4csr/functional/output_generators.py` | `RTFGenerator` / `PDFGenerator` / `HTMLGenerator` for the functional interface. |
| `py4csr/plotting/sas_compatible_rtf_generator.py` | RTF embedding for plots. |

Three independent RTF codepaths (`clinical/enhanced_rtf_formatter.py`,
`reporting/rtf_table.py`, `tables/rtf_formatter.py`) are the strongest internal
argument for delegating rendering: the project maintains ~1,400 lines of RTF
generation across three files, none of which is the statistical core.

## 4. Legacy (kept working, out of the main narrative)

Working, tested code that no longer defines the project's identity. It remains
importable and covered by tests, but new investment goes to the core.

| Module | Why legacy |
|---|---|
| `py4csr/plotting/comprehensive_clinical_plots.py` (4,750 lines), `plot_result.py`, `py4csr/functional/plotting_engine.py` | Clinical figures (KM, forest, waterfall…). A mature ecosystem exists (matplotlib/plotly direct use, future dedicated packages); plotting is not the table engine's job. |
| `py4csr/analysis/efficacy.py`, `enhanced_efficacy.py`, `survival.py`, `advanced_anova.py`, `advanced_safety.py`, `statistical_extensions.py` | Inferential/modeling analyses (ANCOVA, survival, logistic). Out of scope for a summary-table engine; results can enter tables via the ARD instead. |
| `py4csr/functional/session.py` (`ReportSession`), `advanced_features.py`, `advanced_utilities.py`, `workflow_enhancement.py`, `py4csr/core/` (`CSRPipeline`, `DataProcessor`), `py4csr/reporting/report_builder.py`, `clinical_reports.py`, `clinical_study_reports.py`, `templates.py`, `py4csr/clinical/clinical_report.py` | End-to-end orchestration ("run my whole CSR"). This was the old "do everything" framework story; v2 is a composable building block, not an orchestrator. |
| `py4csr/clinical/listing_session.py` | Patient-level listings. Adjacent deliverable, not summary tables; stays as an extra. |

## 5. Known structural issues (honest inventory)

- **Two `TableBuilder` classes**: `py4csr/functional/table_builder.py` and
  `py4csr/tables/table_builder.py` are unrelated implementations.
- **Three RTF formatters** (see §3) with overlapping responsibility.
- **Two statistical layers** (`clinical/statistical_engine.py` vs
  `functional/statistical_templates.py`) computing the same quantities.
- `ClinicalSession` mixes spec, statistics, display pivot, and file output in one
  class — v2 splits these along the seam described in §1.
- Session methods log via `print()` rather than the `logging` module.
- Test suite status at v0.1.1 (verified locally): 717 passed, 4 failed, 15 skipped
  (`pytest tests`). The 4 failures are pre-existing, in
  `data/adam_utils.py`, `data/preprocessing.py`,
  `functional/output_generators.py` (PDF-without-reportlab path), and
  `data/validation.py` — none in the table engine core.

---

## 6. v2 direction: ARD-first

**Interchange format.** The engine's output contract is an **Analysis Results
Dataset (ARD)** — a long/tidy DataFrame, one row per result, aligned with CDISC
Analysis Results Standard concepts (and R `{cards}`):

| ARD column (v2) | Concept | Already present as |
|---|---|---|
| `group1` / `group1_level` | Analysis grouping (treatment arm) | `generated_data["treatment"]` |
| `variable` / `variable_label` | Analysis variable | `variable`, `variable_label` |
| `stat_name` / `stat_label` | Statistic identifier and display label | `statistic` (label only today) |
| `stat` | Raw (unrounded, unformatted) result | `value` |
| `stat_fmt` / formatted string | Presentation of the result | `formatted_value` |
| `context` | Derivation context (summary vs. test vs. shift) | derivable from `variable_type` + spec |
| `analysis_id` / `table_id` | Which output this result belongs to | `ClinicalSession.uri` |

The delta from today's `generated_data` to a documented ARD schema is small and
mechanical — which is the point: py4csr already computes an ARD, it just doesn't
name or guarantee it.

**Rendering split.** v2 turns the §1 seam into an explicit contract:

```
ADaM data ──► py4csr table engine ──► ARD (guaranteed, versioned schema)
                                       │
                                       ├─► table shell (wide DataFrame)
                                       │
                                       └─► external backends:
                                           great_tables → HTML / Word
                                           rtflite      → RTF
```

py4csr guarantees the numbers and the structure; backends guarantee the pixels.
The in-repo RTF/PDF formatters remain for backward compatibility during the
transition.

**API sketch** (distilled from existing `add_var` / `add_catvar` semantics; design
target, not yet implemented):

```python
import py4csr

tbl = py4csr.tbl_summary(
    data=adsl,
    by="TRT01P",                              # was add_trt(name=, decode=)
    include=["AGE", "SEX", "RACE"],
    statistic={
        "AGE": "n mean+sd median q1q3 min+max",  # today's add_var stats= string
        "SEX": "npct",                            # today's add_catvar stats=
        "RACE": "npct",
    },
    label={"AGE": "Age (years)", "SEX": "Sex, n (%)", "RACE": "Race, n (%)"},
    where="SAFFL == 'Y'",                     # was define_report(pop_where=)
    total=True,                               # today's automatic Total column
)

tbl.ard          # long-format Analysis Results Dataset (the interchange contract)
tbl.to_table()   # wide display table (today's generated_table)
tbl.render(backend="great_tables")             # external rendering
```

The stats-spec mini-language (`"n mean+sd median q1q3 min+max"`, `"npct"`,
codelists, denominator controls) is carried over from
`ClinicalStatisticalEngine._parse_stats_spec` /
`_parse_categorical_stats_spec`, so existing `add_var`/`add_catvar` code maps
onto the new API mechanically. `ClinicalSession` remains supported as a thin
compatibility wrapper during the transition.
