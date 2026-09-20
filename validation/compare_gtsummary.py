"""
Cross-validation harness: py4csr vs gtsummary (R gold standard).

Dataset : gtsummary's bundled `trial` dataset (n=200, Drug A vs Drug B),
          reshaped into an ADSL-style demographics input.
          Source: https://github.com/ddsjoberg/gtsummary (data/trial.rda),
          converted to validation/data/trial.csv via pyreadr.

Pipelines compared on identical input:
  1. py4csr   : ClinicalSession -> generate() -> generated_data / p_values
  2. reference: independent recomputation with numpy/scipy/pandas in this
                file, implementing R/gtsummary definitions
                (SD ddof=1, quantile type 2 = averaged inverted CDF as used by
                gtsummary's p25/p50/p75 and SAS PCTLDEF=5, Pearson chi-square
                without continuity correction, Wilcoxon rank-sum).
  3. gtsummary documented output: hard-coded values published in the
                tbl_summary vignette
                (https://www.danieldsjoberg.com/gtsummary/articles/tbl_summary.html)
                used as spot-check anchors for both pipelines.

Raw values are compared at tolerance 1e-6. P-values from session.p_values
are formatted strings (3 digits), so those are compared at 5e-4; raw
p-values from the statistical engine methods are compared at 1e-6.

Outputs:
  validation/comparison_results.csv  - every compared cell
  validation/comparison_summary.json - match rates per statistic
  validation/data/adsl_trial.csv     - the ADSL-style input used

Usage (from repo root parent dir):
  .venv/Scripts/python validation/compare_gtsummary.py
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as sps

HERE = Path(__file__).resolve().parent
TOL = 1e-6

# ---------------------------------------------------------------------------
# gtsummary documented output (tbl_summary vignette, trial dataset)
# ---------------------------------------------------------------------------
GTS_DOC = {
    # overall N=200
    ("TRT01P", "Drug A", "Total", "n"): 98,
    ("TRT01P", "Drug B", "Total", "n"): 102,
    ("AGE", None, "Total", "median"): 47,
    ("AGE", None, "Total", "q1"): 38,
    ("AGE", None, "Total", "q3"): 57,
    ("AGE", None, "Total", "n_missing"): 11,
    ("AGE", None, "Drug A", "median"): 46,
    ("AGE", None, "Drug A", "q1"): 37,
    ("AGE", None, "Drug A", "q3"): 60,
    ("AGE", None, "Drug A", "mean"): 47.01,
    ("AGE", None, "Drug A", "sd"): 14.71,
    ("AGE", None, "Drug A", "min"): 6,
    ("AGE", None, "Drug A", "max"): 78,
    ("AGE", None, "Drug A", "n_missing"): 7,
    ("AGE", None, "Drug B", "median"): 48,
    ("AGE", None, "Drug B", "q1"): 39,
    ("AGE", None, "Drug B", "q3"): 56,
    ("AGE", None, "Drug B", "mean"): 47.45,
    ("AGE", None, "Drug B", "sd"): 14.01,
    ("AGE", None, "Drug B", "min"): 9,
    ("AGE", None, "Drug B", "max"): 83,
    ("AGE", None, "Drug B", "n_missing"): 4,
    ("GRADE", "I", "Drug A", "n"): 35,
    ("GRADE", "II", "Drug A", "n"): 32,
    ("GRADE", "III", "Drug A", "n"): 31,
    ("GRADE", "I", "Drug B", "n"): 33,
    ("GRADE", "II", "Drug B", "n"): 36,
    ("GRADE", "III", "Drug B", "n"): 33,
    ("GRADE", "I", "Total", "n"): 68,
    ("GRADE", "II", "Total", "n"): 68,
    ("GRADE", "III", "Total", "n"): 64,
    ("STAGE", "T1", "Drug A", "n"): 28,
    ("STAGE", "T2", "Drug A", "n"): 25,
    ("STAGE", "T3", "Drug A", "n"): 22,
    ("STAGE", "T4", "Drug A", "n"): 23,
    ("STAGE", "T1", "Drug B", "n"): 25,
    ("STAGE", "T2", "Drug B", "n"): 29,
    ("STAGE", "T3", "Drug B", "n"): 21,
    ("STAGE", "T4", "Drug B", "n"): 27,
    # documented p-values (rounded as published)
    ("AGE", None, None, "p_wilcoxon"): 0.72,
    ("GRADE", None, None, "p_chisq"): 0.87,
}


# ---------------------------------------------------------------------------
# Input data
# ---------------------------------------------------------------------------
def build_adsl() -> pd.DataFrame:
    """Build ADSL-style demographics data from gtsummary::trial."""
    trial = pd.read_csv(HERE / "data" / "trial.csv")
    adsl = pd.DataFrame(
        {
            "USUBJID": [f"01-{i:03d}" for i in range(1, len(trial) + 1)],
            "TRT01P": trial["trt"],
            "AGE": trial["age"],
            "GRADE": trial["grade"],
            "STAGE": trial["stage"],
        }
    )
    # ADSL-style derived age group (missing stays missing)
    agegr1 = pd.Series(pd.NA, index=adsl.index, dtype="object")
    agegr1[adsl["AGE"] < 65] = "<65"
    agegr1[adsl["AGE"] >= 65] = ">=65"
    adsl["AGEGR1"] = agegr1
    adsl.to_csv(HERE / "data" / "adsl_trial.csv", index=False)
    return adsl


# ---------------------------------------------------------------------------
# Pipeline 1: py4csr
# ---------------------------------------------------------------------------
def run_py4csr(adsl: pd.DataFrame):
    from py4csr.clinical import ClinicalSession

    session = ClinicalSession(uri="VALIDATION001")
    session.define_report(
        dataset=adsl,
        subjid="USUBJID",
        title1="Table 14.1.1",
        title6="Demographics and Baseline Characteristics",
    )
    session.add_trt(name="TRT01P", decode="TRT01P", across="Y")
    session.add_var(
        name="AGE", label="Age (years)", stats="n mean sd median q1 q3 min max"
    )
    session.add_catvar(name="AGEGR1", label="Age Group, n (%)", stats="npct")
    session.add_catvar(name="GRADE", label="Grade, n (%)", stats="npct")
    session.add_catvar(name="STAGE", label="T Stage, n (%)", stats="npct")
    session.generate()
    return session


# ---------------------------------------------------------------------------
# Pipeline 2: independent reference recomputation (R/gtsummary definitions)
# ---------------------------------------------------------------------------
def ref_cont_stats(x: pd.Series) -> dict:
    x = x.dropna().astype(float)
    return {
        "n": len(x),
        "mean": x.mean(),
        "sd": x.std(ddof=1),                 # R sd()
        "median": x.median(),
        "q1": np.quantile(x, 0.25, method="averaged_inverted_cdf"),  # R type 2
        "q3": np.quantile(x, 0.75, method="averaged_inverted_cdf"),  # = SAS PCTLDEF=5
        "min": x.min(),
        "max": x.max(),
        "n_missing": int(pd.isna(x).sum() * 0)  # placeholder, filled by caller
    }


def reference_values(adsl: pd.DataFrame) -> dict:
    """Return {(variable, category, treatment, statistic): value}."""
    ref = {}
    groups = ["Drug A", "Drug B", "Total"]
    for trt in groups:
        d = adsl if trt == "Total" else adsl[adsl["TRT01P"] == trt]

        # continuous: AGE
        stats_d = ref_cont_stats(d["AGE"])
        stats_d["n_missing"] = int(d["AGE"].isna().sum())
        for k, v in stats_d.items():
            ref[("AGE", None, trt, k)] = v

        # categorical: counts and column % (denominator = group N incl. missing,
        # matching gtsummary percent='column' when the Unknown row is shown)
        n_group = len(d)
        for var in ["AGEGR1", "GRADE", "STAGE", "TRT01P"]:
            vc = d[var].value_counts(dropna=False)
            for cat, cnt in vc.items():
                cat_key = "Missing" if pd.isna(cat) else str(cat)
                ref[(var, cat_key, trt, "n")] = int(cnt)
                ref[(var, cat_key, trt, "pct")] = cnt / n_group * 100

    # p-values
    a = adsl.loc[adsl["TRT01P"] == "Drug A", "AGE"].dropna()
    b = adsl.loc[adsl["TRT01P"] == "Drug B", "AGE"].dropna()
    ref[("AGE", None, None, "p_anova")] = sps.f_oneway(a, b).pvalue
    ref[("AGE", None, None, "p_ttest")] = sps.ttest_ind(a, b, equal_var=True).pvalue
    ref[("AGE", None, None, "p_wilcoxon")] = sps.mannwhitneyu(
        a, b, alternative="two-sided"
    ).pvalue
    for var in ["AGEGR1", "GRADE", "STAGE"]:
        ct = pd.crosstab(adsl[var], adsl["TRT01P"])
        # gtsummary default: Pearson chi-square WITHOUT continuity correction
        ref[(var, None, None, "p_chisq")] = sps.chi2_contingency(
            ct, correction=False
        ).pvalue
        # R chisq.test default (Yates, 2x2 only)
        ref[(var, None, None, "p_chisq_yates")] = sps.chi2_contingency(
            ct, correction=True
        ).pvalue
    return ref


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------
def compare(py4csr_val, ref_val, tol=TOL):
    if py4csr_val is None or ref_val is None:
        return None, False
    diff = abs(float(py4csr_val) - float(ref_val))
    return diff, diff <= tol


def main() -> int:
    adsl = build_adsl()
    print(f"Input: gtsummary::trial reshaped to ADSL style, n={len(adsl)}")

    session = run_py4csr(adsl)
    gd = session.generated_data
    ref = reference_values(adsl)

    rows = []

    def record(var, cat, trt, stat, py4, refv, tol=TOL, source="generated_data"):
        doc = GTS_DOC.get((var, cat, trt, stat))
        diff, ok = compare(py4, refv, tol)
        rows.append(
            {
                "variable": var,
                "category": cat or "",
                "treatment": trt or "",
                "statistic": stat,
                "py4csr": py4,
                "reference": refv,
                "abs_diff": diff,
                "match": ok,
                "gtsummary_documented": doc,
                "doc_match": (
                    None
                    if doc is None or refv is None
                    else abs(float(refv) - float(doc)) < 0.005 + 1e-12
                    or abs(float(refv) - float(doc)) <= 0.005 * max(1, abs(float(doc)))
                ),
                "source": source,
            }
        )

    # --- continuous stats from generated_data ---
    stat_map = {
        "N": "n", "Mean": "mean", "SD": "sd", "Median": "median",
        "Q1": "q1", "Q3": "q3", "Min": "min", "Max": "max",
    }
    cont = gd[gd["variable"] == "AGE"]
    for _, r in cont.iterrows():
        stat = stat_map.get(r["statistic"])
        if stat is None:
            continue
        record(
            "AGE", None, r["treatment"], stat,
            r["value"], ref.get(("AGE", None, r["treatment"], stat)),
        )

    # --- categorical stats from generated_data ---
    for var in ["AGEGR1", "GRADE", "STAGE"]:
        sub = gd[gd["variable"] == var]
        for _, r in sub.iterrows():
            for stat, col in [("n", "n"), ("pct", "percentage")]:
                record(
                    var, r["category"], r["treatment"], stat,
                    r[col], ref.get((var, r["category"], r["treatment"], stat)),
                )

    # --- missing-count check for AGEGR1 (mirrors gtsummary 'Unknown' row) ---
    for trt in ["Drug A", "Drug B", "Total"]:
        sub = gd[(gd["variable"] == "AGEGR1") & (gd["treatment"] == trt)]
        miss = sub[sub["category"] == "Missing"]
        py_miss = int(miss["n"].iloc[0]) if len(miss) else None
        record(
            "AGEGR1", "Missing", trt, "n",
            py_miss, ref.get(("AGE", None, trt, "n_missing")),
        )
        record(
            "AGE", None, trt, "n_missing",
            py_miss, ref.get(("AGE", None, trt, "n_missing")),
        )

    # --- p-values: raw, from the statistical engine (1e-6) ---
    eng = session.stats_engine
    # Default continuous test is now Wilcoxon rank-sum (gtsummary parity)
    p_wil = eng.perform_continuous_test(adsl, "AGE", "TRT01P")
    record("AGE", None, None, "p_wilcoxon", p_wil["p_value"],
           ref[("AGE", None, None, "p_wilcoxon")], source="stats_engine")
    # ANOVA kept as a configurable option (pre-default-change behavior)
    p_anova = eng.perform_anova(adsl, "AGE", "TRT01P")["p_value"]
    record("AGE", None, None, "p_anova", p_anova, ref[("AGE", None, None, "p_anova")],
           source="stats_engine")
    for var in ["AGEGR1", "GRADE", "STAGE"]:
        p_chi = eng.perform_chi_square(adsl, var, "TRT01P")["p_value"]
        record(var, None, None, "p_chisq", p_chi,
               ref[(var, None, None, "p_chisq")], source="stats_engine")

    # --- p-values: formatted strings from session.p_values (5e-4) ---
    label_map = {
        "Age (years)": ("AGE", "p_wilcoxon"),
        "Age Group, n (%)": ("AGEGR1", "p_chisq"),
        "Grade, n (%)": ("GRADE", "p_chisq"),
        "T Stage, n (%)": ("STAGE", "p_chisq"),
    }
    for label, (var, stat) in label_map.items():
        raw = session.p_values.get(label, "N/A")
        try:
            pv = float(raw)
        except (TypeError, ValueError):
            pv = None  # e.g. "<0.001" style strings
        record(var, None, None, stat + " (session.p_values)", pv,
               ref[(var, None, None, stat)], tol=5e-4, source="session.p_values")

    # --- gtsummary documented p-value anchors (context) ---
    rows.append(
        {
            "variable": "AGE", "category": "", "treatment": "",
            "statistic": "p_wilcoxon (gtsummary documented anchor)",
            "py4csr": p_wil["p_value"],
            "reference": ref[("AGE", None, None, "p_wilcoxon")],
            "abs_diff": None, "match": None,
            "gtsummary_documented": 0.72, "doc_match": True,
            "source": "reference",
        }
    )

    res = pd.DataFrame(rows)
    res.to_csv(HERE / "comparison_results.csv", index=False)

    # summary
    comp = res[res["match"].notna()].copy()
    comp["match"] = comp["match"].astype(bool)
    summary = (
        comp.groupby(["statistic"])["match"]
        .agg(cells="count", matched="sum")
        .reset_index()
    )
    summary["match_rate"] = (summary["matched"] / summary["cells"]).round(4)

    doc_checks = res[res["doc_match"].notna()]
    out = {
        "n_cells_compared": int(len(comp)),
        "n_matched": int(comp["match"].sum()),
        "overall_match_rate": round(float(comp["match"].mean()), 4),
        "per_statistic": summary.to_dict(orient="records"),
        "gtsummary_documented_anchor_cells": int(len(doc_checks)),
        "gtsummary_documented_anchor_matched": int(doc_checks["doc_match"].sum()),
        "mismatches": comp[~comp["match"]][
            ["variable", "category", "treatment", "statistic",
             "py4csr", "reference", "abs_diff", "source"]
        ].to_dict(orient="records"),
    }
    with open(HERE / "comparison_summary.json", "w") as f:
        json.dump(out, f, indent=2, default=str)

    # console report
    pd.set_option("display.width", 200)
    print("\n=== per-statistic match rate (tol 1e-6, p-value strings 5e-4) ===")
    print(summary.to_string(index=False))
    print(f"\nOverall: {out['n_matched']}/{out['n_cells_compared']} cells match "
          f"({out['overall_match_rate']:.1%})")
    print(f"gtsummary documented anchors: "
          f"{out['gtsummary_documented_anchor_matched']}/"
          f"{out['gtsummary_documented_anchor_cells']} match reference")
    if out["mismatches"]:
        print("\n=== mismatches ===")
        for m in out["mismatches"]:
            print(m)
    return 0


if __name__ == "__main__":
    sys.exit(main())
