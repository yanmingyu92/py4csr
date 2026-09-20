# py4csr ARD Schema v0.1 — Design Document (RFC)

- **Status:** Draft / Request for Comments
- **Schema version:** 0.1 (documents behavior as shipped in py4csr 0.1.1)
- **Date:** 2026-09-20
- **Audience:** statistical programmers, pharmaverse/CAMIS contributors, anyone
  who wants to consume py4csr results programmatically.

This document defines the Analysis Results Dataset (ARD) that
`py4csr.tbl_summary()` produces today, explains the design decisions behind it,
maps it — honestly, including the gaps — to the CDISC Analysis Results
Standard (ARS) and to R `{cards}`, and states what downstream code can rely on.
Sections 7–9 are deliberately written as an RFC: critique is the point.

Everything in §3–§4 was produced by running the code, not by reading it.
Reproduction instructions are in §3.3.

---

## 1. Scope

py4csr is an **ARD-first summary table engine**: the Python counterpart of
`gtsummary::tbl_summary()`. The primary output contract is not a rendered
table but a long/tidy pandas DataFrame — the ARD — from which display tables
(`.to_table()`), RTF/PDF, or external backends (great_tables, rtflite) are
derived.

This document covers **only** the ARD emitted by `py4csr.tbl_summary()`
(`py4csr/summary.py`, a thin wrapper over `ClinicalSession` /
`ClinicalStatisticalEngine` in `py4csr/clinical/`). Inferential analyses
(ANCOVA, survival, logistic) are out of scope for v0.1; the intent is that
their results *enter* tables through this same ARD contract later.

References used throughout:

- CDISC Analysis Results Standard (ARS):
  <https://www.cdisc.org/standards/foundational/analysis-results-standard>
  (logical model repo: <https://github.com/cdisc-org/analysis-results-standard>)
- R `{cards}` (pharmaverse):
  <https://pharmaverse.github.io/cards/> (formerly
  `insightsengineering.github.io/cards`)
- R `{cardx}` (test/model ARDs): <https://insightsengineering.github.io/cardx/>

---

## 2. Terminology

- **ARD** — Analysis Results Dataset: a long/tidy table, one row per computed
  result, holding raw values and their formatted presentations.
- **`tbl_summary()` result** — a `TblSummaryResult` object with:
  - `.ard` — the long DataFrame documented here,
  - `.to_table()` — the wide display table (treatment groups as columns),
  - `.p_values` / `.p_value_tests` — per-variable test metadata (dicts),
  - `.preview()` — convenience head of the display table.

---

## 3. The v0.1 schema, as actually implemented

### 3.1 Column reference

`.ard` is `ClinicalSession.generated_data` exposed unchanged. It has **13
columns**, in this order:

| # | Column | dtype | Semantics |
|---|--------|-------|-----------|
| 1 | `treatment` | str | Analysis group label (treatment arm decode). Includes a `"Total"` pseudo-group when `total=True` (the default). |
| 2 | `variable` | str | Analysis variable name (e.g. `AGE`). |
| 3 | `statistic` | str | Statistic identifier — **see honesty note below**. For continuous variables this is a *display label* (`"N"`, `"Mean (SD)"`, `"Median"`, `"Q1, Q3"`, `"Min, Max"`); for categorical variables it is the *stats-spec token* (`"n_pct"`). |
| 4 | `value` | object | Raw, unrounded result. **Heterogeneous by row**: `int`/`float` for atomic stats (`N`, `Median`), a 2-tuple `(mean, sd)` / `(q1, q3)` / `(min, max)` for compound stats, and `NaN` for categorical rows (whose raw pieces live in columns 11–13). |
| 5 | `formatted_value` | str | Presentation string as it appears in the display table (`"55.6 (9.5)"`, `"23 (50.0%)"`). Never missing. |
| 6 | `variable_id` | int64 | 1-based ordering of `include` variables. |
| 7 | `variable_label` | str | Display label from the `label=` argument (defaults to the variable name). |
| 8 | `variable_type` | str | `"continuous"` or `"categorical"`. |
| 9 | `indent` | int64 | Display indentation level for the wide table (currently always 0 from `tbl_summary()`). A rendering concern that currently lives in the ARD. |
| 10 | `category` | str | Category level for categorical rows (`"F"`, `"M"`, …); `NaN` for continuous rows. |
| 11 | `n` | float64 | Raw count for categorical rows; `NaN` otherwise. Note: the continuous `N` statistic is carried in `value`, **not** here. |
| 12 | `percentage` | float64 | Raw percent (0–100, unrounded) for categorical rows; `NaN` otherwise. |
| 13 | `total_n` | float64 | Denominator (group N after the population filter) for categorical rows; `NaN` otherwise. |

**Honesty notes, because reviewers will find these anyway:**

1. `statistic` conflates machine identifiers and display labels, and its
   granularity differs by variable type. There is no stable `stat_name`
   vocabulary in v0.1 (see §5, rows marked *v0.2 target*).
2. `value` is not atomic: compound statistics are stored as Python tuples.
   `{cards}` stores one scalar per row (`mean` and `sd` are separate rows);
   py4csr v0.1 does not.
3. p-values are **not** ARD rows in v0.1. They live on the result object as
   metadata (§4).
4. `indent` and `variable_id` are presentation/ordering concerns leaking into
   the results layer. They are documented because they exist, not because they
   belong.
5. `treatment` values are the grouping variable's *levels*; the grouping
   variable's *name* (the `by=` argument) is not recorded per row — it is on
   the result object as `TblSummaryResult.by`.

### 3.2 Real example output

Synthetic ADSL (120 subjects, 3 arms, 4 missing AGE values), run with the
project venv against py4csr 0.1.1:

```python
import numpy as np, pandas as pd, py4csr

rng = np.random.default_rng(7)
n = 120
adsl = pd.DataFrame({
    "USUBJID": [f"S{i:03d}" for i in range(n)],
    "TRT01P": rng.choice(["Placebo", "Drug 10mg", "Drug 20mg"], size=n),
    "SAFFL": "Y",
    "AGE": np.round(rng.normal(58, 11, n), 1),
    "SEX": rng.choice(["F", "M"], size=n),
    "RACE": rng.choice(["WHITE", "BLACK OR AFRICAN AMERICAN", "ASIAN"],
                       size=n, p=[0.7, 0.15, 0.15]),
})
adsl.loc[rng.choice(adsl.index, 4, replace=False), "AGE"] = np.nan

tbl = py4csr.tbl_summary(
    data=adsl, by="TRT01P", include=["AGE", "SEX", "RACE"],
    label={"AGE": "Age (years)", "SEX": "Sex, n (%)", "RACE": "Race, n (%)"},
    where="SAFFL == 'Y'",
)
```

`tbl.ard` — shape `(40, 13)`, first rows verbatim:

```
    treatment variable  statistic                                    value formatted_value  variable_id variable_label variable_type  indent category   n  percentage  total_n
0   Drug 10mg      AGE          N                                       44              44            1    Age (years)    continuous       0      NaN NaN         NaN      NaN
1   Drug 10mg      AGE  Mean (SD)  (55.584090909090904, 9.484845763339225)      55.6 (9.5)            1    Age (years)    continuous       0      NaN NaN         NaN      NaN
2   Drug 10mg      AGE     Median                                     55.1            55.1            1    Age (years)    continuous       0      NaN NaN         NaN      NaN
3   Drug 10mg      AGE     Q1, Q3                            (47.95, 62.4)      48.0, 62.4            1    Age (years)    continuous       0      NaN NaN         NaN      NaN
4   Drug 10mg      AGE   Min, Max                             (35.6, 73.9)      35.6, 73.9            1    Age (years)    continuous       0      NaN NaN         NaN      NaN
...
20  Drug 10mg      SEX     n_pct                                      NaN       23 (50.0%)            2      Sex, n (%)   categorical       0        F 23.0    50.000000     46.0
21  Drug 10mg      SEX     n_pct                                      NaN       23 (50.0%)            2      Sex, n (%)   categorical       0        M 23.0    50.000000     46.0
```

(Rows 5–19 are the same five statistics for `Drug 20mg`, `Placebo`, and
`Total`; RACE follows the SEX pattern with three category levels.)

Result-object metadata from the same run:

```python
>>> tbl.p_values
{'Age (years)': '0.738', 'Sex, n (%)': '0.684', 'Race, n (%)': '0.483'}
>>> tbl.p_value_tests
{'Age (years)': 'Kruskal-Wallis test',
 'Sex, n (%)': "Pearson's Chi-squared test",
 'Race, n (%)': "Fisher's exact test"}
```

Note the last entry: with `test="auto"` (the default), the engine *recorded*
that it switched from chi-square to Fisher's exact because an expected cell
count dropped below 5. Which test actually ran is data, and py4csr keeps it.

### 3.3 Reproduction

```bash
cd py4csr/                      # repo root (the package imports from here)
../.venv/Scripts/python         # or your environment's Python
# then run the snippet in §3.2
```

The `statistic` mini-language (`"n mean+sd median q1q3 min+max"`, `"npct"`,
per-variable overrides via `statistic=`) is parsed by
`ClinicalStatisticalEngine._parse_stats_spec` /
`_parse_categorical_stats_spec`; the default test selection follows gtsummary
(Wilcoxon rank-sum / Kruskal–Wallis for continuous; Pearson chi-square with
automatic Fisher's-exact fallback for categorical). A validation harness
comparing this output against `gtsummary::tbl_summary()` cell-by-cell (99/99
parity on the validation dataset) lives in `../validation/`.

---

## 4. Test metadata: `p_values` and `p_value_tests`

v0.1 keeps inferential results **off** the ARD, as two dicts on
`TblSummaryResult`, keyed by *variable label* (not variable name):

- `p_values: dict[str, str]` — variable label → **formatted** p-value string
  (e.g. `"0.738"`, or `"<0.001"`). The raw float is not currently retained on
  the public result object — a known gap, see §8.
- `p_value_tests: dict[str, str]` — variable label → human-readable name of
  the test actually performed, after `auto` resolution and expected-count
  fallback.

Design intent: these are ARD *metadata* in waiting. In the CDISC ARS logical
model, a p-value is a `Result` produced by an `Operation` within an
`AnalysisMethod` attached to an `Analysis`; the test name and its selection
rule are method metadata, and the p-value itself is a result like any other.
In `{cards}` terms, this is what `ard_test_*()` / `{cardx}` produce: rows with
`context = "test"`-style provenance and `stat_name = "p.value"`. v0.1 ships
the dicts as the minimally useful subset of that idea; promoting them to ARD
rows is a v0.2 target (§5, §9).

---

## 5. Mapping: py4csr ARD ↔ CDISC ARS ↔ R {cards}

Legend: ✅ = present and semantically aligned today · 🔶 = present but
partial/renamed · 🎯 = **v0.2 target** (aspirational, not implemented —
do not write code against these).

| py4csr v0.1 | CDISC ARS concept | R {cards} field | Status |
|---|---|---|---|
| `treatment` | `AnalysisGrouping` / group level on a `Result` | `group1_level` | 🔶 Holds the level only; the grouping variable name (`group1`, i.e. `by=`) is on `TblSummaryResult.by`, not per row. |
| — (implied `by=`) | `GroupingFactor` name | `group1` | 🎯 v0.2 target: explicit `group1` column. |
| `variable` | `AnalysisVariable` | `variable` | ✅ |
| `variable_label` | display label of the analysis variable | `variable_label` | ✅ |
| `statistic` | `Operation` / result identifier | `stat_name` + `stat_label` | 🔶 One column doing both jobs, with type-dependent granularity (§3.1 note 1). 🎯 v0.2 target: split into stable `stat_name` (machine vocabulary: `n`, `mean`, `sd`, `median`, `p25`, `p75`, `min`, `max`, `n_pct`, `p.value`) and `stat_label` (display). |
| `value` | `Result` value (`ResultData`) | `stat` | 🔶 Raw value is present, but compound stats are tuples rather than one scalar per row. 🎯 v0.2 target: atomic rows (`mean` and `sd` as separate rows), matching `{cards}` cardinality. |
| `formatted_value` | formatted rendering of a result | `fmt_fun` + formatting applied | 🔶 py4csr stores the formatted *string*; `{cards}` stores the formatting *function* (`fmt_fun`) and defers rendering. Deliberate difference, see §6.3. |
| `variable_type` (+ spec) | derivation context of the operation | `context` | 🎯 v0.2 target: explicit `context` column (`"summary"`, `"test"`, …). Currently derivable only indirectly. |
| `category` | category level of a categorical result | `variable_level` | 🔶 Semantically aligned; name differs. |
| `n`, `percentage`, `total_n` | raw components of a categorical result | (components of `stat` for `n`/`%` rows; denominator via `N`) | 🔶 Present, but as *parallel columns* instead of rows; also empty for continuous stats. 🎯 v0.2 target: fold into atomic `stat` rows; keep or drop the convenience columns based on feedback (§8). |
| `p_values` / `p_value_tests` (result-object dicts) | `AnalysisMethod` + its `Result`s | `ard_test_*()` rows (`stat_name = "p.value"`, test name in `stat_label`/method) | 🎯 v0.2 target: p-value rows in the ARD with the performed-test name carried as row metadata. |
| `TblSummaryResult.by`, `ClinicalSession.uri` | `Output` / `Analysis` identity (`analysis_id`, `table_id`) | (not in `{cards}` core; consumer-side) | 🎯 v0.2/v0.3 target: explicit output/analysis identity columns once multiple outputs can share one ARD. |
| — | `warning` / `error` capture | `warning`, `error` list-columns | 🎯 v0.2 target: per-row warning/error capture (e.g. Fisher fallback, zero-count categories). Currently silent or `print()`ed. |
| `variable_id`, `indent` | — (presentation) | — (presentation) | ⚠️ Documented as present; candidates to move out of the ARD or be ignored by schema validators. Not mapped to ARS/`{cards}` by design. |

**What v0.1 does *not* claim:** conformance to the CDISC ARS logical model.
ARS is a full metadata model (ReportingEvent → Analysis → Method → Operation →
Result, plus traceability to ADaM and SAP). py4csr v0.1 produces a
*result-value table aligned with ARS concepts* — the same layer `{cards}`
occupies — not a serialized ARS metadata instance. No claim is made beyond
that alignment.

---

## 6. Design decisions

### 6.1 Why long/tidy (one row per result)

Because a long table is the only shape that is simultaneously (a) writable by
a statistics engine that doesn't know the final layout, (b) diffable and
QC-able (two ARDs compare with a join, not with a table parser), and (c)
consumable by arbitrary renderers. This is the same conclusion the R ecosystem
reached with `{cards}`/gtsummary's `tbl_ard_summary()` split, and the same
motivation CDISC gives for ARS: results should be machine-readable *before*
they are human-readable. The wide display table is a *pivot* of the ARD, and
py4csr treats it that way (`to_table()` is derivable; `.ard` is primary).

### 6.2 Why raw `value` + `formatted_value` separation

Rounding is a presentation decision; it must not destroy information. If the
ARD stored only `"55.6 (9.5)"`, a downstream consumer (another table layout,
a medical writer pulling a single number into text, a cross-study pooling
script) could never recover `9.48484…`. Keeping the raw value next to the
formatted string means: the engine guarantees the numbers, each renderer
decides the pixels — and a renderer that wants different rounding can take
`value` and reformat. The tuple-valued compound stats (§3.1 note 2) are the
one place v0.1 falls short of its own rule's spirit: the information is raw,
but not atomically addressable. That is scheduled for v0.2.

### 6.3 Why rendering is decoupled (and why `formatted_value` is a string, not a function)

py4csr's output contract is a DataFrame, and DataFrames cross process and
language boundaries badly when they carry closures. `{cards}` can store
`fmt_fun` as a list-column of functions because its ARDs live and die inside
one R session; py4csr wants `.ard` to survive `to_parquet()`, a hand-off to a
non-Python consumer, or a QC diff six months later. So py4csr applies its
formatting eagerly into `formatted_value` and keeps the raw `value` for anyone
who disagrees with the format. The rendering split itself — engine guarantees
numbers and structure, backends (great_tables, rtflite, the legacy in-repo RTF
formatter) guarantee pixels — follows ARCHITECTURE.md §6.

### 6.4 Why the performed test is recorded as metadata

"Chi-square" in a table footnote is a claim about what was computed. With
`test="auto"`, the engine — not the user — chooses the test per variable, and
the choice depends on the data (expected counts < 5 ⇒ Fisher). If that choice
is not captured, the output is not reproducible from its own metadata.
`p_value_tests` is the minimal v0.1 capture; §5 shows where it lands in the
ARS/`{cards}` model once promoted into the ARD.

---

## 7. Non-goals for v0.1

- **ARS logical-model serialization.** No JSON/XML export of ARS metadata
  classes, no `ReportingEvent`/`AnalysisMethod` objects. Alignment of
  concepts only.
- **Atomic statistic rows.** Compound stats stay as tuples in `value` (v0.2).
- **P-values as ARD rows.** They remain result-object dicts (v0.2).
- **Stable `stat_name` vocabulary.** The `statistic` column is what the
  engine emits; treat it as display text (v0.2 adds the machine column).
- **Multi-group ARDs** beyond one `by=` variable (`group2`, `group3`, …),
  overall/unstratified rows as a first-class concept (the `"Total"` arm is a
  string, not a flag), shift tables, hierarchical AE tables.
- **Warning/error capture** in the ARD.
- **Schema validation machinery** (no pandera/pydantic model shipped yet).
- **Backwards compatibility of the wide display table** as a contract —
  `.to_table()` is a rendering; only `.ard` is versioned.

---

## 8. Open questions (RFC — please argue)

1. **Cardinality:** should v0.2 go fully atomic (one scalar per row,
   `{cards}`-style), or is the compound row (`Mean (SD)` as one row) a
   legitimate clinical-reporting idiom worth keeping alongside? Atomic rows
   make pooling trivial; compound rows match how statisticians *talk* about
   these statistics.
2. **`statistic` vocabulary:** adopt `{cards}` names verbatim (`N`, `mean`,
   `sd`, `p25`, `p75`, …) to maximize cross-ecosystem tooling, or a superset
   with py4csr-specific tokens? Divergence has a real cost for anyone writing
   a bilingual QC harness.
3. **Raw p-value retention:** v0.1 exposes only the formatted p-value string.
   Should `p_values` become a DataFrame/rows with the raw float, the formatted
   string, the test name, and the rejection reason for `auto` fallback — or is
   promoting tests into the ARD sufficient and the dicts should be deprecated?
4. **Denominator semantics:** `total_n` is the post-filter group N. For
   non-missing-denominator percentages (gtsummary's `percent = "row"|"cell"`
   analogues), where should the denominator definition live — per row, or as
   table-level metadata?
5. **The `"Total"` pseudo-group:** sentinel string in `treatment` vs. an
   `is_total` flag vs. a separate `context`. The current approach is simplest
   and the most fragile (a treatment genuinely named "Total" collides).
6. **Keys:** what is the natural key of a v0.1 row —
   `(variable, statistic, treatment, category)`? v0.1 does not enforce
   uniqueness; should it?
7. **Parquet interchange:** any objection to declaring
   `value`-must-be-scalar as a v0.2 constraint so the ARD is parquet/Arrow
   native? This forces question 1.
8. **Traceability:** is `where=` + `by=` + spec enough provenance for your
   QC workflows, or do you need dataset fingerprints (hash of input
   ADSL) stamped into the ARD?

---

## 9. Stability guarantees and direction

### What downstream code can rely on in v0.1

- `.ard` is a pandas DataFrame with **exactly the 13 columns of §3.1**, in
  that order, with those dtypes. Columns may be *added* in minor releases;
  none will be removed, renamed, or retyped before v0.2, and v0.2 changes
  will be announced in this document series and the changelog.
- `formatted_value` is always a non-null string; `value` is raw (int / float /
  2-tuple / NaN) exactly as documented per row type.
- `variable_type ∈ {"continuous", "categorical"}`.
- For categorical rows: `n`, `percentage` (0–100 scale, unrounded),
  `total_n`, `category` are populated together.
- `TblSummaryResult.p_values` and `.p_value_tests` exist and are keyed by
  variable label; values are formatted strings and performed-test names.
- `.to_table()` remains available, but its column layout is **not** part of
  the stability contract.

### v0.2 direction (targets, not promises)

- Explicit `group1`/`group1_level` and `context` columns; stable `stat_name`
  vocabulary split from `stat_label`.
- Atomic statistic rows (resolving §8 Q1) and scalar-only `value`
  (parquet-native ARD).
- P-values and performed-test names promoted into the ARD; raw p-value floats
  retained; per-row `warning`/`error` capture.
- A shipped schema validator (pandera or plain pandas) so "is this a v0.2
  ARD?" is a function call.

### v0.3 direction

- Output/analysis identity (`analysis_id`/`table_id`) enabling multi-output
  ARDs; ingestion path (`tbl_ard_summary()`-style: render a display table
  *from* an external ARD); exploration of exporting ARS-aligned metadata
  alongside the result table; shift and hierarchical (AE) table contexts.

---

*Comments, corrections, and dissent: open an issue or discussion on the py4csr
repository. The fastest way to change this schema is to show a workflow it
breaks.*
