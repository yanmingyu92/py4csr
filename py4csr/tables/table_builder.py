"""
Enhanced Table Builder for Clinical Reporting
Integrates with professional RTF formatter for publication-ready tables.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from pathlib import Path
import os

from .rtf_formatter import ClinicalRTFFormatter


class ClinicalTableBuilder:
    """Enhanced table builder for clinical reporting with professional formatting."""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.rtf_formatter = ClinicalRTFFormatter()
        
    def create_demographics_table(self, 
                                 adsl_data: pd.DataFrame,
                                 treatment_var: str = 'TRT01P',
                                 study_title: str = None) -> Dict[str, str]:
        """
        Create a comprehensive demographics table.
        
        Args:
            adsl_data: ADSL dataset
            treatment_var: Treatment variable name
            study_title: Study title for subtitle
            
        Returns:
            Dictionary with table formats (CSV, RTF, HTML, Excel)
        """
        # Prepare demographics summary
        demo_summary = []
        
        # Get treatment groups
        treatments = sorted(adsl_data[treatment_var].unique())
        
        # Age statistics
        age_stats = self._calculate_continuous_stats(adsl_data, 'AGE', treatment_var)
        demo_summary.extend(age_stats)
        
        # Gender distribution
        gender_stats = self._calculate_categorical_stats(adsl_data, 'SEX', treatment_var)
        demo_summary.extend(gender_stats)
        
        # Race distribution
        if 'RACE' in adsl_data.columns:
            race_stats = self._calculate_categorical_stats(adsl_data, 'RACE', treatment_var)
            demo_summary.extend(race_stats)
        
        # Create DataFrame
        df = pd.DataFrame(demo_summary)
        
        # Add footnote markers
        df.loc[df['Parameter'] == 'Age (years)', 'Parameter'] = 'Age (years)ᵃ'
        
        # Generate outputs
        outputs = self._generate_table_outputs(
            df, 
            'demographics_table',
            table_type='demographics',
            study_title=study_title
        )
        
        return outputs
    
    def create_adverse_events_table(self,
                                   adae_data: pd.DataFrame,
                                   adsl_data: pd.DataFrame,
                                   treatment_var: str = 'TRT01P',
                                   study_title: str = None) -> Dict[str, str]:
        """
        Create a comprehensive adverse events table.
        
        Args:
            adae_data: ADAE dataset
            adsl_data: ADSL dataset for population counts
            treatment_var: Treatment variable name
            study_title: Study title for subtitle
            
        Returns:
            Dictionary with table formats
        """
        # Get population counts
        pop_counts = adsl_data[treatment_var].value_counts().sort_index()
        
        # Overall AE summary
        ae_summary = []
        
        # Any AE
        any_ae_stats = self._calculate_ae_incidence(
            adae_data, adsl_data, treatment_var, 
            category="Any Adverse Event"
        )
        ae_summary.extend(any_ae_stats)
        
        # Serious AEs
        if 'AESER' in adae_data.columns:
            serious_ae_stats = self._calculate_ae_incidence(
                adae_data[adae_data['AESER'] == 'Y'], adsl_data, treatment_var,
                category="Any Serious Adverse Event"
            )
            ae_summary.extend(serious_ae_stats)
        
        # AEs by severity
        if 'AESEV' in adae_data.columns:
            for severity in ['MILD', 'MODERATE', 'SEVERE']:
                sev_data = adae_data[adae_data['AESEV'] == severity]
                if not sev_data.empty:
                    sev_stats = self._calculate_ae_incidence(
                        sev_data, adsl_data, treatment_var,
                        category=f"{severity.title()} AEs"
                    )
                    ae_summary.extend(sev_stats)
        
        # Top AEs by System Organ Class
        if 'AESOC' in adae_data.columns:
            top_socs = adae_data['AESOC'].value_counts().head(5).index
            for soc in top_socs:
                soc_data = adae_data[adae_data['AESOC'] == soc]
                soc_stats = self._calculate_ae_incidence(
                    soc_data, adsl_data, treatment_var,
                    category=f"{soc}ᵃ"
                )
                ae_summary.extend(soc_stats)
        
        # Create DataFrame
        df = pd.DataFrame(ae_summary)
        
        # Generate outputs
        outputs = self._generate_table_outputs(
            df,
            'adverse_events_table',
            table_type='ae',
            study_title=study_title
        )
        
        return outputs
    
    def create_laboratory_table(self,
                               lab_data: pd.DataFrame,
                               adsl_data: pd.DataFrame,
                               treatment_var: str = 'TRT01P',
                               param_var: str = 'PARAM',
                               value_var: str = 'AVAL',
                               study_title: str = None) -> Dict[str, str]:
        """
        Create a laboratory values summary table.
        
        Args:
            lab_data: Laboratory dataset (ADLB*)
            adsl_data: ADSL dataset
            treatment_var: Treatment variable name
            param_var: Parameter variable name
            value_var: Analysis value variable name
            study_title: Study title for subtitle
            
        Returns:
            Dictionary with table formats
        """
        lab_summary = []
        
        # Get unique parameters
        parameters = lab_data[param_var].unique()[:10]  # Limit to top 10
        
        for param in parameters:
            param_data = lab_data[lab_data[param_var] == param]
            if not param_data.empty:
                param_stats = self._calculate_continuous_stats(
                    param_data, value_var, treatment_var,
                    parameter_name=param
                )
                lab_summary.extend(param_stats)
        
        # Create DataFrame
        df = pd.DataFrame(lab_summary)
        
        # Add footnote markers
        if not df.empty:
            df.loc[0, 'Parameter'] = df.loc[0, 'Parameter'] + 'ᵃ'
        
        # Generate outputs
        outputs = self._generate_table_outputs(
            df,
            'laboratory_table',
            table_type='lab',
            study_title=study_title
        )
        
        return outputs
    
    def _calculate_continuous_stats(self, 
                                   data: pd.DataFrame,
                                   value_var: str,
                                   treatment_var: str,
                                   parameter_name: str = None) -> List[Dict]:
        """Calculate statistics for continuous variables."""
        if parameter_name is None:
            parameter_name = value_var.replace('_', ' ').title()
        
        treatments = sorted(data[treatment_var].unique())
        stats_rows = []
        
        # N
        n_row = {'Parameter': f'{parameter_name}', 'Statistic': 'N'}
        for trt in treatments:
            trt_data = data[data[treatment_var] == trt][value_var].dropna()
            n_row[trt] = len(trt_data)
        stats_rows.append(n_row)
        
        # Mean (SD)
        mean_row = {'Parameter': '', 'Statistic': 'Mean (SD)'}
        for trt in treatments:
            trt_data = data[data[treatment_var] == trt][value_var].dropna()
            if len(trt_data) > 0:
                mean_val = trt_data.mean()
                sd_val = trt_data.std()
                mean_row[trt] = f"{mean_val:.1f} ({sd_val:.1f})"
            else:
                mean_row[trt] = "0"
        stats_rows.append(mean_row)
        
        # Median (Min, Max)
        median_row = {'Parameter': '', 'Statistic': 'Median (Min, Max)'}
        for trt in treatments:
            trt_data = data[data[treatment_var] == trt][value_var].dropna()
            if len(trt_data) > 0:
                median_val = trt_data.median()
                min_val = trt_data.min()
                max_val = trt_data.max()
                median_row[trt] = f"{median_val:.1f} ({min_val:.1f}, {max_val:.1f})"
            else:
                median_row[trt] = "0"
        stats_rows.append(median_row)
        
        return stats_rows
    
    def _calculate_categorical_stats(self,
                                    data: pd.DataFrame,
                                    cat_var: str,
                                    treatment_var: str) -> List[Dict]:
        """Calculate statistics for categorical variables."""
        treatments = sorted(data[treatment_var].unique())
        stats_rows = []
        
        # Get categories
        categories = sorted(data[cat_var].unique())
        
        for category in categories:
            cat_row = {'Parameter': f'{cat_var.replace("_", " ").title()}', 'Statistic': category}
            
            for trt in treatments:
                trt_data = data[data[treatment_var] == trt]
                total_n = len(trt_data)
                cat_n = len(trt_data[trt_data[cat_var] == category])
                
                if total_n > 0:
                    pct = (cat_n / total_n) * 100
                    cat_row[trt] = f"{cat_n} ({pct:.1f}%)"
                else:
                    cat_row[trt] = "0 (0.0%)"
            
            stats_rows.append(cat_row)
        
        return stats_rows
    
    def _calculate_ae_incidence(self,
                               ae_data: pd.DataFrame,
                               adsl_data: pd.DataFrame,
                               treatment_var: str,
                               category: str) -> List[Dict]:
        """Calculate AE incidence rates."""
        treatments = sorted(adsl_data[treatment_var].unique())
        
        # Get population counts
        pop_counts = adsl_data[treatment_var].value_counts()
        
        # Count subjects with AEs
        ae_counts = ae_data.groupby(treatment_var)['USUBJID'].nunique()
        
        ae_row = {'Parameter': category, 'Statistic': 'n (%)'}
        
        for trt in treatments:
            total_n = pop_counts.get(trt, 0)
            ae_n = ae_counts.get(trt, 0)
            
            if total_n > 0:
                pct = (ae_n / total_n) * 100
                ae_row[trt] = f"{ae_n} ({pct:.1f}%)"
            else:
                ae_row[trt] = "0 (0.0%)"
        
        return [ae_row]
    
    def _generate_table_outputs(self,
                               df: pd.DataFrame,
                               filename: str,
                               table_type: str = 'generic',
                               study_title: str = None) -> Dict[str, str]:
        """Generate multiple output formats for a table."""
        outputs = {}
        
        # CSV output
        csv_path = self.output_dir / f"{filename}.csv"
        df.to_csv(csv_path, index=False)
        outputs['csv'] = str(csv_path)
        
        # Excel output
        excel_path = self.output_dir / f"{filename}.xlsx"
        df.to_excel(excel_path, index=False, sheet_name='Table')
        outputs['xlsx'] = str(excel_path)
        
        # HTML output
        html_path = self.output_dir / f"{filename}.html"
        html_content = self._create_html_table(df, table_type, study_title)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        outputs['html'] = str(html_path)
        
        # Professional RTF output
        rtf_path = self.output_dir / f"{filename}.rtf"
        if table_type == 'demographics':
            rtf_content = self.rtf_formatter.format_demographics_table(df, study_title)
        elif table_type == 'ae':
            rtf_content = self.rtf_formatter.format_ae_table(df, study_title)
        elif table_type == 'lab':
            rtf_content = self.rtf_formatter.format_lab_table(df, study_title)
        else:
            rtf_content = self.rtf_formatter.format_table(df, "Clinical Summary Table", study_title)
        
        with open(rtf_path, 'w', encoding='utf-8') as f:
            f.write(rtf_content)
        outputs['rtf'] = str(rtf_path)
        
        return outputs
    
    def _create_html_table(self, 
                          df: pd.DataFrame, 
                          table_type: str,
                          study_title: str = None) -> str:
        """Create a styled HTML table."""
        if table_type == 'demographics':
            title = "Summary of Demographics and Baseline Characteristics"
        elif table_type == 'ae':
            title = "Summary of Adverse Events"
        elif table_type == 'lab':
            title = "Summary of Laboratory Values"
        else:
            title = "Clinical Summary Table"
        
        subtitle = study_title or "Safety Population"
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{ font-family: 'Times New Roman', serif; margin: 40px; }}
        .table-title {{ text-align: center; font-size: 14pt; font-weight: bold; margin-bottom: 10px; }}
        .table-subtitle {{ text-align: center; font-size: 12pt; margin-bottom: 20px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th {{ background-color: #f5f5f5; border: 1px solid #333; padding: 8px; text-align: center; font-weight: bold; }}
        td {{ border: 1px solid #333; padding: 6px; text-align: center; }}
        .left-align {{ text-align: left; }}
        .footnotes {{ margin-top: 20px; font-size: 10pt; }}
        .footnote {{ margin: 5px 0; }}
    </style>
</head>
<body>
    <div class="table-title">{title}</div>
    <div class="table-subtitle">{subtitle}</div>
    
    {df.to_html(classes='clinical-table', table_id='main-table', escape=False, index=False)}
    
    <div class="footnotes">
        <div class="footnote"><sup>a</sup> Age calculated at date of informed consent.</div>
        <div class="footnote"><sup>b</sup> P-values from appropriate statistical tests.</div>
    </div>
    
    <div style="margin-top: 30px; font-size: 9pt; border-top: 1px solid #333; padding-top: 10px;">
        Generated by py4csr Clinical Reporting System
    </div>
</body>
</html>
"""
        return html_content 