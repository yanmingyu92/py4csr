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
    Result returned by :func:`tbl_summary`.

    Args:
        session: Generated clinical analysis session. Use :func:`tbl_summary`
            to create a result for normal application code.
        by: Name of the variable used to group the table columns.

    Attributes:
        by: Name of the variable used to group the table columns.
        ard: Long-format Analysis Results Dataset (ARD), with one row per
            variable, statistic or category, and treatment result.
        p_values: Mapping from variable labels to formatted p-value strings.
        p_value_tests: Mapping from variable labels to the test names used.

    Examples:
        >>> from contextlib import redirect_stdout
        >>> from io import StringIO
        >>> import pandas as pd
        >>> import py4csr
        >>> data = pd.DataFrame({"TRT": ["A", "A", "B", "B"],
        ...                      "AGE": [42, 50, 45, 53]})
        >>> with redirect_stdout(StringIO()):
        ...     result = py4csr.tbl_summary(data, by="TRT", include=["AGE"])
        >>> result.by
        'TRT'
    """

    def __init__(self, session: ClinicalSession, by: str):
        """Initialize the result wrapper around a generated session.

        Args:
            session: Generated clinical analysis session that owns the result
                data and display table.
            by: Name of the grouping variable used for the table columns.
        """
        self._session = session
        self.by = by
        self.ard = session.generated_data
        self.p_values = session.p_values
        self.p_value_tests = session.p_value_tests

    def to_table(self) -> pd.DataFrame:
        """Return the wide display table with treatment groups as columns.

        Returns:
            pandas.DataFrame: The generated table.

        Examples:
            >>> from contextlib import redirect_stdout
            >>> from io import StringIO
            >>> import pandas as pd
            >>> import py4csr
            >>> data = pd.DataFrame({"TRT": ["A", "A", "B", "B"],
            ...                      "AGE": [42, 50, 45, 53]})
            >>> with redirect_stdout(StringIO()):
            ...     result = py4csr.tbl_summary(data, by="TRT", include=["AGE"])
            >>> table = result.to_table()
            >>> "A" in table.columns
            True
        """
        return self._session.generated_table

    def preview(self, max_rows: int = 20) -> pd.DataFrame:
        """Return the first rows of the display table.

        Args:
            max_rows: Maximum number of rows to return. Defaults to 20.

        Returns:
            pandas.DataFrame: The requested leading rows.

        Examples:
            >>> from contextlib import redirect_stdout
            >>> from io import StringIO
            >>> import pandas as pd
            >>> import py4csr
            >>> data = pd.DataFrame({"TRT": ["A", "A", "B", "B"],
            ...                      "AGE": [42, 50, 45, 53]})
            >>> with redirect_stdout(StringIO()):
            ...     result = py4csr.tbl_summary(data, by="TRT", include=["AGE"])
            >>> with redirect_stdout(StringIO()):
            ...     preview = result.preview(max_rows=5)
        """
        return self._session.preview(max_rows=max_rows)

    def __repr__(self):
        """Return a concise representation of the result.

        Returns:
            str: The result type, grouping variable, and table shape, or its
                not-generated state.

        Examples:
            >>> from contextlib import redirect_stdout
            >>> from io import StringIO
            >>> import pandas as pd
            >>> import py4csr
            >>> data = pd.DataFrame({"TRT": ["A", "A", "B", "B"],
            ...                      "AGE": [42, 50, 45, 53]})
            >>> with redirect_stdout(StringIO()):
            ...     result = py4csr.tbl_summary(data, by="TRT", include=["AGE"])
            >>> repr(result).startswith("TblSummaryResult(by='TRT'")
            True
        """
        table = self._session.generated_table
        if table is None:
            return "TblSummaryResult(<not generated>)"
        return (
            f"TblSummaryResult(by={self.by!r}, shape={table.shape})\n"
            + table.to_string(index=False)
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
    """Build a treatment-group summary table.

    Numeric variables are treated as continuous. Other variables are treated
    as categorical unless ``type`` overrides their classification.

    Args:
        data: Input dataset as a pandas DataFrame.
        by: Column that defines the treatment or grouping columns.
        include: Non-empty list of columns to summarize.
        statistic: Optional per-variable statistic specifications. Continuous
            variables default to ``"n mean+sd median q1q3 min+max"`` and
            categorical variables default to ``"npct"``.
        label: Optional per-variable display labels.
        where: Optional pandas query expression that selects the analysis
            population. An empty string includes every row.
        total: Whether to include the Total column. Defaults to True.
        type: Optional per-variable type override. Values must be
            ``"continuous"`` or ``"categorical"``.
        test: Optional test name for all variables or a per-variable mapping.
            When omitted, the engine selects tests automatically. Valid names
            are the same as those accepted by ``ClinicalSession.add_var`` and
            ``ClinicalSession.add_catvar``.

    Returns:
        TblSummaryResult: Result with the long-format ``ard``, wide display
        table, and selected p-value tests.

    Raises:
        TypeError: If ``data`` is not a pandas DataFrame.
        ValueError: If ``by`` or an included column is missing, ``include``
            is empty, or a type override is invalid.

    Examples:
        >>> from contextlib import redirect_stdout
        >>> from io import StringIO
        >>> import pandas as pd
        >>> import py4csr
        >>> data = pd.DataFrame({
        ...     "SUBJID": ["S001", "S002", "S003", "S004"],
        ...     "TRT": ["A", "A", "B", "B"],
        ...     "AGE": [42, 50, 45, 53],
        ... })
        >>> with redirect_stdout(StringIO()):
        ...     result = py4csr.tbl_summary(
        ...         data, by="TRT", include=["AGE"], test="ttest"
        ...     )
        >>> table = result.to_table()
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError(
            "data must be a pandas DataFrame, got " + data.__class__.__name__
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
    test_spec = (
        test if isinstance(test, dict) else ({v: test for v in include} if test else {})
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
