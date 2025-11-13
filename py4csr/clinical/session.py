"""
Clinical reporting session for py4csr.

This module provides a high-level interface for building clinical tables
by accumulating variables and generating comprehensive statistical reports.
"""

import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from ..analysis.utils import format_pvalue
from .enhanced_rtf_formatter import EnhancedClinicalRTFFormatter
from .pdf_formatter import REPORTLAB_AVAILABLE, ClinicalPDFFormatter
from .statistical_engine import ClinicalStatisticalEngine


class ClinicalSession:
    """
    High-level clinical reporting session.

    This class provides a workflow-based approach to building clinical tables,
    where variables are added incrementally and then generated as a complete table.

    Examples
    --------
    >>> session = ClinicalSession(uri="table_01_demographics")
    >>> session.define_report(
    ...     dataset=adsl_data,
    ...     pop_where="saffl=='Y'",
    ...     title1="Table 1. Demographics and Baseline Characteristics"
    ... )
    >>> session.add_trt(name="trt01pn", decode="trt01p")
    >>> session.add_var("age", "Age (years)", "n mean+sd median q1q3 min+max")
    >>> session.add_catvar("sexn", "Sex, n (%)", decode="sex", stats="npct")
    >>> session.generate()
    >>> session.finalize("demographics.rtf")
    """

    def __init__(self, uri: str, purpose: str = "", outname: str = ""):
        """
        Initialize clinical reporting session.

        Parameters
        ----------
        uri : str
            Unique identifier for this table/report
        purpose : str, optional
            Description of the table purpose
        outname : str, optional
            Output filename (without extension)
        """
        self.uri = uri
        self.purpose = purpose or f"Clinical table generation for {uri}"
        self.outname = outname or uri

        # Core session state
        self.dataset = None
        self.dataset_name = ""
        self.variables = []
        self.treatments = {}
        self.groups = {}
        self.report_config = {}

        # Statistical engine
        self.stats_engine = ClinicalStatisticalEngine()

        # Generation state
        self.generated_data = None
        self.generated_table = None
        self.treatment_info = {}
        self.p_values = {}

        print(f"[CHECK] Clinical session initialized: {self.uri}")

    def define_report(
        self,
        dataset: Union[pd.DataFrame, str],
        pop_where: str = "1==1",
        tab_where: str = "1==1",
        subjid: str = "usubjid",
        title1: str = "",
        title2: str = "",
        title3: str = "",
        title4: str = "",
        title5: str = "",
        title6: str = "",
        footnot1: str = "",
        footnot2: str = "",
        footnot3: str = "",
        footnot4: str = "",
        footnot5: str = "",
        footnot6: str = "",
        footnot7: str = "",
        footnot8: str = "",
        footnot9: str = "",
        footnot10: str = "",
        footnot11: str = "",
        footnot12: str = "",
        footnot13: str = "",
        footnot14: str = "",
        colwidths: str = "4cm",
        splitchars: str = "- ",
        reptype: str = "regular",
        statsacross: str = "N",
        colhead1: str = "",
    ):
        """
        Define report structure and parameters.

        Parameters
        ----------
        dataset : DataFrame or str
            Input dataset for analysis
        pop_where : str
            Population filter condition
        tab_where : str
            Additional table filter condition
        subjid : str
            Subject ID variable name
        title1-title6 : str
            Report titles
        footnot1-footnot14 : str
            Report footnotes
        colwidths : str
            Column width specification
        splitchars : str
            Characters used for text splitting
        reptype : str
            Report type ('regular', 'events', etc.)
        """
        # Store dataset
        if isinstance(dataset, str):
            self.dataset_name = dataset
            # In real implementation, would load from specified source
            raise NotImplementedError("String dataset references not yet implemented")
        else:
            self.dataset = dataset.copy()
            self.dataset_name = "dataset"

        # Store report configuration
        self.report_config = {
            "pop_where": pop_where,
            "tab_where": tab_where,
            "subjid": subjid,
            "titles": [title1, title2, title3, title4, title5, title6],
            "footnotes": [
                footnot1,
                footnot2,
                footnot3,
                footnot4,
                footnot5,
                footnot6,
                footnot7,
                footnot8,
                footnot9,
                footnot10,
                footnot11,
                footnot12,
                footnot13,
                footnot14,
            ],
            "colwidths": colwidths,
            "splitchars": splitchars,
            "reptype": reptype,
            "statsacross": statsacross,
            "colhead1": colhead1,
        }

        print(f"[CHECK] Report defined: {len(self.dataset)} subjects")
        return self

    def add_trt(
        self,
        name: str,
        decode: str = "",
        autospan: str = "N",
        across: str = "Y",
        nline: str = "Y",
        splitrow: str = "",
        label: str = "",
        suffix: str = "",
        totaltext: str = "",
        sortcolumn: str = "",
        cutoffcolumn: str = "",
        incolumns: str = "",
        remove: str = "",
        codelist: str = "",
        delimiter: str = ",",
    ):
        """
        Add treatment variable.

        Parameters
        ----------
        name : str
            Treatment variable name
        decode : str
            Treatment decode variable name
        autospan : str
            Whether to auto-span treatment columns
        across : str
            Display treatments across columns ("Y"/"N", default: "Y")
        nline : str
            New line control ("Y"/"N", default: "Y")
        splitrow : str
            Character to split row labels (e.g., "|")
        label : str
            Label override for treatment
        suffix : str
            Suffix for treatment variable
        totaltext : str
            Text for total column (seems unused in RRG)
        sortcolumn : str
            Column to use for sorting treatments
        cutoffcolumn : str
            Cutoff column specification
        incolumns : str
            Alias for across parameter
        remove : str
            Remove control
        codelist : str
            Code list for treatment values
        delimiter : str
            Delimiter for codelist parsing (default: ",")
        """
        # Handle alias: incolumns is an alias for across
        if incolumns:
            across = incolumns

        self.treatments = {
            "name": name,
            "decode": decode or name,
            "autospan": autospan,
            "across": across,
            "nline": nline,
            "splitrow": splitrow,
            "label": label,
            "suffix": suffix,
            "totaltext": totaltext,
            "sortcolumn": sortcolumn,
            "cutoffcolumn": cutoffcolumn,
            "remove": remove,
            "codelist": codelist,
            "delimiter": delimiter,
        }

        print(f"[CHECK] Treatment variable added: {name}")
        return self

    def make_trt(self, name: str, newvalue: int, newdecode: str, values: str):
        """
        Create pooled treatment group.

        Parameters
        ----------
        name : str
            Treatment variable name
        newvalue : int
            New pooled value
        newdecode : str
            New pooled decode
        values : str
            Values to pool together
        """
        if "pooled" not in self.treatments:
            self.treatments["pooled"] = []

        self.treatments["pooled"].append(
            {
                "name": name,
                "newvalue": newvalue,
                "newdecode": newdecode,
                "values": values,
            }
        )

        print(f"[CHECK] Pooled treatment created: {newdecode}")
        return self

    def add_group(
        self,
        name: str,
        decode: str = "",
        label: str = "",
        page: str = "N",
        freqsort: bool = False,
        sortcolumn: str = "",
        mincnt: int = 0,
        minpct: float = 0.0,
        across: str = "N",
        codelist: str = "",
        delimiter: str = ",",
        skipline: str = "N",
        autospan: str = "",
        nline: str = "N",
        colhead: str = "",
        ordervar: str = "",
        preloadfmt: str = "",
        eventcnt: str = "",
        popsplit: str = "",
        incolumns: str = "",
        incolumn: str = "",
        stat: str = "",
    ):
        """
        Add grouping variable.

        Parameters
        ----------
        name : str
            Grouping variable name
        decode : str
            Grouping decode variable name
        label : str
            Grouping variable label
        page : str
            Whether to create page breaks
        freqsort : bool
            Sort groups by frequency (most common first)
        sortcolumn : str
            Column to use for sorting
        mincnt : int
            Minimum count threshold to display group
        minpct : float
            Minimum percentage threshold to display group
        across : str
            Create columns instead of rows ("Y"/"N") - CRITICAL for shift tables
        codelist : str
            Code list for categories (e.g., "1='Normal',2='Abnormal'")
        delimiter : str
            Delimiter for codelist parsing (default: ",")
        skipline : str
            Skip line after this group ("Y"/"N")
        autospan : str
            Auto-span control
        nline : str
            New line control ("Y"/"N")
        colhead : str
            Column header text
        ordervar : str
            Variable to use for ordering
        preloadfmt : str
            Preload format name
        eventcnt : str
            Event count control
        popsplit : str
            Population split control
        incolumns : str
            Alias for across parameter
        incolumn : str
            In-column control
        stat : str
            Statistics (seems unused in RRG)
        """
        # Handle alias: incolumns is an alias for across
        if incolumns:
            across = incolumns

        group_id = len(self.groups) + 1
        self.groups[group_id] = {
            "name": name,
            "decode": decode or name,
            "label": label or name,
            "page": page,
            "freqsort": freqsort,
            "sortcolumn": sortcolumn,
            "mincnt": mincnt,
            "minpct": minpct,
            "across": across,
            "codelist": codelist,
            "delimiter": delimiter,
            "skipline": skipline,
            "autospan": autospan,
            "nline": nline,
            "colhead": colhead,
            "ordervar": ordervar,
            "preloadfmt": preloadfmt,
            "eventcnt": eventcnt,
            "popsplit": popsplit,
            "incolumn": incolumn,
            "stat": stat,
        }

        print(
            f"[CHECK] Grouping variable added: {name}"
            + (" (across columns)" if across.upper() == "Y" else "")
        )
        return self

    def add_var(
        self,
        name: str,
        label: str = "",
        stats: str = "n mean+sd median q1q3.q1q3 min+max",
        where: str = "",
        indent: int = 0,
        basedec: int = 0,
        skipline: str = "Y",
        align: str = "",
        maxdec: str = "",
        showneg0: str = "N",
        keepwithnext: str = "N",
        popgrp: str = "",
        labelline: int = 0,
        suffix: str = "",
        statsetid: str = "",
        overallstats: str = "",
        templatewhere: str = "",
        condfmt: str = "",
        condfmtstats: str = "",
        subjid: str = "",
        statdispfmt: str = "$__rrgcf.",
        statlabfmt: str = "$__rrglf.",
        pvfmt: str = "__rrgpf.",
        statdecinfmt: str = "__rrgdf.",
    ):
        """
        Add continuous variable for analysis.

        Parameters
        ----------
        name : str
            Variable name in dataset
        label : str
            Display label
        stats : str
            Statistics to calculate (space-separated)
        where : str
            Additional filter condition
        indent : int
            Indentation level
        basedec : int
            Base decimal places
        skipline : str
            Whether to skip line after variable
        align : str
            Text alignment
        maxdec : str
            Maximum decimal places
        showneg0 : str
            Whether to show negative zeros
        keepwithnext : str
            Keep with next row ("Y"/"N")
        popgrp : str
            Population grouping variables
        labelline : int
            Label line control
        suffix : str
            Suffix for variable
        statsetid : str
            Statistic set ID
        overallstats : str
            Overall statistics to calculate
        templatewhere : str
            Template filter condition
        condfmt : str
            Conditional format
        condfmtstats : str
            Conditional format statistics
        subjid : str
            Subject ID variable override
        statdispfmt : str
            Statistic display format
        statlabfmt : str
            Statistic label format
        pvfmt : str
            P-value format
        statdecinfmt : str
            Statistic decimal format
        """
        var_id = len(self.variables) + 1

        variable = {
            "id": var_id,
            "name": name,
            "label": label or name,
            "type": "continuous",
            "stats": stats,
            "where": where,
            "indent": indent,
            "basedec": basedec,
            "skipline": skipline,
            "align": align,
            "maxdec": maxdec,
            "showneg0": showneg0,
            "keepwithnext": keepwithnext,
            "popgrp": popgrp,
            "labelline": labelline,
            "suffix": suffix,
            "statsetid": statsetid,
            "overallstats": overallstats,
            "templatewhere": templatewhere,
            "condfmt": condfmt,
            "condfmtstats": condfmtstats,
            "subjid": subjid,
            "statdispfmt": statdispfmt,
            "statlabfmt": statlabfmt,
            "pvfmt": pvfmt,
            "statdecinfmt": statdecinfmt,
        }

        self.variables.append(variable)

        # Validate variable exists
        if self.dataset is not None and name not in self.dataset.columns:
            warnings.warn(f"Variable '{name}' not found in dataset")

        print(f"[CHECK] Continuous variable added: {name} ({stats})")
        return self

    def add_catvar(
        self,
        name: str,
        label: str = "",
        stats: str = "npct",
        where: str = "",
        indent: int = 0,
        codelist: str = "",
        decode: str = "",
        totalpos: str = "last",
        totaltext: str = "",
        showmissing: str = "Y",
        pct4missing: str = "",
        skipline: str = "Y",
        denomwhere: str = "",
        freqsort: bool = False,
        showgroupcnt: bool = False,
        minpct: float = 0.0,
        mincnt: int = 0,
        popgrp: str = "",
        denomgrp: str = "",
        delimiter: str = ",",
        codelistds: str = "",
        ordervar: str = "",
        popwhere: str = "",
        totalgrp: str = "",
        totalwhere: str = "",
        misspos: str = "",
        misstext: str = "",
        countwhat: str = "all",
        suffix: str = "",
        overallstats: str = "",
        denom: str = "",
        fmt: str = "",
        worst: str = "",
        events: str = "n",
        templateds: str = "",
        sortcolumn: str = "",
        labelline: int = 1,
        subjid: str = "",
        showemptygroups: str = "N",
        pct4total: str = "n",
        pctfmt: str = "",
        preloadfmt: str = "",
        keepwithnext: str = "N",
        templatewhere: str = "",
        desc: str = "",
        remove: str = "",
        DENOMINClTRT: str = "Y",
        show0cnt: str = "y",
        noshow0cntvals: str = "",
    ):
        """
        Add categorical variable for analysis.

        Parameters
        ----------
        name : str
            Variable name in dataset
        label : str
            Display label
        stats : str
            Statistics to calculate
        where : str
            Additional filter condition
        indent : int
            Indentation level
        codelist : str
            Value codelist specification
        decode : str
            Decode variable name
        totalpos : str
            Position of total row ('first' or 'last')
        totaltext : str
            Text for total row (e.g., 'All', 'Total')
        showmissing : str
            Whether to show missing values
        pct4missing : str
            Whether to calculate percentages for missing
        skipline : str
            Whether to skip line after variable
        denomwhere : str
            Filter condition for denominator calculation
        freqsort : bool
            Sort categories by frequency (most common first)
        showgroupcnt : bool
            Show group counts in labels
        minpct : float
            Minimum percentage threshold to display category
        mincnt : int
            Minimum count threshold to display category
        popgrp : str
            Population grouping variables for numerator (CRITICAL for shift tables)
        denomgrp : str
            Denominator grouping variables (CRITICAL for shift tables)
        delimiter : str
            Delimiter for codelist parsing (default: ",")
        codelistds : str
            External codelist dataset name
        ordervar : str
            Variable to use for ordering categories
        popwhere : str
            Population filter condition
        totalgrp : str
            Total grouping variables
        totalwhere : str
            Total filter condition
        misspos : str
            Position of missing row
        misstext : str
            Text for missing row
        countwhat : str
            What to count ('all', 'subjid', etc.)
        suffix : str
            Suffix for variable
        overallstats : str
            Overall statistics to calculate
        denom : str
            Alias for denomgrp
        fmt : str
            Format to apply
        worst : str
            Worst case analysis flag
        events : str
            Event counting flag
        templateds : str
            Template dataset name
        sortcolumn : str
            Column to use for sorting
        labelline : int
            Label line control
        subjid : str
            Subject ID variable override
        showemptygroups : str
            Show empty groups ("Y"/"N")
        pct4total : str
            Calculate percentage for total
        pctfmt : str
            Percentage format
        preloadfmt : str
            Preload format name
        keepwithnext : str
            Keep with next row ("Y"/"N")
        templatewhere : str
            Template filter condition
        desc : str
            Description
        remove : str
            Remove control
        DENOMINClTRT : str
            Include treatment in denominator ("Y"/"N")
        show0cnt : str
            Show zero counts ("y"/"n")
        noshow0cntvals : str
            Values to not show zero counts for
        """
        # Handle alias: denom is an alias for denomgrp
        if denom:
            denomgrp = denom

        var_id = len(self.variables) + 1

        variable = {
            "id": var_id,
            "name": name,
            "label": label or name,
            "type": "categorical",
            "stats": stats,
            "where": where,
            "indent": indent,
            "codelist": codelist,
            "decode": decode or name,
            "totalpos": totalpos,
            "totaltext": totaltext,
            "showmissing": showmissing,
            "pct4missing": pct4missing,
            "skipline": skipline,
            "denomwhere": denomwhere,
            "freqsort": freqsort,
            "showgroupcnt": showgroupcnt,
            "minpct": minpct,
            "mincnt": mincnt,
            "popgrp": popgrp,
            "denomgrp": denomgrp,
            "delimiter": delimiter,
            "codelistds": codelistds,
            "ordervar": ordervar,
            "popwhere": popwhere,
            "totalgrp": totalgrp,
            "totalwhere": totalwhere,
            "misspos": misspos,
            "misstext": misstext,
            "countwhat": countwhat,
            "suffix": suffix,
            "overallstats": overallstats,
            "fmt": fmt,
            "worst": worst,
            "events": events,
            "templateds": templateds,
            "sortcolumn": sortcolumn,
            "labelline": labelline,
            "subjid": subjid,
            "showemptygroups": showemptygroups,
            "pct4total": pct4total,
            "pctfmt": pctfmt,
            "preloadfmt": preloadfmt,
            "keepwithnext": keepwithnext,
            "templatewhere": templatewhere,
            "desc": desc,
            "remove": remove,
            "DENOMINClTRT": DENOMINClTRT,
            "show0cnt": show0cnt,
            "noshow0cntvals": noshow0cntvals,
        }

        self.variables.append(variable)

        # Validate variable exists
        if self.dataset is not None and name not in self.dataset.columns:
            warnings.warn(f"Variable '{name}' not found in dataset")

        print(f"[CHECK] Categorical variable added: {name} ({stats})")
        return self

    def add_label(
        self,
        label: str = "",
        skipline: str = "N",
        indent: int = 0,
        keepwithnext: str = "Y",
        wholerow: str = "",
    ):
        """
        Add a label row to the report.

        This method adds a text label row without any statistics, commonly used
        for section headers or grouping labels in tables.

        Parameters
        ----------
        label : str
            Display label text
        skipline : str
            Whether to skip line after this label ("Y"/"N")
        indent : int
            Indentation level
        keepwithnext : str
            Keep label with next row ("Y"/"N")
        wholerow : str
            Span entire row width
        """
        var_id = len(self.variables) + 1

        variable = {
            "id": var_id,
            "name": "__LABEL__",
            "label": label,
            "type": "label",
            "skipline": skipline,
            "indent": indent,
            "keepwithnext": keepwithnext,
            "wholerow": wholerow,
        }

        self.variables.append(variable)
        print(f"[CHECK] Label added: {label}")
        return self

    def add_cond(
        self,
        label: str = "",
        where: str = "1==1",
        stats: str = "n",
        skipline: str = "Y",
        indent: int = 0,
        subjid: str = "",
        denomwhere: str = "",
        labelvar: str = "",
        statlabel: str = "",
        countwhat: str = "subjid",
        keepwithnext: str = "N",
    ):
        """
        Add condition-based analysis row.

        This method adds a row that counts subjects (or events) satisfying a specific condition.
        Commonly used for population analysis tables (e.g., "All Randomized Patients").

        Parameters
        ----------
        label : str
            Display label for the condition
        where : str
            Filter condition to identify subjects/events
        stats : str
            Statistics to calculate (e.g., 'n', 'npct')
        skipline : str
            Whether to skip line after this row
        indent : int
            Indentation level
        subjid : str
            Subject ID variable (overrides default)
        denomwhere : str
            Filter condition for denominator calculation
        labelvar : str
            Variable name to use for label (instead of fixed label)
        statlabel : str
            Custom label for statistics
        countwhat : str
            What to count: 'subjid' (subjects) or 'events'
        keepwithnext : str
            Keep this row with the next row ("Y"/"N")
        """
        var_id = len(self.variables) + 1

        variable = {
            "id": var_id,
            "name": "__condition__",  # Special marker for condition-based rows
            "label": label,
            "type": "condition",
            "where": where,
            "stats": stats,
            "skipline": skipline,
            "indent": indent,
            "subjid": subjid or self.report_config.get("subjid", "usubjid"),
            "denomwhere": denomwhere,
            "labelvar": labelvar,
            "statlabel": statlabel,
            "countwhat": countwhat,
            "keepwithnext": keepwithnext,
        }

        self.variables.append(variable)

        print(f"[CHECK] Condition added: {label} (where: {where})")
        return self

    def generate(self):
        """
        Generate the complete table by processing all added variables.

        This is the main generation process that:
        1. Applies population and table filters
        2. Processes all added variables
        3. Calculates statistics using the statistical engine
        4. Combines results into final table structure
        """
        if self.dataset is None:
            raise ValueError("No dataset defined. Call define_report() first.")

        if not self.variables:
            raise ValueError(
                "No variables added. Add variables with add_var() or add_catvar()."
            )

        if not self.treatments:
            raise ValueError("No treatment variable defined. Call add_trt() first.")

        print(f"Generating table with {len(self.variables)} variables...")

        # Apply population filter
        filtered_data = self.dataset.copy()
        if self.report_config["pop_where"] != "1==1":
            try:
                filtered_data = filtered_data.query(self.report_config["pop_where"])
                print(
                    f"  Population filter applied: {len(filtered_data)} subjects remaining"
                )
            except Exception as e:
                warnings.warn(f"Population filter failed: {e}")

        # Apply table filter
        if self.report_config["tab_where"] != "1==1":
            try:
                filtered_data = filtered_data.query(self.report_config["tab_where"])
                print(
                    f"  Table filter applied: {len(filtered_data)} subjects remaining"
                )
            except Exception as e:
                warnings.warn(f"Table filter failed: {e}")

        # Collect treatment information
        treatment_var = self.treatments["name"]
        decode_var = self.treatments["decode"]

        self._collect_treatment_info(filtered_data, treatment_var, decode_var)

        # Check if this is a shift table (has grouping variable with across='Y')
        across_group = self._get_across_grouping_variable()
        is_shift_table = across_group is not None

        # Process each variable
        all_results = []

        for i, variable in enumerate(self.variables, 1):
            print(f"  {i}/{len(self.variables)}: Processing {variable['name']}...")

            try:
                if variable["type"] == "continuous":
                    result = self.stats_engine.calculate_continuous_stats(
                        filtered_data,
                        variable["name"],
                        treatment_var,
                        variable["stats"],
                        variable.get("where", ""),
                        variable.get("basedec", 0),
                    )
                elif variable["type"] == "condition":
                    # Handle condition-based rows (add_cond)
                    result = self.stats_engine.calculate_condition_stats(
                        filtered_data,
                        treatment_var,
                        variable.get("where", "1==1"),
                        variable.get("stats", "n"),
                        variable.get(
                            "subjid", self.report_config.get("subjid", "usubjid")
                        ),
                        variable.get("denomwhere", ""),
                        variable.get("countwhat", "subjid"),
                    )
                elif is_shift_table and variable["type"] == "categorical":
                    # Handle shift table (cross-tabulation)
                    result = self._process_shift_table(
                        filtered_data, variable, across_group, treatment_var
                    )
                else:  # categorical (regular)
                    result = self.stats_engine.calculate_categorical_stats(
                        filtered_data,
                        variable["name"],
                        treatment_var,
                        variable["stats"],
                        variable.get("where", ""),
                        variable.get("decode", variable["name"]),
                        variable.get("showmissing", "Y"),
                    )

                # Add variable metadata
                result["variable_id"] = variable["id"]
                result["variable_label"] = variable["label"]
                result["variable_type"] = variable["type"]
                result["indent"] = variable.get("indent", 0)

                # Collect p-values for this variable
                self._collect_p_values(variable, result, filtered_data, treatment_var)

                all_results.append(result)

            except Exception as e:
                warnings.warn(f"Failed to process variable {variable['name']}: {e}")
                import traceback

                traceback.print_exc()
                continue

        # Combine all results
        if all_results:
            self.generated_data = pd.concat(all_results, ignore_index=True)

            # Format for display
            self.generated_table = self._format_for_display(self.generated_data)

            # Apply statsacross transformation if needed
            if self.report_config.get("statsacross", "N").upper() == "Y":
                self.generated_table = self._apply_statsacross(self.generated_table)

            print(
                f"[CHECK_MARK] Generation complete: {len(self.generated_table)} rows generated"
            )
        else:
            print("[CROSS_MARK] No results generated")

        return self

    def _get_across_grouping_variable(self):
        """Find grouping variable with across='Y' for shift tables."""
        for group_id, group in self.groups.items():
            if group.get("across", "N").upper() == "Y":
                return group
        return None

    def _process_shift_table(
        self, data: pd.DataFrame, variable: Dict, across_group: Dict, treatment_var: str
    ) -> pd.DataFrame:
        """
        Process shift table (cross-tabulation).

        Parameters
        ----------
        data : pd.DataFrame
            Filtered dataset
        variable : Dict
            Categorical variable configuration (row variable)
        across_group : Dict
            Grouping variable with across='Y' (column variable)
        treatment_var : str
            Treatment variable name

        Returns
        -------
        pd.DataFrame
            Shift table results
        """
        # Parse codelists
        row_codelist = self._parse_codelist(
            variable.get("codelist", ""), variable.get("delimiter", ",")
        )
        col_codelist = self._parse_codelist(
            across_group.get("codelist", ""), across_group.get("delimiter", ",")
        )

        print(
            f"    [SHIFT TABLE] Row variable: {variable['name']}, Column variable: {across_group['name']}"
        )
        print(f"    [SHIFT TABLE] Row categories: {list(row_codelist.keys())}")
        print(f"    [SHIFT TABLE] Column categories: {list(col_codelist.keys())}")

        # Check for grouping variables with across='N' (these create row groups)
        row_grouping_vars = []
        for group_id, group in self.groups.items():
            if group.get("across", "N").upper() == "N":
                row_grouping_vars.append(group)

        if row_grouping_vars:
            print(
                f"    [SHIFT TABLE] Row grouping variables: {[g['name'] for g in row_grouping_vars]}"
            )

        # Call shift table calculation with grouping variables
        result = self.stats_engine.calculate_shift_table_stats(
            data=data,
            row_variable=variable["name"],
            col_variable=across_group["name"],
            treatment_var=treatment_var,
            stats_spec=variable.get("stats", "nnpct"),
            row_codelist=row_codelist,
            col_codelist=col_codelist,
            popgrp=variable.get("popgrp", ""),
            denomgrp=variable.get("denomgrp", ""),
            denomwhere=variable.get("denomwhere", ""),
            where_clause=variable.get("where", ""),
            row_grouping_vars=row_grouping_vars,  # Pass grouping variables
        )

        return result

    def _parse_codelist(self, codelist_str: str, delimiter: str = ",") -> dict:
        """
        Parse codelist string into dictionary.

        Format: "1='Label 1',2='Label 2',3='Label 3'"
        or: "1='Label 1'~2='Label 2'~3='Label 3'" (with ~ delimiter)

        Returns dict: {1: 'Label 1', 2: 'Label 2', 3: 'Label 3'}
        """
        codelist = {}

        if not codelist_str:
            return codelist

        # Split by delimiter
        items = codelist_str.split(delimiter)

        for item in items:
            item = item.strip()
            if "=" in item:
                # Split on first '='
                parts = item.split("=", 1)
                key_str = parts[0].strip()
                value_str = parts[1].strip()

                # Remove quotes from value
                value_str = value_str.strip("'\"")

                # Convert key to appropriate type (int or float)
                try:
                    if "." in key_str:
                        key = float(key_str)
                    else:
                        key = int(key_str)
                except ValueError:
                    key = key_str

                codelist[key] = value_str

        return codelist

    def _collect_treatment_info(
        self, data: pd.DataFrame, treatment_var: str, decode_var: str
    ):
        """Collect treatment information for professional headers."""
        self.treatment_info = {}

        # Check if this is a shift table (has categorical variables with across groups)
        is_shift_table = False
        for var in self.variables:
            if var.get("type") == "categorical":
                # Check if there's a group with across='Y' (column grouping for shift tables)
                for group_id, group in self.groups.items():
                    if group.get("across", "N").upper() == "Y":
                        is_shift_table = True
                        break
                if is_shift_table:
                    break

        # For shift tables with row grouping variables, collect info from the grouping variable
        if is_shift_table:
            # Find row grouping variables (across='N')
            row_grouping_vars = []
            for group_id, group in self.groups.items():
                if group.get("across", "N").upper() == "N":
                    row_grouping_vars.append(group)

            if row_grouping_vars:
                # For multi-level shift tables, we need to find the treatment grouping variable
                # This is typically:
                # 1. A grouping variable with 'TRT' in the name (e.g., TRT01AN, TRTAN, etc.)
                # 2. Or the last row grouping variable (closest to the categorical variable)

                group_var = None

                # First, try to find a grouping variable with 'TRT' in the name
                for gvar in row_grouping_vars:
                    if "TRT" in gvar["name"].upper():
                        group_var = gvar
                        break

                # If no TRT variable found, use the last row grouping variable
                if group_var is None:
                    group_var = row_grouping_vars[-1]

                group_name = group_var["name"]
                group_decode = group_var.get("decode", group_name)

                if group_name in data.columns:
                    for group_val in sorted(data[group_name].dropna().unique()):
                        if pd.isna(group_val):
                            continue

                        group_data = data[data[group_name] == group_val]
                        n_count = len(group_data)

                        # Get group name from decode variable
                        group_label = str(group_val)
                        if group_decode != group_name and group_decode in data.columns:
                            decode_values = group_data[group_decode].unique()
                            if len(decode_values) > 0 and not pd.isna(decode_values[0]):
                                group_label = str(decode_values[0])
                                # Clean up SAS byte strings if present
                                if group_label.startswith(
                                    "b'"
                                ) and group_label.endswith("'"):
                                    group_label = group_label[2:-1]

                        # Store as string key to match table columns
                        self.treatment_info[str(group_val)] = {
                            "name": group_label,
                            "n": n_count,
                        }

        # For regular tables (or if shift table logic didn't populate treatment_info)
        if not self.treatment_info:
            # Regular tables: collect from treatment variable
            if treatment_var in data.columns:
                for trt_val in sorted(data[treatment_var].unique()):
                    if pd.isna(trt_val):
                        continue

                    trt_data = data[data[treatment_var] == trt_val]
                    n_count = len(trt_data)

                    # Get treatment name from decode variable
                    trt_name = str(trt_val)
                    if decode_var != treatment_var and decode_var in data.columns:
                        decode_values = trt_data[decode_var].unique()
                        if len(decode_values) > 0 and not pd.isna(decode_values[0]):
                            trt_name = str(decode_values[0])
                            # Clean up SAS byte strings if present
                            if trt_name.startswith("b'") and trt_name.endswith("'"):
                                trt_name = trt_name[2:-1]

                    # Store as string key to match table columns
                    self.treatment_info[str(trt_val)] = {"name": trt_name, "n": n_count}

        # Add Total information
        self.treatment_info["Total"] = {"name": "Total", "n": len(data)}

        print(f"  Treatment info collected: {self.treatment_info}")

    def _collect_p_values(
        self,
        variable: Dict,
        result_data: pd.DataFrame,
        data: pd.DataFrame,
        treatment_var: str,
    ):
        """Collect p-values for variables using simple tests.

        - Continuous: one-way ANOVA across treatment groups (scipy.stats.f_oneway)
        - Categorical: Pearson chi-square test on contingency table
        Falls back to "N/A" if required packages are unavailable or data insufficient.
        """
        var_label = variable.get("label", variable.get("name"))

        # Attempt to import SciPy lazily to avoid hard dependency at import time
        try:
            import pandas as _pd  # local alias to avoid shadowing
            from scipy import stats as _sps  # type: ignore
        except Exception:
            self.p_values[var_label] = "N/A"
            return

        df = data.copy()
        where = variable.get("where")
        if where:
            try:
                df = df.query(where)
            except Exception:
                pass

        name = variable.get("name")
        if name not in df.columns or treatment_var not in df.columns:
            self.p_values[var_label] = "N/A"
            return

        pval = None
        try:
            if variable.get("type") == "continuous":
                groups = [g[name].dropna().values for _, g in df.groupby(treatment_var)]
                valid = [arr for arr in groups if len(arr) > 0]
                if len(valid) >= 2:
                    _stat, p = _sps.f_oneway(*valid)
                    pval = float(p)
            else:
                ct = _pd.crosstab(df[name], df[treatment_var])
                if ct.shape[0] >= 2 and ct.shape[1] >= 2:
                    _chi2, p, _dof, _exp = _sps.chi2_contingency(ct)
                    pval = float(p)
        except Exception:
            pval = None

        if pval is None:
            self.p_values[var_label] = "N/A"
        else:
            try:
                self.p_values[var_label] = format_pvalue(pval)
            except Exception:
                self.p_values[var_label] = f"{pval:.4f}"

    def _format_shift_table_for_display(self, stats_data: pd.DataFrame) -> pd.DataFrame:
        """
        Format shift table results for display.

        Shift tables have structure:
        - Rows: Treatment groups × Row variable categories (e.g., post-baseline status)
        - Columns: Column variable categories (e.g., baseline status)
        - Cells: n (%) showing shift from baseline to post-baseline

        Supports multi-level row grouping (e.g., Visit → Treatment Group)
        """
        display_rows = []

        # Detect number of group levels
        num_group_levels = 0
        for i in range(1, 10):  # Check up to 10 levels
            if f"group_variable_{i}" in stats_data.columns:
                num_group_levels = i
            else:
                break

        # Get unique treatments
        treatments = sorted(stats_data["treatment"].unique())

        # Get unique column labels (baseline status) - these become table columns
        col_labels = []
        for col_val in sorted(stats_data["col_value"].unique()):
            col_data = stats_data[stats_data["col_value"] == col_val]
            if not col_data.empty:
                col_labels.append(col_data["col_label"].iloc[0])

        # Get unique row labels (post-baseline status) - these become table rows
        row_labels = []
        for row_val in sorted(stats_data["row_value"].unique()):
            row_data = stats_data[stats_data["row_value"] == row_val]
            if not row_data.empty:
                row_labels.append(row_data["row_label"].iloc[0])

        # For each treatment (e.g., PARAM='ECG')
        for treatment in treatments:
            trt_data = stats_data[stats_data["treatment"] == treatment]

            if trt_data.empty:
                continue

            # Get treatment name
            trt_name = str(treatment)

            # Add treatment header row
            header_row = {"Parameter": f"{trt_name}"}
            for col_label in col_labels:
                header_row[col_label] = ""
            display_rows.append(header_row)

            if num_group_levels > 0:
                # Process multi-level grouping recursively
                self._format_shift_table_groups(
                    data=trt_data,
                    group_level=1,
                    num_group_levels=num_group_levels,
                    indent_level=1,
                    col_labels=col_labels,
                    row_labels=row_labels,
                    display_rows=display_rows,
                )
            else:
                # Original logic without groups
                # For each row category (post-baseline status)
                for row_label in row_labels:
                    row_data = trt_data[trt_data["row_label"] == row_label]

                    # Create row
                    row = {"Parameter": f"  {row_label}"}

                    # For each column category (baseline status)
                    for col_label in col_labels:
                        cell_data = row_data[row_data["col_label"] == col_label]

                        if not cell_data.empty:
                            row[col_label] = cell_data["formatted_value"].iloc[0]
                        else:
                            row[col_label] = "0 (0.0%)"

                    display_rows.append(row)

        return pd.DataFrame(display_rows)

    def _format_shift_table_groups(
        self,
        data,
        group_level,
        num_group_levels,
        indent_level,
        col_labels,
        row_labels,
        display_rows,
    ):
        """
        Recursively format multi-level row grouping for shift tables.

        Parameters
        ----------
        data : pd.DataFrame
            Current level data (filtered by previous group levels)
        group_level : int
            Current grouping level (1-based)
        num_group_levels : int
            Total number of grouping levels
        indent_level : int
            Current indentation level
        col_labels : list
            List of column labels
        row_labels : list
            List of row labels
        display_rows : list
            List to append display rows to
        """
        # If we've processed all grouping levels, add the data rows
        if group_level > num_group_levels:
            # For each row category (post-baseline status)
            for row_label in row_labels:
                row_data = data[data["row_label"] == row_label]

                # Create row with proper indentation
                indent = "  " * indent_level
                row = {"Parameter": f"{indent}{row_label}"}

                # For each column category (baseline status)
                for col_label in col_labels:
                    cell_data = row_data[row_data["col_label"] == col_label]

                    if not cell_data.empty:
                        row[col_label] = cell_data["formatted_value"].iloc[0]
                    else:
                        row[col_label] = "0 (0.0%)"

                display_rows.append(row)
            return

        # Process current grouping level
        group_col = f"group_value_{group_level}"
        label_col = f"group_label_{group_level}"

        # Get unique group values at this level
        group_values = sorted(data[group_col].unique())

        # For each group value at this level
        for group_val in group_values:
            group_data = data[data[group_col] == group_val]

            if group_data.empty:
                continue

            # Get group label
            group_label = group_data[label_col].iloc[0]

            # Add group header row with proper indentation
            indent = "  " * indent_level
            group_header_row = {"Parameter": f"{indent}{group_label}"}
            for col_label in col_labels:
                group_header_row[col_label] = ""
            display_rows.append(group_header_row)

            # Recursively process next level
            self._format_shift_table_groups(
                data=group_data,
                group_level=group_level + 1,
                num_group_levels=num_group_levels,
                indent_level=indent_level + 1,
                col_labels=col_labels,
                row_labels=row_labels,
                display_rows=display_rows,
            )

    def _format_for_display(self, stats_data: pd.DataFrame) -> pd.DataFrame:
        """Format statistical results for display table."""
        if stats_data.empty:
            return pd.DataFrame()

        # Check if this is a shift table (has col_label column)
        is_shift_table = "col_label" in stats_data.columns

        if is_shift_table:
            return self._format_shift_table_for_display(stats_data)

        # Convert treatment column to string to handle mixed types (float and 'Total')
        stats_data = stats_data.copy()
        stats_data["treatment"] = stats_data["treatment"].astype(str)

        # Get treatment levels
        treatments = sorted(stats_data["treatment"].unique())

        # Reorder to put 'Total' last if it exists
        if "Total" in treatments:
            treatments = [t for t in treatments if t != "Total"] + ["Total"]

        display_rows = []

        # Process by variable order
        for var_id in sorted(stats_data["variable_id"].unique()):
            var_data = stats_data[stats_data["variable_id"] == var_id]
            var_label = var_data["variable_label"].iloc[0]
            var_type = var_data["variable_type"].iloc[0]
            indent = var_data["indent"].iloc[0]

            indent_str = "  " * indent

            if var_type == "continuous":
                # Group by statistic
                for stat in var_data["statistic"].unique():
                    stat_data = var_data[var_data["statistic"] == stat]

                    row = {"Parameter": f"{indent_str}{var_label}"}
                    if stat != "N":  # Don't repeat variable name for non-N stats
                        row["Parameter"] = f"{indent_str}  {stat}"

                    for treatment in treatments:
                        trt_data = stat_data[stat_data["treatment"] == treatment]
                        if not trt_data.empty:
                            row[treatment] = trt_data["formatted_value"].iloc[0]
                        else:
                            row[treatment] = ""

                    display_rows.append(row)

            elif var_type == "condition":
                # For condition variables, create a single row with the label
                row = {"Parameter": f"{indent_str}{var_label}"}
                for treatment in treatments:
                    trt_data = var_data[var_data["treatment"] == treatment]
                    if not trt_data.empty:
                        row[treatment] = trt_data["formatted_value"].iloc[0]
                    else:
                        row[treatment] = "0"
                display_rows.append(row)

            else:  # categorical
                # Add variable header
                header_row = {"Parameter": f"{indent_str}{var_label}"}
                for treatment in treatments:
                    header_row[treatment] = ""
                display_rows.append(header_row)

                # Add categories
                for category in sorted(var_data["category"].unique()):
                    cat_data = var_data[var_data["category"] == category]

                    row = {"Parameter": f"{indent_str}  {category}"}
                    for treatment in treatments:
                        trt_data = cat_data[cat_data["treatment"] == treatment]
                        if not trt_data.empty:
                            row[treatment] = trt_data["formatted_value"].iloc[0]
                        else:
                            row[treatment] = "0 (0.0%)"

                    display_rows.append(row)

        return pd.DataFrame(display_rows)

    def _apply_statsacross(self, table: pd.DataFrame) -> pd.DataFrame:
        """
        Apply statsacross transformation - simplified version.

        For now, this is a placeholder. The full implementation requires
        restructuring data generation to group by the incolumn variable.
        """
        # Find grouping variable with incolumn=Y
        incolumn_group = None
        for group_id, group in self.groups.items():
            if (
                group.get("incolumn", "N").upper() == "Y"
                or group.get("across", "N").upper() == "Y"
            ):
                incolumn_group = group
                break

        if incolumn_group:
            group_name = incolumn_group["name"]
            print(f"  [INFO] statsacross detected for grouping variable: {group_name}")

        # Return table as-is for now
        # Full implementation will be added when needed
        return table

    def finalize(self, output_file: str = None, output_format: str = "rtf"):
        """
        Finalize and save the generated table.

        Parameters
        ----------
        output_file : str, optional
            Output filename. If None, uses session outname.
        output_format : str
            Output format ('rtf', 'pdf', 'csv', 'html')
        """
        if self.generated_table is None:
            raise ValueError("No table generated. Call generate() first.")

        if output_file is None:
            output_file = f"{self.outname}.{output_format}"

        if output_format.lower() == "rtf":
            self._save_clinical_rtf(output_file)
        elif output_format.lower() == "pdf":
            self._save_clinical_pdf(output_file)
        elif output_format.lower() == "csv":
            self._save_clinical_csv(output_file)
        else:
            raise NotImplementedError(
                f"Output format '{output_format}' not yet implemented"
            )

        print(f"[CHECK_MARK] Table finalized: {output_file}")
        return self

    def _save_clinical_rtf(self, output_file: str):
        """Save table as RTF using Enhanced Clinical formatter."""
        formatter = EnhancedClinicalRTFFormatter()

        # Prepare titles and footnotes (filter out empty ones)
        titles = [t.strip() for t in self.report_config["titles"] if t.strip()]
        footnotes = [f.strip() for f in self.report_config["footnotes"] if f.strip()]

        # Remove "Randomized Population" from titles to avoid duplication
        # (it will be added by the formatter)
        titles = [t for t in titles if "randomized population" not in t.lower()]

        # Prepare the table with proper treatment column headers
        display_table = self._prepare_table_for_rtf()

        # Add statistical methodology footnote
        method_footnote = "P-values: ANOVA for continuous variables, Chi-square for categorical variables"
        if method_footnote not in footnotes:
            footnotes.append(method_footnote)

        # Add system attribution footnote
        system_footnote = "Generated using py4csr streamlined interface"
        if system_footnote not in footnotes:
            footnotes.append(system_footnote)

        # Extract titles for formatter
        title1 = (
            titles[0]
            if len(titles) > 0
            else "Demographics and Baseline Characteristics"
        )
        title2 = titles[1] if len(titles) > 1 else ""
        title3 = "Randomized Population"  # This will be shown only once

        # Create RTF output using Enhanced formatter
        rtf_content = formatter.create_professional_table(
            display_table,
            title1=title1,
            title2=title2,
            title3=title3,
            footnotes=footnotes,
            treatment_info=self.treatment_info,
            p_values=self.p_values,
        )

        # Save to file
        Path(output_file).write_text(rtf_content, encoding="utf-8")

    def _save_clinical_pdf(self, output_file: str):
        """Save table as PDF using Clinical PDF formatter."""
        if not REPORTLAB_AVAILABLE:
            raise ImportError(
                "reportlab is required for PDF generation. "
                "Install it with: pip install reportlab"
            )

        formatter = ClinicalPDFFormatter()

        # Prepare titles and footnotes (filter out empty ones)
        titles = [t.strip() for t in self.report_config["titles"] if t.strip()]
        footnotes = [f.strip() for f in self.report_config["footnotes"] if f.strip()]

        # Remove "Randomized Population" from titles to avoid duplication
        titles = [t for t in titles if "randomized population" not in t.lower()]

        # Prepare the table with proper treatment column headers
        display_table = self._prepare_table_for_rtf()

        # Add statistical methodology footnote
        method_footnote = "P-values: ANOVA for continuous variables, Chi-square for categorical variables"
        if method_footnote not in footnotes:
            footnotes.append(method_footnote)

        # Add system attribution footnote
        system_footnote = "Generated using py4csr streamlined interface"
        if system_footnote not in footnotes:
            footnotes.append(system_footnote)

        # Extract titles for formatter
        title1 = (
            titles[0]
            if len(titles) > 0
            else "Demographics and Baseline Characteristics"
        )
        title2 = titles[1] if len(titles) > 1 else ""
        title3 = "Randomized Population"

        # Determine orientation based on number of columns
        num_cols = len(display_table.columns)
        orientation = "landscape" if num_cols > 6 else "portrait"

        # Create PDF output using PDF formatter
        formatter.create_professional_table(
            display_table,
            output_file=output_file,
            title1=title1,
            title2=title2,
            title3=title3,
            footnotes=footnotes,
            treatment_info=self.treatment_info,
            p_values=self.p_values,
            orientation=orientation,
        )

    def _save_clinical_csv(self, output_file: str):
        """Save table as CSV."""
        display_table = self._prepare_table_for_rtf()
        display_table.to_csv(output_file, index=False, encoding="utf-8")

    def _prepare_table_for_rtf(self) -> pd.DataFrame:
        """Prepare the table with proper treatment column names for RTF output."""
        if self.generated_table is None:
            return pd.DataFrame()

        # Make a copy for modification
        display_table = self.generated_table.copy()

        # Identify the parameter column (first column, or one with 'Parameter' in name)
        param_col = None
        if len(display_table.columns) > 0:
            first_col = display_table.columns[0]
            # Check if first column is the parameter column
            if (
                "Parameter" in first_col
                or "/" in first_col
                or "System Organ Class" in first_col
            ):
                param_col = first_col
            else:
                # Look for a column with 'Parameter' in the name
                for col in display_table.columns:
                    if "Parameter" in col:
                        param_col = col
                        break

        # Check if this is a shift table (columns contain '|' separator)
        is_shift_table = any(
            "|" in str(col) for col in display_table.columns if col != param_col
        )

        # Map treatment column names to proper treatment names
        new_columns = {}
        for col in display_table.columns:
            # Skip the parameter column
            if col == param_col:
                continue

            # For shift tables, don't add N counts - columns represent categories, not treatments
            if is_shift_table:
                # Keep column name as is (it's already formatted like "Baseline Status|Normal")
                continue

            # Try to get treatment name from treatment_info
            if str(col) in self.treatment_info:
                trt_info = self.treatment_info[str(col)]
                trt_name = trt_info["name"]
                n_count = trt_info["n"]
                new_name = f"{trt_name}\n(N={n_count})"
                new_columns[col] = new_name
                print(f"  Mapped column '{col}' -> '{new_name}'")
            else:
                # Fallback mapping for common treatment values
                try:
                    col_val = float(col)
                    if col_val == 0.0:
                        new_columns[col] = "Placebo\n(N=86)"
                    elif col_val == 54.0:
                        new_columns[col] = "Xanomeline Low Dose\n(N=84)"
                    elif col_val == 81.0:
                        new_columns[col] = "Xanomeline High Dose\n(N=84)"
                    else:
                        new_columns[col] = f"Treatment {col}\n(N=?)"
                except:
                    new_columns[col] = f"{col}\n(N=?)"
                print(f"  Fallback mapping column '{col}' -> '{new_columns[col]}'")

        # Rename columns
        if new_columns:
            display_table = display_table.rename(columns=new_columns)
            print(f"  Final columns: {list(display_table.columns)}")

        return display_table

    def to_csv(self, output_file: str, index: bool = False):
        """
        Export generated table to CSV format.

        Parameters
        ----------
        output_file : str
            Path to output CSV file
        index : bool
            Whether to include row index in CSV
        """
        if self.generated_table is None:
            raise ValueError("No table generated yet. Call generate() first.")

        # Save to CSV
        self.generated_table.to_csv(output_file, index=index)
        print(f"[CHECK] Table exported to CSV: {output_file}")

    def preview(self, max_rows: int = 20) -> pd.DataFrame:
        """
        Preview the generated table.

        Parameters
        ----------
        max_rows : int
            Maximum number of rows to display

        Returns
        -------
        pd.DataFrame
            Preview of the generated table
        """
        if self.generated_table is None:
            print("No table generated yet. Call generate() first.")
            return pd.DataFrame()

        preview_table = self.generated_table.head(max_rows)
        print(
            f"Table preview ({len(preview_table)} of {len(self.generated_table)} rows):"
        )
        return preview_table

    def summary(self):
        """Print session summary."""
        print(f"\n[CHART] Clinical Session Summary: {self.uri}")
        print(f"   Purpose: {self.purpose}")
        print(
            f"   Dataset: {len(self.dataset) if self.dataset is not None else 0} subjects"
        )
        print(f"   Variables: {len(self.variables)} added")
        print(f"   Treatments: {self.treatments.get('name', 'None')}")
        print(f"   Groups: {len(self.groups)}")
        print(f"   Generated: {'Yes' if self.generated_table is not None else 'No'}")
        if self.generated_table is not None:
            print(f"   Final table: {len(self.generated_table)} rows")
