"""
Table Builder for Functional Clinical Reporting

This module provides table construction functionality that mirrors the SAS RRG
approach to building clinical tables from statistical components.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from ..analysis.utils import format_pvalue
from .config import FunctionalConfig, TableTemplate
from .statistical_templates import StatisticalTemplates


class TableResult:
    """Result object from table building process."""

    def __init__(self, data: pd.DataFrame, metadata: Dict[str, Any]):
        self.data = data
        self.metadata = metadata
        self.title = metadata.get("title", "")
        self.subtitle = metadata.get("subtitle", "")
        self.footnotes = metadata.get("footnotes", [])

    def __repr__(self):
        return f"TableResult(shape={self.data.shape}, title='{self.title[:50]}...')"


class TableBuilder:
    """
    Table builder class (equivalent to SAS RRG table generation process).

    This class takes table specifications and builds formatted tables using
    the statistical templates, similar to how SAS RRG generates tables from
    macro specifications.
    """

    def __init__(self, session, table_spec: Dict[str, Any]):
        """
        Initialize table builder.

        Parameters
        ----------
        session : ReportSession
            Parent report session containing data and configuration
        table_spec : dict
            Table specification dictionary
        """
        self.session = session
        self.spec = table_spec
        self.config = session.config
        self.templates = session.templates

    def build(self) -> TableResult:
        """
        Build table according to specification.

        Returns
        -------
        TableResult
            Built table with metadata
        """
        table_type = self.spec["type"]

        # Get table template
        template = self.config.get_template(table_type)
        if not template:
            raise ValueError(f"No template found for table type: {table_type}")

        # Route to appropriate builder method
        if table_type == "demographics":
            return self._build_demographics_table(template)
        elif table_type == "disposition":
            return self._build_disposition_table(template)
        elif table_type == "ae_summary":
            return self._build_ae_summary_table(template)
        elif table_type == "ae_detail":
            return self._build_ae_detail_table(template)
        elif table_type == "laboratory":
            return self._build_laboratory_table(template)
        elif table_type == "efficacy":
            return self._build_efficacy_table(template)
        elif table_type == "vital_signs":
            return self._build_vital_signs_table(template)
        elif table_type == "survival":
            return self._build_survival_table(template)
        else:
            raise ValueError(f"Unsupported table type: {table_type}")

    def _build_demographics_table(self, template: TableTemplate) -> TableResult:
        """Build demographics table (equivalent to SAS RRG demographics template)."""

        # Get ADSL data
        if "ADSL" not in self.session.datasets:
            raise ValueError("ADSL dataset required for demographics table")

        adsl = self._get_filtered_data("ADSL")
        treatment_var = self.session.treatments["variable"]

        # Use template variables or specification variables
        variables = self.spec.get("variables") or template.default_variables

        # Build table sections
        table_sections = []

        for variable in variables:
            if variable not in adsl.columns:
                print(f"Warning: Variable '{variable}' not found in ADSL, skipping")
                continue

            # Determine variable type
            var_type = self._determine_variable_type(adsl[variable])

            if var_type == "continuous":
                stats_df = self.templates.calculate_continuous_statistics(
                    adsl,
                    variable,
                    treatment_var,
                    statistics=["n", "mean_sd", "median", "min_max"],
                )
            else:
                stats_df = self.templates.calculate_categorical_statistics(
                    adsl, variable, treatment_var, statistics=["n_percent"]
                )

            # Add variable label
            stats_df["VARIABLE_LABEL"] = self._get_variable_label(variable)
            table_sections.append(stats_df)

        # Combine all sections
        if table_sections:
            combined_data = pd.concat(table_sections, ignore_index=True)
        else:
            combined_data = pd.DataFrame()

        # Format for display
        display_table = self._format_demographics_display(
            combined_data,
            treatment_var,
            tests=self.spec.get("tests", []),
            source_df=adsl,
        )

        # Create metadata
        metadata = {
            "title": self.spec.get("title", template.title_template),
            "subtitle": self._format_subtitle(template.subtitle_template),
            "footnotes": self.spec.get("footnotes", template.footnotes),
            "population": self.spec.get("population", "safety"),
            "table_type": "demographics",
        }

        return TableResult(display_table, metadata)

    def _build_disposition_table(self, template: TableTemplate) -> TableResult:
        """Build disposition table."""

        if "ADSL" not in self.session.datasets:
            raise ValueError("ADSL dataset required for disposition table")

        adsl = self._get_filtered_data("ADSL")
        treatment_var = self.session.treatments["variable"]

        # Use disposition reason variable
        disp_var = "DCSREAS" if "DCSREAS" in adsl.columns else "DCREASCD"

        if disp_var not in adsl.columns:
            raise ValueError(f"Disposition variable not found in ADSL")

        # Calculate disposition statistics
        stats_df = self.templates.calculate_categorical_statistics(
            adsl, disp_var, treatment_var, statistics=["n_percent"]
        )

        # Format for display
        display_table = self._format_disposition_display(stats_df, treatment_var)

        metadata = {
            "title": self.spec.get("title", template.title_template),
            "subtitle": self._format_subtitle(template.subtitle_template),
            "footnotes": self.spec.get("footnotes", template.footnotes),
            "population": "randomized",
            "table_type": "disposition",
        }

        return TableResult(display_table, metadata)

    def _build_ae_summary_table(self, template: TableTemplate) -> TableResult:
        """Build AE summary table."""

        if "ADAE" not in self.session.datasets:
            raise ValueError("ADAE dataset required for AE summary table")

        adae = self._get_filtered_data("ADAE")
        treatment_var = self.session.treatments["variable"]

        # Calculate AE summary statistics
        ae_stats = self.templates.calculate_ae_statistics(adae, treatment_var)

        # Create summary categories
        summary_stats = self._create_ae_summary_categories(adae, treatment_var)

        # Format for display
        display_table = self._format_ae_summary_display(summary_stats, treatment_var)

        metadata = {
            "title": self.spec.get("title", template.title_template),
            "subtitle": self._format_subtitle(template.subtitle_template),
            "footnotes": self.spec.get("footnotes", template.footnotes),
            "population": self.spec.get("population", "safety"),
            "table_type": "ae_summary",
        }

        return TableResult(display_table, metadata)

    def _build_ae_detail_table(self, template: TableTemplate) -> TableResult:
        """Build detailed AE table by SOC and PT."""

        if "ADAE" not in self.session.datasets:
            raise ValueError("ADAE dataset required for AE detail table")

        adae = self._get_filtered_data("ADAE")
        treatment_var = self.session.treatments["variable"]

        # Calculate detailed AE statistics
        ae_stats = self.templates.calculate_ae_statistics(adae, treatment_var)

        # Format for display
        display_table = self._format_ae_detail_display(ae_stats, treatment_var)

        metadata = {
            "title": self.spec.get("title", template.title_template),
            "subtitle": self._format_subtitle(template.subtitle_template),
            "footnotes": self.spec.get("footnotes", template.footnotes),
            "population": self.spec.get("population", "safety"),
            "table_type": "ae_detail",
        }

        return TableResult(display_table, metadata)

    def _build_laboratory_table(self, template: TableTemplate) -> TableResult:
        """Build laboratory parameters table."""

        if "ADLB" not in self.session.datasets:
            raise ValueError("ADLB dataset required for laboratory table")

        adlb = self._get_filtered_data("ADLB")
        treatment_var = self.session.treatments["variable"]

        # Get laboratory parameters
        lab_params = adlb["PARAMCD"].unique() if "PARAMCD" in adlb.columns else []

        table_sections = []

        for param in lab_params:
            param_data = adlb[adlb["PARAMCD"] == param]

            # Use change from baseline if available
            value_var = "CHG" if "CHG" in param_data.columns else "AVAL"

            if value_var in param_data.columns:
                stats_df = self.templates.calculate_continuous_statistics(
                    param_data,
                    value_var,
                    treatment_var,
                    statistics=["n", "mean_sd", "median", "min_max"],
                )
                stats_df["PARAMETER"] = param
                table_sections.append(stats_df)

        # Combine all parameters
        if table_sections:
            combined_data = pd.concat(table_sections, ignore_index=True)
        else:
            combined_data = pd.DataFrame()

        # Format for display
        display_table = self._format_laboratory_display(combined_data, treatment_var)

        metadata = {
            "title": self.spec.get("title", template.title_template),
            "subtitle": self._format_subtitle(template.subtitle_template),
            "footnotes": self.spec.get("footnotes", template.footnotes),
            "population": self.spec.get("population", "safety"),
            "table_type": "laboratory",
        }

        return TableResult(display_table, metadata)

    def _build_efficacy_table(self, template: TableTemplate) -> TableResult:
        """Build efficacy analysis table."""

        # This is a placeholder - actual efficacy tables would depend on study design
        # For now, create a simple efficacy summary

        if "ADSL" not in self.session.datasets:
            raise ValueError("ADSL dataset required for efficacy table")

        adsl = self._get_filtered_data("ADSL")
        treatment_var = self.session.treatments["variable"]

        # Simple efficacy placeholder
        display_table = pd.DataFrame(
            {
                "Parameter": ["Primary Endpoint Analysis"],
                "Statistic": ["To be implemented"],
                **{trt: ["--"] for trt in sorted(adsl[treatment_var].unique())},
                "Total": ["--"],
            }
        )

        metadata = {
            "title": self.spec.get("title", template.title_template),
            "subtitle": self._format_subtitle(template.subtitle_template),
            "footnotes": self.spec.get("footnotes", template.footnotes),
            "population": self.spec.get("population", "efficacy"),
            "table_type": "efficacy",
        }

        return TableResult(display_table, metadata)

    def _build_vital_signs_table(self, template: TableTemplate) -> TableResult:
        """Build vital signs table."""

        if "ADVS" not in self.session.datasets:
            raise ValueError("ADVS dataset required for vital signs table")

        advs = self._get_filtered_data("ADVS")
        treatment_var = self.session.treatments["variable"]

        # Get vital signs parameters
        vs_params = advs["PARAMCD"].unique() if "PARAMCD" in advs.columns else []

        table_sections = []

        for param in vs_params:
            param_data = advs[advs["PARAMCD"] == param]

            # Use change from baseline if available
            value_var = "CHG" if "CHG" in param_data.columns else "AVAL"

            if value_var in param_data.columns:
                stats_df = self.templates.calculate_continuous_statistics(
                    param_data,
                    value_var,
                    treatment_var,
                    statistics=["n", "mean_sd", "median", "min_max"],
                )
                stats_df["PARAMETER"] = param
                table_sections.append(stats_df)

        # Combine all parameters
        if table_sections:
            combined_data = pd.concat(table_sections, ignore_index=True)
        else:
            combined_data = pd.DataFrame()

        # Format for display
        display_table = self._format_vital_signs_display(combined_data, treatment_var)

        metadata = {
            "title": self.spec.get("title", template.title_template),
            "subtitle": self._format_subtitle(template.subtitle_template),
            "footnotes": self.spec.get("footnotes", template.footnotes),
            "population": self.spec.get("population", "safety"),
            "table_type": "vital_signs",
        }

        return TableResult(display_table, metadata)

    def _build_survival_table(self, template: TableTemplate) -> TableResult:
        """Build survival analysis table (Kaplan-Meier medians and log-rank p-value)."""
        # Require ADTTE
        if "ADTTE" not in self.session.datasets:
            raise ValueError("ADTTE dataset required for survival table")

        adtte = self._get_filtered_data("ADTTE")
        treatment_var = self.session.treatments["variable"]

        # Resolve duration and event columns (allow overrides in spec)
        duration_col = self.spec.get("duration_col") or (
            "AVAL" if "AVAL" in adtte.columns else None
        )
        if duration_col is None:
            raise ValueError(
                "Duration column not found; provide duration_col in spec or include AVAL in ADTTE"
            )

        # Derive event indicator: prefer EVENT(1/0), else derive from CNSR (1=censor -> event=1-CNSR), else EVNTFL (Y/N)
        event_col = None
        derived_event = None
        if "EVENT" in adtte.columns:
            event_col = "EVENT"
        elif "CNSR" in adtte.columns:
            derived_event = 1 - adtte["CNSR"].astype(int)
        elif "EVNTFL" in adtte.columns:
            derived_event = adtte["EVNTFL"].astype(str).str.upper().eq("Y").astype(int)
        else:
            # Fallback: treat non-missing duration as censored (no events)
            derived_event = (adtte[duration_col].notna() & False).astype(int)

        # Prepare display rows
        rows: List[Dict[str, Any]] = []
        treatments = sorted(adtte[treatment_var].dropna().unique())

        # Compute median survival per treatment (KM if lifelines available; else naive median among events)
        logrank_p = None
        try:
            from lifelines import KaplanMeierFitter
            from lifelines.statistics import logrank_test

            lifelines_ok = True
        except Exception:
            lifelines_ok = False

        medians_by_trt: Dict[Any, float] = {}
        for trt in treatments:
            g = adtte[adtte[treatment_var] == trt]
            durations = g[duration_col]
            events = g[event_col] if event_col else derived_event.loc[g.index]
            if lifelines_ok:
                try:
                    kmf = KaplanMeierFitter()
                    kmf.fit(durations, events)
                    med = float(kmf.median_survival_time_)
                except Exception:
                    med = (
                        float(durations[events == 1].median())
                        if (events == 1).any()
                        else float("nan")
                    )
            else:
                med = (
                    float(durations[events == 1].median())
                    if (events == 1).any()
                    else float("nan")
                )
            medians_by_trt[trt] = med

        # Build median survival row
        row = {"Parameter": "Median survival"}
        for trt in treatments:
            val = medians_by_trt.get(trt)
            row[trt] = f"{val:.2f}" if val == val else "N/A"  # check NaN
        # Total column as blank for medians
        row["Total"] = ""
        rows.append(row)

        # Log-rank p-value if exactly two groups
        if len(treatments) == 2:
            g1 = adtte[adtte[treatment_var] == treatments[0]]
            g2 = adtte[adtte[treatment_var] == treatments[1]]
            d1 = g1[duration_col]
            d2 = g2[duration_col]
            e1 = g1[event_col] if event_col else derived_event.loc[g1.index]
            e2 = g2[event_col] if event_col else derived_event.loc[g2.index]
            try:
                if lifelines_ok:
                    res = logrank_test(d1, d2, e1, e2)
                    logrank_p = float(res.p_value)
                else:
                    logrank_p = None
            except Exception:
                logrank_p = None

        # Append p-value row
        p_row = {"Parameter": "P-value (log-rank)"}
        for trt in treatments:
            p_row[trt] = ""
        p_row["Total"] = format_pvalue(logrank_p) if (logrank_p is not None) else "N/A"
        rows.append(p_row)

        display_table = pd.DataFrame(rows)

        metadata = {
            "title": self.spec.get("title", template.title_template),
            "subtitle": self._format_subtitle(template.subtitle_template),
            "footnotes": self.spec.get("footnotes", template.footnotes),
            "population": self.spec.get("population", "safety"),
            "table_type": "survival",
        }

        return TableResult(display_table, metadata)

    def _get_filtered_data(self, dataset_name: str) -> pd.DataFrame:
        """Get filtered dataset based on population and filters."""

        if dataset_name not in self.session.datasets:
            raise ValueError(f"Dataset '{dataset_name}' not found")

        data = self.session.datasets[dataset_name]["data"].copy()

        # Apply population filter
        population = self.spec.get("population", "safety")
        if population in self.session.populations:
            pop_filter = self.session.populations[population]
            try:
                data = data.query(pop_filter)
            except Exception as e:
                print(f"Warning: Failed to apply population filter '{pop_filter}': {e}")

        # Apply additional filters
        filters = self.spec.get("filters", {})
        for filter_name, filter_expr in filters.items():
            try:
                data = data.query(filter_expr)
            except Exception as e:
                print(f"Warning: Failed to apply filter '{filter_name}': {e}")

        return data

    def _determine_variable_type(self, series: pd.Series) -> str:
        """Determine if variable is continuous or categorical."""

        # Check if numeric
        if pd.api.types.is_numeric_dtype(series):
            # Check number of unique values
            unique_count = series.nunique()
            total_count = len(series.dropna())

            # If less than 10 unique values or less than 5% unique, treat as categorical
            if unique_count < 10 or (unique_count / total_count) < 0.05:
                return "categorical"
            else:
                return "continuous"
        else:
            return "categorical"

    def _get_variable_label(self, variable: str) -> str:
        """Get variable label from dataset metadata or use variable name."""

        # Try to get from ADSL metadata
        if "ADSL" in self.session.datasets:
            adsl_attrs = getattr(self.session.datasets["ADSL"]["data"], "attrs", {})
            var_labels = adsl_attrs.get("variable_labels", {})
            if variable in var_labels:
                return var_labels[variable]

        # Default labels for common variables
        default_labels = {
            "AGE": "Age (years)",
            "AGEGR1": "Age Group",
            "SEX": "Sex",
            "RACE": "Race",
            "WEIGHT": "Weight (kg)",
            "HEIGHT": "Height (cm)",
            "BMI": "BMI (kg/m²)",
            "DCSREAS": "Primary Reason for Discontinuation",
        }

        return default_labels.get(variable, variable)

    def _format_subtitle(self, subtitle_template: str) -> str:
        """Format subtitle template with session metadata."""

        replacements = {
            "study_title": self.session.metadata.get("title", "Clinical Study"),
            "population_label": self._get_population_label(),
        }

        formatted = subtitle_template
        for key, value in replacements.items():
            formatted = formatted.replace(f"{{{key}}}", str(value))

        return formatted

    def _get_population_label(self) -> str:
        """Get population label for subtitle."""

        population = self.spec.get("population", "safety")

        labels = {
            "safety": "Safety Analysis Population",
            "efficacy": "Efficacy Analysis Population",
            "itt": "Intent-to-Treat Population",
            "randomized": "All Randomized Subjects",
        }

        return labels.get(population, f"{population.title()} Population")

    def _format_demographics_display(
        self,
        stats_df: pd.DataFrame,
        treatment_var: str,
        tests: Optional[List[str]] = None,
        source_df: Optional[pd.DataFrame] = None,
    ) -> pd.DataFrame:
        """Format demographics statistics for display.
        If tests are requested, append a P-value row per variable (ANOVA for continuous,
        Chi-square for categorical) with the value placed in the Total column.
        """

        if stats_df.empty:
            return pd.DataFrame()

        tests_upper = set([t.upper() for t in (tests or [])])
        want_anova = "TEST[ANOVA]" in tests_upper
        want_chi2 = (
            "TEST[CHI_SQUARE]" in tests_upper or "TEST[CHI-SQUARE]" in tests_upper
        )

        # Get treatment levels
        treatments = sorted(stats_df["TREATMENT"].unique())
        treatments = [t for t in treatments if t != "Total"] + ["Total"]

        display_rows: List[Dict[str, Any]] = []

        for variable in stats_df["VARIABLE"].unique():
            var_data = stats_df[stats_df["VARIABLE"] == variable]
            var_label = (
                var_data["VARIABLE_LABEL"].iloc[0]
                if "VARIABLE_LABEL" in var_data.columns
                else variable
            )

            is_categorical = "CATEGORY" in var_data.columns

            if is_categorical:
                # Categorical variable
                for category in sorted(var_data["CATEGORY"].unique()):
                    cat_data = var_data[var_data["CATEGORY"] == category]
                    row = {"Parameter": f"  {category}"}
                    for treatment in treatments:
                        trt_data = cat_data[cat_data["TREATMENT"] == treatment]
                        row[treatment] = (
                            trt_data["FORMATTED_VALUE"].iloc[0]
                            if not trt_data.empty
                            else "0 (0.0%)"
                        )
                    display_rows.append(row)

                # Append p-value row if requested
                if want_chi2 and source_df is not None:
                    try:
                        import pandas as _pd
                        from scipy import stats as _sps  # type: ignore

                        if (
                            variable in source_df.columns
                            and treatment_var in source_df.columns
                        ):
                            ct = _pd.crosstab(
                                source_df[variable], source_df[treatment_var]
                            )
                            pval_str = ""
                            if ct.shape[0] >= 2 and ct.shape[1] >= 2:
                                _chi2, p, _dof, _exp = _sps.chi2_contingency(ct)
                                pval_str = format_pvalue(float(p))
                            row = {"Parameter": f"P-value ({var_label})"}
                            for t in treatments:
                                row[t] = ""
                            row["Total"] = pval_str or "N/A"
                            display_rows.append(row)
                    except Exception:
                        row = {"Parameter": f"P-value ({var_label})"}
                        for t in treatments:
                            row[t] = ""
                        row["Total"] = "N/A"
                        display_rows.append(row)
            else:
                # Continuous variable - group by statistic
                for statistic in var_data["STATISTIC"].unique():
                    stat_data = var_data[var_data["STATISTIC"] == statistic]
                    row = {"Parameter": f"{var_label} - {statistic}"}
                    for treatment in treatments:
                        trt_data = stat_data[stat_data["TREATMENT"] == treatment]
                        row[treatment] = (
                            trt_data["FORMATTED_VALUE"].iloc[0]
                            if not trt_data.empty
                            else ""
                        )
                    display_rows.append(row)

                # Append p-value row if requested
                if want_anova and source_df is not None:
                    try:
                        from scipy import stats as _sps  # type: ignore

                        groups = [
                            g[variable].dropna().values
                            for _, g in source_df.groupby(treatment_var)
                        ]
                        valid = [arr for arr in groups if len(arr) > 0]
                        if len(valid) >= 2:
                            _stat, p = _sps.f_oneway(*valid)
                            pval_str = format_pvalue(float(p))
                        else:
                            pval_str = "N/A"
                        row = {"Parameter": f"{var_label} - P-value"}
                        for t in treatments:
                            row[t] = ""
                        row["Total"] = pval_str
                        display_rows.append(row)
                    except Exception:
                        row = {"Parameter": f"{var_label} - P-value"}
                        for t in treatments:
                            row[t] = ""
                        row["Total"] = "N/A"
                        display_rows.append(row)

        return pd.DataFrame(display_rows)

    def _format_disposition_display(
        self, stats_df: pd.DataFrame, treatment_var: str
    ) -> pd.DataFrame:
        """Format disposition statistics for display."""

        if stats_df.empty:
            return pd.DataFrame()

        treatments = sorted(stats_df["TREATMENT"].unique())
        treatments = [t for t in treatments if t != "Total"] + ["Total"]

        display_rows = []

        for category in sorted(stats_df["CATEGORY"].unique()):
            cat_data = stats_df[stats_df["CATEGORY"] == category]

            row = {"Disposition": category}
            for treatment in treatments:
                trt_data = cat_data[cat_data["TREATMENT"] == treatment]
                if not trt_data.empty:
                    row[treatment] = trt_data["FORMATTED_VALUE"].iloc[0]
                else:
                    row[treatment] = "0 (0.0%)"

            display_rows.append(row)

        return pd.DataFrame(display_rows)

    def _create_ae_summary_categories(
        self, adae: pd.DataFrame, treatment_var: str
    ) -> pd.DataFrame:
        """Create AE summary categories."""

        subject_var = "USUBJID" if "USUBJID" in adae.columns else "SUBJID"

        # Get denominators from ADSL
        if "ADSL" in self.session.datasets:
            adsl = self._get_filtered_data("ADSL")
            denominators = adsl.groupby(treatment_var).size().to_dict()
        else:
            denominators = adae.groupby(treatment_var)[subject_var].nunique().to_dict()

        results = []
        treatments = sorted(adae[treatment_var].unique())

        # Summary categories
        categories = [
            ("Any adverse event", adae),
            (
                "Any serious adverse event",
                (
                    adae[adae.get("AESER", "N") == "Y"]
                    if "AESER" in adae.columns
                    else pd.DataFrame()
                ),
            ),
            (
                "Any severe adverse event",
                (
                    adae[adae.get("AESEV", "") == "SEVERE"]
                    if "AESEV" in adae.columns
                    else pd.DataFrame()
                ),
            ),
            (
                "Any drug-related adverse event",
                (
                    adae[
                        adae.get("AEREL", "").isin(["RELATED", "PROBABLE", "POSSIBLE"])
                    ]
                    if "AEREL" in adae.columns
                    else pd.DataFrame()
                ),
            ),
        ]

        for category_name, category_data in categories:
            if category_data.empty:
                continue

            for treatment in treatments:
                trt_data = category_data[category_data[treatment_var] == treatment]
                subject_count = (
                    trt_data[subject_var].nunique() if not trt_data.empty else 0
                )
                denominator = denominators.get(treatment, 1)
                percentage = (
                    (subject_count / denominator * 100) if denominator > 0 else 0
                )

                results.append(
                    {
                        "CATEGORY": category_name,
                        "TREATMENT": treatment,
                        "SUBJECT_COUNT": subject_count,
                        "PERCENTAGE": percentage,
                        "FORMATTED_VALUE": f"{subject_count} ({percentage:.1f}%)",
                    }
                )

        return pd.DataFrame(results)

    def _format_ae_summary_display(
        self, stats_df: pd.DataFrame, treatment_var: str
    ) -> pd.DataFrame:
        """Format AE summary for display."""

        if stats_df.empty:
            return pd.DataFrame()

        treatments = sorted(stats_df["TREATMENT"].unique())

        display_rows = []

        for category in stats_df["CATEGORY"].unique():
            cat_data = stats_df[stats_df["CATEGORY"] == category]

            row = {"Adverse Event Category": category}
            for treatment in treatments:
                trt_data = cat_data[cat_data["TREATMENT"] == treatment]
                if not trt_data.empty:
                    row[treatment] = trt_data["FORMATTED_VALUE"].iloc[0]
                else:
                    row[treatment] = "0 (0.0%)"

            display_rows.append(row)

        return pd.DataFrame(display_rows)

    def _format_ae_detail_display(
        self, ae_stats: pd.DataFrame, treatment_var: str
    ) -> pd.DataFrame:
        """Format detailed AE statistics for display."""

        if ae_stats.empty:
            return pd.DataFrame()

        treatments = sorted(ae_stats["TREATMENT"].unique())

        display_rows = []

        # Group by SOC, then PT
        for soc in sorted(ae_stats[ae_stats["LEVEL"] == "SOC"]["TERM"].unique()):
            # Add SOC header
            soc_data = ae_stats[
                (ae_stats["LEVEL"] == "SOC") & (ae_stats["TERM"] == soc)
            ]

            soc_row = {"System Organ Class / Preferred Term": soc}
            for treatment in treatments:
                trt_data = soc_data[soc_data["TREATMENT"] == treatment]
                if not trt_data.empty:
                    soc_row[treatment] = trt_data["FORMATTED_VALUE"].iloc[0]
                else:
                    soc_row[treatment] = "0 (0.0%)"

            display_rows.append(soc_row)

            # Add PTs under this SOC
            pt_data = ae_stats[
                (ae_stats["LEVEL"] == "PT") & (ae_stats["PARENT_TERM"] == soc)
            ]

            for pt in sorted(pt_data["TERM"].unique()):
                pt_row_data = pt_data[pt_data["TERM"] == pt]

                pt_row = {"System Organ Class / Preferred Term": f"  {pt}"}
                for treatment in treatments:
                    trt_data = pt_row_data[pt_row_data["TREATMENT"] == treatment]
                    if not trt_data.empty:
                        pt_row[treatment] = trt_data["FORMATTED_VALUE"].iloc[0]
                    else:
                        pt_row[treatment] = "0 (0.0%)"

                display_rows.append(pt_row)

        return pd.DataFrame(display_rows)

    def _format_laboratory_display(
        self, stats_df: pd.DataFrame, treatment_var: str
    ) -> pd.DataFrame:
        """Format laboratory statistics for display."""

        if stats_df.empty:
            return pd.DataFrame()

        treatments = sorted(stats_df["TREATMENT"].unique())
        treatments = [t for t in treatments if t != "Total"] + ["Total"]

        display_rows = []

        for parameter in stats_df["PARAMETER"].unique():
            param_data = stats_df[stats_df["PARAMETER"] == parameter]

            for statistic in param_data["STATISTIC"].unique():
                stat_data = param_data[param_data["STATISTIC"] == statistic]

                row = {"Parameter": f"{parameter} - {statistic}"}
                for treatment in treatments:
                    trt_data = stat_data[stat_data["TREATMENT"] == treatment]
                    if not trt_data.empty:
                        row[treatment] = trt_data["FORMATTED_VALUE"].iloc[0]
                    else:
                        row[treatment] = ""

                display_rows.append(row)

        return pd.DataFrame(display_rows)

    def _format_vital_signs_display(
        self, stats_df: pd.DataFrame, treatment_var: str
    ) -> pd.DataFrame:
        """Format vital signs statistics for display."""

        # Same format as laboratory
        return self._format_laboratory_display(stats_df, treatment_var)
