# py4csr vs gtsummary: Cross-Validation Report — Demographics Table

**Date:** 2026-09-20 (updated: Wilcoxon default closes the last p-value gap)
**Harness:** `validation/compare_gtsummary.py` (fully reproducible, no R required)
**Verdict up front:** after three minimal bug fixes in py4csr's table core **and
switching the default continuous p-value test to gtsummary's default (Wilcoxon
rank-sum / Kruskal-Wallis)**, **99/99 compared cells match the independent
reference at tolerance 1e-6 (100%) — including p-values**, and **40/40 published
gtsummary output values for the same dataset are reproduced exactly** (up to the
published rounding). py4csr can credibly claim gtsummary parity for the standard
demographics/baseline table use case.

---

## 1. Ground-truth method (important — no R on this machine)

`Rscript` is **not available** on this Windows host, so gtsummary could not be executed
directly. Per the pre-agreed fallback, two independent ground truths were used:

1. **Independent reference recomputation** — every statistic recomputed from the same
   input CSV with numpy/scipy/pandas inside `compare_gtsummary.py`, implementing R /
   gtsummary definitions explicitly:
   - SD with ddof=1 (R `sd()`)
   - quantiles with **R type 2** (`averaged_inverted_cdf`), which is what gtsummary's
     `p25`/`p50`/`p75` summaries use (`stats::quantile(..., type = 2)`, see
     `gtsummary/R/tbl_summary.R:802`) and equals SAS `PCTLDEF=5`
   - Pearson chi-square **without** Yates continuity correction (gtsummary `add_p()`
     default, "Pearson's Chi-squared test"; also SAS PROC FREQ's Pearson statistic)
   - Wilcoxon rank-sum (gtsummary default for 2-group continuous) and one-way ANOVA /
     pooled t-test (what py4csr implements) for p-value context
2. **gtsummary's bundled `trial` dataset with its documented outputs** — `trial.rda`
   pulled from the [gtsummary GitHub repo](https://github.com/ddsjoberg/gtsummary)
   (`data/trial.rda`, converted to CSV with pyreadr), and the **published numbers in
   the official [`tbl_summary` vignette](https://www.danieldsjoberg.com/gtsummary/articles/tbl_summary.html)**
   hard-coded into the harness as 39 anchor cells (counts, medians, Q1/Q3, means, SDs,
   min/max, missing counts, and two documented p-values). These anchors validate the
   reference implementation itself against gtsummary's real output.

Result: reference implementation reproduces **39/39** documented gtsummary values —
the reference is a faithful stand-in for running gtsummary.

## 2. Dataset

gtsummary::`trial` — simulated cohort, n=200, Drug A (n=98) vs Drug B (n=102).
Reshaped to ADSL style (`validation/data/adsl_trial.csv`):

| Variable | Source | Type | Notes |
|---|---|---|---|
| `TRT01P` | `trt` | treatment | Drug A / Drug B |
| `AGE` | `age` | continuous | 11 missing (7 in A, 4 in B) — exercises missing handling |
| `AGEGR1` | derived: `<65` / `>=65` | categorical | ADSL-style age group; missing where AGE missing |
| `GRADE` | `grade` | categorical | I / II / III (Roman numerals — exposed a label bug) |
| `STAGE` | `stage` | categorical | T1–T4 |

The `trial` dataset has no SEX/RACE columns; the categorical n(%) machinery is
identical for any coded categorical, and GRADE/STAGE/AGEGR1 cover 2-, 3- and
4-level cases plus missing categories. py4csr's race-label handling is a hardcoded
mapping (`_format_category_name`) exercised separately by its own unit tests.

Table built through the full public API: `ClinicalSession` → `define_report` →
`add_trt` → `add_var(AGE, stats="n mean sd median q1 q3 min max")` →
`add_catvar(..., stats="npct")` → `generate()`; machine-readable cells taken from
`session.generated_data`, p-values from both `session.p_values` and the raw
`ClinicalStatisticalEngine` methods.

## 3. Results (after fixes)

Tolerance: 1e-6 on raw values; 5e-4 on `session.p_values` strings (they are formatted
to 3 decimals by design). Raw engine p-values compared at 1e-6.

| Statistic | Cells | Matched | Rate |
|---|---|---|---|
| n (continuous) | 3 | 3 | 100% |
| mean | 3 | 3 | 100% |
| SD | 3 | 3 | 100% |
| median | 3 | 3 | 100% |
| Q1 | 3 | 3 | 100% |
| Q3 | 3 | 3 | 100% |
| min / max | 6 | 6 | 100% |
| n (categorical, incl. Missing rows) | 36 | 36 | 100% |
| % (categorical) | 30 | 30 | 100% |
| p-value: chi-square (GRADE, STAGE, AGEGR1) | 3 (+3 formatted) | 6 | 100% |
| p-value: Wilcoxon rank-sum (AGE; now the default) | 1 (+1 formatted) | 2 | 100% |
| p-value: ANOVA (AGE; kept as configurable option) | 1 | 1 | 100% |
| **Total** | **99** | **99** | **100%** |

gtsummary documented anchors: **40/40 match**, including vignette values
Age median (Q1, Q3) = 46 (37, 60) / 48 (39, 56) by arm; mean (SD) = 47.01 (14.71) /
47.45 (14.01); min/max = 6, 78 / 9, 83; Grade I/II/III = 35 (36%) / 32 (33%) /
31 (32%) on Drug A; stage cross-counts; chi-square p = 0.87 for Grade; Wilcoxon
rank-sum p = 0.72 for Age (py4csr session reports 0.718).

### Update (2026-09-20): continuous p-value test now matches gtsummary defaults

- `ClinicalStatisticalEngine` gains `perform_wilcoxon` (2 groups, scipy
  `mannwhitneyu` two-sided), `perform_kruskal` (>2 groups), `perform_ttest`, and
  two dispatchers with explicit test selection: `perform_continuous_test(test=)`
  and `perform_categorical_test(test=)`.
- With `test="auto"` (the new default), continuous variables use Wilcoxon
  rank-sum for 2 groups and Kruskal-Wallis for >2 groups — gtsummary's
  `add_p()` defaults. ANOVA/t-test remain available via `test="anova"` /
  `test="ttest"`.
- Categorical `test="auto"` keeps Pearson chi-square without continuity
  correction and switches to Fisher's exact test when any expected cell count
  is < 5 (gtsummary behavior); Fisher supports RxC tables via a fixed-seed
  Monte Carlo (deterministic).
- The session exposes the same choice per variable (`add_var(..., test=...)`,
  `add_catvar(..., test=...)`) and records the test actually used in
  `session.p_value_tests`; the RTF/PDF methodology footnote is now generated
  from those recorded tests, so a regulatory footnote can state the test.
- Result on the `trial` dataset: AGE p = **0.718** (Wilcoxon) vs gtsummary
  documented **0.72** — the last definitional gap is closed.

Machine-readable detail: `validation/comparison_results.csv`,
`validation/comparison_summary.json`.

## 4. Bugs found in py4csr's table core — all fixed minimally

### Bug 1 — Wrong quantile definition (real numeric bug)
- **Symptom:** AGE Q3, Drug A: py4csr = 59.0; gtsummary documented = 60.
- **Root cause:** py4csr used pandas `.quantile()` default (R **type 7**, linear
  interpolation). gtsummary uses `stats::quantile(..., type = 2)` and SAS uses
  `PCTLDEF=5` — both are the averaged-inverted-CDF definition. For Drug A (n=91),
  the Q3 position falls between the 68th (58) and 69th (60) ordered values: type 7
  interpolates to 59, type 2 gives 60.
- **Fix** (`py4csr/clinical/statistical_engine.py`, `_calculate_single_continuous_stat`):
  Q1/Q3/Q1Q3 now use `np.percentile(..., method="averaged_inverted_cdf")`.
  Median/min/max unaffected (identical under both definitions).

### Bug 2 — Yates continuity correction on 2×2 chi-square (real numeric bug)
- **Symptom:** AGEGR1 (2×2) p-value: py4csr = 0.9938; gtsummary convention = 0.8265.
- **Root cause:** `scipy.stats.chi2_contingency()` defaults to `correction=True`
  (Yates) for 2×2 tables. gtsummary's default is Pearson chi-square **without**
  continuity correction, as is SAS PROC FREQ's headline "Pearson Chi-Square".
  (>2-level tables were unaffected — Yates only applies to 2×2 — which is why GRADE
  and STAGE matched even before the fix.)
- **Fix:** `correction=False` in
  `ClinicalStatisticalEngine.perform_chi_square`
  (`py4csr/clinical/statistical_engine.py`) and in the p-value collection in
  `ClinicalSession._collect_p_values` (`py4csr/clinical/session.py`).

### Bug 3 — Roman-numeral category labels mangled (display bug)
- **Symptom:** GRADE levels printed as "Ii" / "Iii" instead of "II" / "III".
- **Root cause:** `_format_category_name` blindly title-cased every category.
  Counts were always correct; only labels were wrong.
- **Fix** (`py4csr/clinical/statistical_engine.py`): Roman numerals
  (`^[IVXLCDM]+$`) and uppercase alphanumeric codes (e.g. "T1") are preserved
  verbatim; prose labels ("FEMALE" → "Female") still title-case as before, so the
  existing unit-test contract is kept.

### Regression check
- py4csr's own suite (2026-09-20, after the Wilcoxon-default change, robustness
  pass and pandas-3.0 fixes): **721 passed, 24 skipped** (skips are optional
  dependencies: plotly/statsmodels/reportlab, plus intentional not-implemented
  stubs). The 4 pre-existing pandas-3.0 failures in `test_data_io.py`,
  `test_data_preprocessing.py`, `test_data_adam_utils.py`, `test_validation.py`
  are fixed (`fillna(method=)` → `.ffill()`; object-dtype handling for StringDtype;
  `FileNotFoundError` before the optional `pyreadstat` check).
- End-to-end RTF smoke test (`generate()` → `finalize("demographics.rtf")`) passes;
  table p-values now read Grade 0.871 (= documented 0.87) and Age 0.718
  (= documented Wilcoxon 0.72).

## 5. Known definitional differences (not bugs — disclosure required)

- ~~**Continuous p-value test choice.**~~ **Resolved 2026-09-20:** py4csr's default
  continuous p-value test is now Wilcoxon rank-sum (2 arms) / Kruskal-Wallis (>2
  arms), exactly gtsummary's `add_p()` default: AGE p = 0.718 vs documented 0.72.
  ANOVA/t-test remain available as explicit `test=` options.
- **Percentage denominator with missing data.** py4csr uses the full column N
  (including missing) — consistent with gtsummary's `percent="column"` when the
  "Unknown" row is displayed (its default). No discrepancy on this dataset.
- **Display formatting.** py4csr prints AGE mean/SD at 1 decimal ("47.0 (14.7)");
  gtsummary's default renders 47.01 (14.71)-style values. Cosmetic, driven by
  py4csr's per-variable `decimal_places` config; raw values are identical.
- ~~**Fisher's exact test** ... not auto-selected~~ **Resolved 2026-09-20:** the
  categorical `auto` test now switches to Fisher's exact when any expected cell
  count < 5 (gtsummary behavior). Not triggered on this dataset (all expected
  counts > 5); covered by unit tests instead.

## 6. Competitive assessment — can this be presented as gtsummary parity?

**Yes, with the fixes applied, for the demographic-table use case.** Every cell a
standard Table 14.1.1 contains — n, mean, SD, median, Q1/Q3, min/max, n (%) by arm
and overall, missing counts, and chi-square p-values — now matches gtsummary's
definitions to 1e-6, and the harness reproduces all 39 published gtsummary numbers
for the same dataset. Before the fixes the claim would not have survived scrutiny:
the quantile definition and the Yates correction produced visibly different numbers
(Q3 off by a year; 2×2 p-value 0.99 vs 0.83), exactly the kind of discrepancy a
reviewer with R open in another window would catch in minutes.

Caveats for outreach messaging:
- ~~The one residual numeric difference is **by design, not error**: ANOVA/t-test vs
  gtsummary's Wilcoxon default for continuous p-values.~~ As of 2026-09-20 the
  defaults match; the tests used are recorded per variable in
  `session.p_value_tests` and printed in the output footnote, so parity claims can
  state the test exactly as gtsummary does.
- This validation covers one 200-row simulated dataset (2 arms; 2/3/4-level
  categoricals; ~5% missing). Broader claims (multi-arm, sparse cells/Fisher,
  stratified percent denominators) need more fixtures — the harness is built to be
  extended.
- The comparison used documented gtsummary output, not a live R run (no R on this
  machine); re-running `compare_gtsummary.py` plus a 5-line R script on any R-equipped
  machine closes that loop.

## Appendix — reproduction

```bash
# from r_open_source/
python -m venv .venv
.venv/Scripts/python -m pip install -e ./py4csr pandas numpy scipy pyreadr pytest
.venv/Scripts/python validation/compare_gtsummary.py   # writes CSV + JSON results
```

Files: `validation/compare_gtsummary.py` (harness), `validation/data/trial.rda` +
`trial.csv` (gtsummary data), `validation/data/adsl_trial.csv` (ADSL-style input),
`validation/comparison_results.csv` (99 cells), `validation/comparison_summary.json`
(match rates), `validation/demographics.rtf` (end-to-end smoke output).
Source of documented anchors: gtsummary `tbl_summary` vignette (cited above).
