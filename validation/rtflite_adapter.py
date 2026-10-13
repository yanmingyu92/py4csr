"""
rtflite_adapter.py — experimental adapter: render py4csr tbl_summary output via rtflite.

Maps a ``py4csr.tbl_summary()`` result (display table from ``.to_table()`` plus
metadata from ``.ard`` / ``.p_values`` / ``.p_value_tests``) onto rtflite
components (RTFPage / RTFTitle / RTFColumnHeader / RTFBody / RTFFootnote /
RTFSource) and writes a clinical-style RTF table.

Experiment only — lives in validation/, no py4csr source is modified.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import rtflite as rtf

_INDENT_TWIPS = 240  # 1/6 inch hanging indent for stat/category rows


def _row_structure(result) -> list[dict]:
    """Reconstruct per-display-row metadata from the ARD.

    Returns one dict per row of ``result.to_table()`` with keys
    ``kind`` ("label" | "stat" | "category") and ``variable_label``.
    Falls back to all-label rows if the ARD shape does not match the
    display table.
    """
    tab = result.to_table()
    ard = result.ard
    rows: list[dict] = []
    try:
        for _, vdf in ard.groupby("variable_id", sort=True):
            vtype = vdf["variable_type"].iloc[0]
            vlabel = vdf["variable_label"].iloc[0]
            n_rows = vdf[vdf["treatment"] == vdf["treatment"].iloc[0]].shape[0]
            if vtype == "continuous":
                # display merges the label with the first stat row (usually N)
                rows.append({"kind": "label", "variable_label": vlabel})
                rows += [
                    {"kind": "stat", "variable_label": vlabel}
                    for _ in range(n_rows - 1)
                ]
            else:  # categorical: standalone label row, then one row per category
                rows.append({"kind": "label", "variable_label": vlabel})
                rows += [
                    {"kind": "category", "variable_label": vlabel}
                    for _ in range(n_rows)
                ]
        if len(rows) != len(tab):
            raise ValueError("row count mismatch")
    except Exception:
        rows = [{"kind": "label", "variable_label": None} for _ in tab]
    return rows


def _group_ns(result) -> dict[str, int] | None:
    """Per-treatment group N, taken from categorical ARD rows (total_n)."""
    ard = result.ard
    if "total_n" not in ard.columns:
        return None
    ns = (
        ard.dropna(subset=["total_n"])
        .groupby("treatment")["total_n"]
        .first()
        .astype(int)
        .to_dict()
    )
    return ns or None


def _methodology_footnote(result) -> str | None:
    """Auto footnote from the tests actually used (gtsummary-style)."""
    tests = getattr(result, "p_value_tests", None) or {}
    if not tests:
        return None
    parts = [f"{label} by {test}" for label, test in tests.items()]
    return "P-values from: " + "; ".join(parts) + "."


def render_rtf(
    tbl_summary_result,
    path,
    title=("Table 14.1.1", "Demographics and Baseline Characteristics"),
    footnote: str | list[str] | None = None,
    source: str | None = None,
    add_pvalue: bool = True,
    orientation: str = "landscape",
) -> Path:
    """Render a py4csr ``tbl_summary`` result to a clinical-style RTF table.

    Parameters
    ----------
    tbl_summary_result : py4csr.TblSummaryResult
    path : str or Path
        Output ``.rtf`` file.
    title : str or tuple/list of str
        Title line(s), e.g. ``("Table 14.1.1", "Demographics ...")``.
    footnote : str or list of str, optional
        Extra footnote line(s); the methodology footnote derived from
        ``.p_value_tests`` is always prepended when tests were run.
    source : str, optional
        Source line (e.g. dataset / program attribution).
    add_pvalue : bool
        Append a P-value column (values from ``.p_values``, shown on the
        variable-label row).
    orientation : {"landscape", "portrait"}
    """
    path = Path(path)
    tab = tbl_summary_result.to_table().copy()
    structure = _row_structure(tbl_summary_result)

    # --- optional p-value column -------------------------------------------
    pvals = getattr(tbl_summary_result, "p_values", {}) or {}
    if add_pvalue and pvals:
        col = []
        for row in structure:
            if row["kind"] == "label" and row["variable_label"] in pvals:
                col.append(pvals[row["variable_label"]])
            else:
                col.append("")
        tab["P-value"] = col

    n_cols = tab.shape[1]

    # --- column headers ------------------------------------------------------
    ns = _group_ns(tbl_summary_result)
    header_text = []
    for c in tab.columns:
        if ns and c in ns:
            header_text.append(f"{c}\\line (N={ns[c]})")
        else:
            header_text.append(c)

    # relative widths: stub column gets 3, data columns 1.5, p-value 1
    rel = [3.0] + [1.5] * (n_cols - 1)
    if add_pvalue and pvals:
        rel[-1] = 1.0

    trt_span = sum(rel[1 : (n_cols if not (add_pvalue and pvals) else n_cols - 1)])
    spanner = ["", "Treatment Group"] + ([""] if add_pvalue and pvals else [])
    spanner_rel = [rel[0], trt_span] + ([rel[-1]] if add_pvalue and pvals else [])
    column_header = [
        rtf.RTFColumnHeader(
            text=spanner,
            col_rel_width=spanner_rel,
            text_justification=["l", "c"] + (["c"] if add_pvalue and pvals else []),
            text_format="b",
            border_bottom=["", "single"] + ([""] if add_pvalue and pvals else []),
        ),
        rtf.RTFColumnHeader(
            text=header_text,
            col_rel_width=rel,
            text_justification=["l"] + ["c"] * (n_cols - 1),
            text_format="b",
        ),
    ]

    # --- body: per-cell indentation + bold variable-label rows ---------------
    indent = [
        [0 if row["kind"] == "label" else _INDENT_TWIPS] + [0] * (n_cols - 1)
        for row in structure
    ]
    fmt = [
        ["b" if row["kind"] == "label" else ""] * n_cols for row in structure
    ]
    body = rtf.RTFBody(
        col_rel_width=rel,
        text_justification=["l"] + ["c"] * (n_cols - 1),
        text_indent_left=indent,
        text_format=fmt,
    )

    # --- title / footnote / source ------------------------------------------
    title_lines = [title] if isinstance(title, str) else list(title)
    rtf_title = rtf.RTFTitle(text=title_lines, text_format=["b"] + [""] * (len(title_lines) - 1))

    foot_lines: list[str] = []
    meth = _methodology_footnote(tbl_summary_result)
    if meth:
        foot_lines.append(meth)
    if footnote:
        foot_lines += [footnote] if isinstance(footnote, str) else list(footnote)
    # text_convert=False: default conversion treats "_" as subscript markup,
    # which corrupts filenames / program names (e.g. "adsl_trial.csv").
    rtf_footnote = (
        rtf.RTFFootnote(text=foot_lines, text_convert=False) if foot_lines else None
    )

    rtf_source = rtf.RTFSource(text=source, text_convert=False) if source else None

    # rtflite 2.6.0's DataFrame validation (narwhals to_native) rejects the
    # installed pandas version; polars DataFrames validate cleanly. Build the
    # polars frame from plain Python lists to avoid the pyarrow dependency.
    import polars as pl

    tab_pl = pl.DataFrame(tab.fillna("").astype(str).to_dict(orient="list"))

    doc = rtf.RTFDocument(
        df=tab_pl,
        rtf_page=rtf.RTFPage(orientation=orientation),
        rtf_page_footer=rtf.RTFPageFooter(text="Confidential — py4csr/rtflite prototype"),
        rtf_title=rtf_title,
        rtf_column_header=column_header,
        rtf_body=body,
        rtf_footnote=rtf_footnote,
        rtf_source=rtf_source,
    )
    doc.write_rtf(str(path))
    return path


if __name__ == "__main__":
    from py4csr import tbl_summary

    root = Path(__file__).resolve().parent
    adsl = pd.read_csv(root / "data" / "adsl_trial.csv")

    result = tbl_summary(
        adsl,
        by="TRT01P",
        include=["AGE", "GRADE"],
        label={"AGE": "Age (years)", "GRADE": "Tumor Grade, n (%)"},
        test={"AGE": "anova", "GRADE": "chisq"},
    )
    out = render_rtf(
        result,
        root / "rtflite_demographics.rtf",
        title=("Table 14.1.1", "Demographics and Baseline Characteristics",
               "Full Analysis Set"),
        footnote="Percentages are based on the number of subjects in each treatment group.",
        source="Source: validation/data/adsl_trial.csv | Program: rtflite_adapter.py",
    )
    print(f"Wrote {out}")
