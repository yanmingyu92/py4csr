# py4csr → rtflite integration notes

Experiment: render a `py4csr.tbl_summary()` result (ADSL demographics table:
AGE continuous + GRADE categorical, by TRT01P, with p-values) as a
clinical-style RTF through rtflite 2.6.0.

- Adapter: `validation/rtflite_adapter.py` (`render_rtf(result, path, title, footnote, source)`)
- Output: `validation/rtflite_demographics.rtf`
- Data: `validation/data/adsl_trial.csv` (200 subjects, Drug A / Drug B)
- Environment: Windows, Python 3.13, pandas 3.0.6, polars 1.44.2, narwhals 2.26.0

**Verdict: the end-to-end pipeline works.** The display table from
`.to_table()`, group Ns from `.ard`, and the methodology footnote from
`.p_value_tests` all map onto rtflite components, and the output passes a
structural check (balanced groups, `\paperw15840\paperh12240\landscape`,
12 `\trowd` rows) and round-trips through an independent RTF parser
(`striprtf`) with every value, header, footnote, and source line intact.
No LibreOffice on this machine, so no PDF render check was done.

## What mapped cleanly

- **Core layout model.** `RTFDocument(df=..., rtf_page/rtf_title/
  rtf_column_header/rtf_body/rtf_footnote/rtf_source)` is a genuinely good
  fit for an external table engine: we hand over a display-shaped DataFrame
  and decorate it. No impedance mismatch.
- **Page setup.** `RTFPage(orientation="landscape")` auto-swaps width/height
  and adjusts usable column width (verified: `\paperw15840\paperh12240
  \landscape`, col_width 8.5"). Zero manual twip math.
- **Multi-row headers.** A list of `RTFColumnHeader(df=...)` renders a
  "Treatment Group" spanner row over per-group `Drug A\line (N=98)` columns.
  `\line` line breaks inside header cells work as documented.
- **`col_rel_width`.** Behaves exactly as specified (ratios, matched between
  header rows and body); the wide-stub / narrow-data-column clinical layout
  is trivial.
- **Per-cell formatting.** 2D broadcast of `text_indent_left` (twips) and
  `text_format` gives indented stat/category rows and bold variable-label
  rows — the standard demographics-table hierarchy display. Verified
  `\li240` on exactly the 7 sub-rows.
- **Footnote/source lines, page footer.** `RTFFootnote(text=[...])`,
  `RTFSource`, `RTFPageFooter` all work first try; the auto-generated
  methodology footnote from `p_value_tests` ("P-values from: Age (years) by
  One-way ANOVA; ...") drops straight in.

## Friction points (worked around, but awkward)

1. **pandas 3.x DataFrame rejected at validation.** `RTFDocument(df=<pandas
   DataFrame>)` with pandas 3.0.6 raises
   `ValidationError: DataFrame must be a valid DataFrame: DataFrame.to_native()
   takes 1 positional argument but 2 were given` (narwhals interop).
   Workaround: convert to polars first — and `pl.from_pandas` itself needs
   pyarrow for object columns, so we build `pl.DataFrame(df.astype(str)
   .to_dict("list"))`. For a package whose users are largely pandas-based
   table engines, this is the first thing that bites. Suggestion: pin/CI
   against pandas 3.x, and/or accept anything narwhals can wrap by passing
   the frame straight to `nw.from_native` without the pre-validation path
   that calls `to_native`.
2. **`text_convert=True` default corrupts clinical text.** Underscores are
   treated as LaTeX subscript markup, so the source line
   `adsl_trial.csv | Program: rtflite_adapter.py` rendered as
   `adsl{\sub trial.csv}`. Filenames, variable names, and program paths full
   of underscores are the norm in this domain. Expected: literal text unless
   I opt in. Suggestion: default `text_convert=False` for
   `RTFFootnote`/`RTFSource` (or globally), keeping opt-in conversion for
   titles/body where math symbols are wanted.
3. **Spanner headers require manual width arithmetic.** The "Treatment
   Group" spanner needs the caller to sum the spanned columns'
   `col_rel_width` values by hand and keep three width lists (spanner row,
   label row, body) in sync — error-prone when a column is added
   (e.g. our optional P-value column changes the arithmetic in three
   places). Suggestion: a per-cell span parameter, e.g.
   `RTFColumnHeader(text=["", "Treatment Group"], col_span=[1, 3])`, with
   widths derived from the body.

## Missing features for a standard clinical demographics table

1. **Cell spanning (`col_span`/`row_span`).** Expected: declare that a
   header cell spans N columns. Actual: only manual `col_rel_width`
   replication across header rows (above). Minimal API:
   `RTFColumnHeader(text=[...], col_span=[1, 3, 1])`.
2. **Footnote-symbol machinery.** Standard CSR tables annotate cells with
   superscript symbols/letters (`a`, `b`, `†`) tied to footnote lines.
   Expected: e.g. `RTFFootnote(text=..., symbols=["a","b"])` plus a way to
   attach `{\super a}` to given body cells. Actual: nothing — the caller
   must hand-inject raw RTF super scripts into cell text and keep symbols
   and footnotes consistent manually.
3. **Row-level hierarchy declaration for the stub column.** py4csr's ARD
   carries an explicit `indent`/variable-label structure; we had to
   re-derive per-row indentation and rebuild 2D `text_indent_left` /
   `text_format` broadcast matrices by hand. `subline_by`/`group_by` exist
   on `RTFBody` but group on data values, not on a display hierarchy.
   Suggestion: accept a per-row indent vector for the stub column, e.g.
   `RTFBody(stub_indent=[0,1,1,1,0,1,1])`, or a `stub_column` +
   `indent_by` pair.
4. **Orphan control at page breaks.** A variable-label row can land as the
   last row of a page with its stat rows on the next. Expected: a
   keep-with-next / keep-block-together hint (r2rtf doesn't have this
   either, but Word supports `\keepn`). Suggestion: `RTFBody(keep_with_next=[...])`
   or automatic keeping of `group_by` blocks.
5. **Page-number helper.** `RTFPageHeader` defaults to r2rtf-style
   `\chpgn`/`NUMPAGES` field codes, which is fine, but any custom header
   text must re-embed raw field codes by hand. Suggestion: a
   `page_number=True/«format»` option independent of `text`.

## Notes for the maintainer question

"Can rtflite serve as the RTF backend for an external table engine?" — yes.
The component model (page/title/header/body/footnote/source), broadcast
attribute system, and landscape/letter handling are all backend-friendly;
the only integration-layer work was (a) polars conversion, (b)
`text_convert=False` on provenance lines, and (c) width arithmetic for
spanner headers. The gap list above is what stands between "works" and
"drop-in for regulated CSR output", and items 1–3 are all small, additive
API surface.
