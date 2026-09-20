"""
Top-level gtsummary-style convenience interface for py4csr.

This module implements the ARCHITECTURE.md section 6 sketch minimally over the
existing table engine (`ClinicalSession` / `ClinicalStatisticalEngine`): a
single `tbl_summary()` call builds a by-treatment summary table and returns a
result object exposing the long-format analysis results dataset (ARD) and a
wide display table.
"""

from typing import Dict, List, Optional, Union

import pandas as pd

from .clinical import ClinicalSession

# Default statistic specs (existing add_var / add_catvar mini-language)
DEFAULT_CONT_STATS = "n mean+sd median q1q3 min+max"
DEFAULT_CAT_STATS = "npct"


class TblSummaryResult:
    """
    Result of :func:`tbl_summary`.

    Attributes
    ----------
    ard : pd.DataFrame
        Long-format Analysis Results Dataset: one row per
        (variable, statistic/category, treatment) result, with raw ``value``
        and ``formatted_value`` columns.
    p_values : dict
        Variable label -> formatted p-value string.
    p_value_tests : dict
        Variable label -> name of the statistical test actually used.
    """

    def __init__(self, session: ClinicalSession, by: str):
        self._session = session
        self.by = by
        self.ard = session.generated_data
        self.p_values = session.p_values
        self.p_value_tests = session.p_value_tests

    def to_table(self) -> pd.DataFrame:
        """Return the wide display table (treatment groups across columns)."""
        return self._session.generated_table

    def preview(self, max_rows: int = 20) -> pd.DataFrame:
        """Return the first ``max_rows`` rows of the display table."""
        return self._session.preview(max_rows=max_rows)

    def __repr__(self):
        table = self._session.generated_table
        if table is None:
            return "TblSummaryResult(<not generated>)"
        return f"TblSummaryResult(by={self.by!r}, shape={table.shape})\n" + table.to_string(
            index=False
        )


def tbl_summary(
    data: pd.DataFrame,
    by: str,
    include: List[str],
    statistic: Union[Dict[str, str], None] = None,
    label: Union[Dict[str, str], None] = None,
    where: str = "",
    total: bool = True,
    type: Union[Dict[str, str], None] = None,
    test: Union[Dict[str, str], str, None] = None,
) -> TblSummaryResult:
    """
    Build a by-treatment summary table (gtsummary-style convenience API).

    Thin wrapper over the existing table engine; see ARCHITECTURE.md §6.

    Parameters
    ----------
    data : pd.DataFrame
        Input dataset (e.g. ADSL)
    by : str
        Treatment/grouping variable (columns of the table)
    include : list of str
        Variables to summarize. Numeric variables are summarized as
        continuous, others as categorical; override per variable with
        ``type={"VAR": "continuous"}`` / ``"categorical"``.
    statistic : dict, optional
        Per-variable stats spec using the existing mini-language, e.g.
        ``{"AGE": "n mean+sd median q1q3 min+max", "SEX": "npct"}``.
        Defaults: ``"n mean+sd median q1q3 min+max"`` (continuous),
        ``"npct"`` (categorical).
    label : dict, optional
        Per-variable display labels.
    where : str, optional
        Population filter, pandas query syntax (e.g. ``"SAFFL == 'Y'"``).
    total : bool
        Keep the Total column (default True).
    type : dict, optional
        Per-variable type override: "continuous" or "categorical".
    test : str or dict, optional
        Statistical test selection: a single test name applied to all
        variables, or a per-variable dict. Defaults ("auto") follow
        gtsummary: Wilcoxon rank-sum / Kruskal-Wallis for continuous,
        Pearson chi-square (Fisher's exact when any expected count < 5)
        for categorical. See ``add_var``/``add_catvar`` for valid names.

    Returns
    -------
    TblSummaryResult
        Object with ``.ard`` (long results DataFrame), ``.to_table()``
        (wide display table), ``.preview()``, ``.p_values`` and
        ``.p_value_tests``.

    Examples
    --------
    >>> import py4csr
    >>> tbl = py4csr.tbl_summary(
    ...     data=adsl, by="TRT01P", include=["AGE", "SEX"],
    ...     label={"AGE": "Age (years)", "SEX": "Sex, n (%)"},
    ...     where="SAFFL == 'Y'",
    ... )
    >>> tbl.ard          # long-format results
    >>> tbl.to_table()   # wide display table
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError(
            "data must be a pandas DataFrame, got "
            + data.__class__.__name__
        )
    if by not in data.columns:
        raise ValueError(f"Grouping variable '{by}' not found in data")
    if not include:
        raise ValueError("include must name at least one variable")
    missing = [v for v in include if v not in data.columns]
    if missing:
        raise ValueError(f"Variable(s) not found in data: {', '.join(missing)}")

    statistic = statistic or {}
    label = label or {}
    type = type or {}
    test_spec = test if isinstance(test, dict) else (
        {v: test for v in include} if test else {}
    )

    session = ClinicalSession(uri="tbl_summary")
    session.define_report(
        dataset=data,
        pop_where=where if where else "1==1",
        subjid="USUBJID" if "USUBJID" in data.columns else "SUBJID",
    )
    session.add_trt(name=by, decode=by)

    for var in include:
        var_type = type.get(var)
        if var_type is None:
            var_type = (
                "continuous"
                if pd.api.types.is_numeric_dtype(data[var])
                else "categorical"
            )
        var_test = test_spec.get(var, "auto")
        if var_type == "continuous":
            session.add_var(
                name=var,
                label=label.get(var, var),
                stats=statistic.get(var, DEFAULT_CONT_STATS),
                test=var_test,
            )
        elif var_type == "categorical":
            session.add_catvar(
                name=var,
                label=label.get(var, var),
                stats=statistic.get(var, DEFAULT_CAT_STATS),
                test=var_test,
            )
        else:
            raise ValueError(
                f"type for variable '{var}' must be 'continuous' or "
                f"'categorical', got {var_type!r}"
            )

    session.generate()

    if not total and session.generated_data is not None:
        session.generated_data = session.generated_data[
            session.generated_data["treatment"].astype(str) != "Total"
        ].reset_index(drop=True)
        session.generated_table = session.generated_table.drop(
            columns=["Total"], errors="ignore"
        )

    return TblSummaryResult(session, by)
