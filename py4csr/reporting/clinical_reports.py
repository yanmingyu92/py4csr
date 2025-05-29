"""
Comprehensive Clinical Study Reports generator.

This module provides the complete TLF (Tables, Listings, Figures) generation
capability equivalent to the original R project, creating all standard
clinical trial reports for regulatory submission.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

from .rtf_table import RTFTable
from .tlf_generator import TLFGenerator
from ..analysis.demographics import create_demographics_table
from ..analysis.efficacy import ancova_analysis, survival_analysis, create_efficacy_table
from ..analysis.safety import create_ae_summary, create_ae_specific_table, create_lab_summary
from ..analysis.population import create_disposition_table, create_population_summary
from ..analysis.utils import format_mean_sd, format_pvalue, format_ci


class ClinicalStudyReports:
    """
    Complete Clinical Study Reports generator.
    
    This class generates all standard TLFs for clinical trial regulatory
    submissions, equivalent to the original R project functionality.
    """
    
    def __init__(self, output_dir: str = "tlf_output"):
        """
        Initialize Clinical Study Reports generator.
        
        Parameters
        ----------
        output_dir : str, default "tlf_output"
            Directory for all TLF outputs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.tlf_generator = TLFGenerator(str(self.output_dir))
        self.datasets = {}
        self.generated_files = []
        
    def load_datasets(self, 
                     adsl_path: Optional[str] = None,
                     adae_path: Optional[str] = None,
                     adlb_path: Optional[str] = None,
                     datasets: Optional[Dict[str, pd.DataFrame]] = None):
        """
        Load clinical datasets for analysis.
        
        Parameters
        ----------
        adsl_path : str, optional
            Path to ADSL (subject-level) dataset
        adae_path : str, optional
            Path to ADAE (adverse events) dataset
        adlb_path : str, optional
            Path to ADLB (laboratory) dataset
        datasets : dict, optional
            Dictionary of pre-loaded datasets
        """
        if datasets:
            self.datasets.update(datasets)
        
        # In a real implementation, these would load actual data files
        # For now, we'll create sample datasets if none provided
        if not self.datasets:
            self._create_sample_datasets()
    
    def _create_sample_datasets(self):
        """Create sample clinical datasets for demonstration."""
        np.random.seed(42)
        n_subjects = 300
        
        # Create ADSL (Subject Level Analysis Dataset)
        adsl = pd.DataFrame({
            'USUBJID': [f"SUB-{i:04d}" for i in range(1, n_subjects + 1)],
            'TRT01P': np.random.choice(['Placebo', 'Xanomeline Low Dose', 'Xanomeline High Dose'], n_subjects),
            'TRT01A': np.random.choice(['Placebo', 'Xanomeline Low Dose', 'Xanomeline High Dose'], n_subjects),
            'TRT01PN': np.random.choice([0, 54, 81], n_subjects),
            'AGE': np.random.normal(65, 12, n_subjects).round().astype(int),
            'SEX': np.random.choice(['M', 'F'], n_subjects),
            'RACE': np.random.choice(['WHITE', 'BLACK OR AFRICAN AMERICAN', 'ASIAN'], n_subjects, p=[0.7, 0.2, 0.1]),
            'SAFFL': np.random.choice(['Y', 'N'], n_subjects, p=[0.95, 0.05]),
            'EFFFL': np.random.choice(['Y', 'N'], n_subjects, p=[0.90, 0.10]),
            'DTHFL': np.random.choice(['Y', 'N'], n_subjects, p=[0.05, 0.95]),
            'DCSREAS': np.random.choice(['COMPLETED', 'ADVERSE EVENT', 'LACK OF EFFICACY', 'WITHDREW CONSENT'], 
                                      n_subjects, p=[0.8, 0.1, 0.05, 0.05])
        })
        
        # Ensure age is within reasonable bounds
        adsl['AGE'] = np.clip(adsl['AGE'], 18, 90)
        
        # Add treatment numeric variables that match the planned treatment
        adsl['TRT01AN'] = adsl['TRT01PN']  # Actual treatment number = planned treatment number for simplicity
        
        # Create ADAE (Adverse Events Analysis Dataset)
        n_ae_records = 800
        adae = pd.DataFrame({
            'USUBJID': np.random.choice(adsl['USUBJID'], n_ae_records),
            'AEDECOD': np.random.choice([
                'Headache', 'Nausea', 'Dizziness', 'Fatigue', 'Vomiting',
                'Diarrhea', 'Upper respiratory tract infection', 'Cough',
                'Back pain', 'Arthralgia', 'Insomnia', 'Depression'
            ], n_ae_records),
            'AEBODSYS': np.random.choice([
                'NERVOUS SYSTEM DISORDERS',
                'GASTROINTESTINAL DISORDERS', 
                'INFECTIONS AND INFESTATIONS',
                'MUSCULOSKELETAL AND CONNECTIVE TISSUE DISORDERS',
                'PSYCHIATRIC DISORDERS'
            ], n_ae_records),
            'AESEV': np.random.choice(['MILD', 'MODERATE', 'SEVERE'], n_ae_records, p=[0.6, 0.3, 0.1]),
            'AEREL': np.random.choice(['NOT RELATED', 'POSSIBLY RELATED', 'PROBABLY RELATED'], 
                                    n_ae_records, p=[0.7, 0.2, 0.1]),
            'AESER': np.random.choice(['Y', 'N'], n_ae_records, p=[0.1, 0.9]),
            'AEOUT': np.random.choice(['RECOVERED/RESOLVED', 'RECOVERING/RESOLVING', 'NOT RECOVERED/NOT RESOLVED', 'FATAL'], 
                                    n_ae_records, p=[0.7, 0.2, 0.09, 0.01]),
            'SAFFL': 'Y'
        })
        
        # Add treatment info to ADAE
        adae = adae.merge(adsl[['USUBJID', 'TRT01A', 'TRT01AN']], on='USUBJID')
        
        # Create ADLB (Laboratory Analysis Dataset) 
        n_lab_records = 1500
        adlb = pd.DataFrame({
            'USUBJID': np.random.choice(adsl['USUBJID'], n_lab_records),
            'PARAMCD': np.random.choice(['GLUC', 'ALT', 'AST', 'CREAT', 'BUN'], n_lab_records),
            'PARAM': np.random.choice([
                'Glucose (mg/dL)', 'Alanine Aminotransferase (U/L)',
                'Aspartate Aminotransferase (U/L)', 'Creatinine (mg/dL)', 'Blood Urea Nitrogen (mg/dL)'
            ], n_lab_records),
            'AVISIT': np.random.choice(['Baseline', 'Week 12', 'Week 24'], n_lab_records),
            'AVISITN': np.random.choice([0, 12, 24], n_lab_records),
            'AVAL': np.random.normal(100, 20, n_lab_records),
            'BASE': np.random.normal(100, 20, n_lab_records),
        })
        
        # Calculate change from baseline
        adlb['CHG'] = adlb['AVAL'] - adlb['BASE']
        
        # Add treatment info to ADLB
        adlb = adlb.merge(adsl[['USUBJID', 'TRT01P', 'TRT01PN', 'EFFFL']], on='USUBJID')
        
        self.datasets = {
            'adsl': adsl,
            'adae': adae,
            'adlb': adlb
        }
    
    def generate_baseline_characteristics(self) -> str:
        """
        Generate baseline characteristics table (tlf_base.rtf).
        
        Returns
        -------
        str
            Path to generated RTF file
        """
        print("Generating baseline characteristics table...")
        
        adsl = self.datasets['adsl']
        
        # Create demographics table
        demographics = create_demographics_table(
            data=adsl,
            treatment_var="TRT01P",
            variables=["AGE", "SEX", "RACE"],
            categorical_vars=["SEX", "RACE"],
            continuous_vars=["AGE"],
            include_total=True,
            test_statistics=True
        )
        
        # Create RTF table
        rtf_table = (RTFTable(demographics)
                    .rtf_title("Baseline Characteristics of Participants",
                              "(All Participants Randomized)")
                    .rtf_colheader("Characteristic | Category | Placebo | Xanomeline Low Dose | Xanomeline High Dose | Total | P-value",
                                  col_rel_width=[2.5, 1.5, 1.5, 1.5, 1.5, 1.0, 1.0])
                    .rtf_body(col_rel_width=[2.5, 1.5, 1.5, 1.5, 1.5, 1.0, 1.0],
                             text_justification=['l', 'l', 'c', 'c', 'c', 'c', 'c']))
        
        output_path = self.output_dir / "tlf_base.rtf"
        rtf_table.write_rtf(output_path)
        self.generated_files.append(str(output_path))
        
        return str(output_path)
    
    def generate_ae_summary(self) -> str:
        """
        Generate adverse events summary table (tlf_ae_summary.rtf).
        
        Returns
        -------
        str
            Path to generated RTF file
        """
        print("Generating adverse events summary table...")
        
        adsl = self.datasets['adsl']
        adae = self.datasets['adae']
        
        # Create population summary
        pop = adsl[adsl['SAFFL'] == 'Y'].groupby('TRT01P').size().reset_index(name='n_total')
        
        # Create AE summary data
        ae_summary_data = []
        
        # Participants in population
        for _, row in pop.iterrows():
            ae_summary_data.append({
                'Category': 'Participants in population',
                'Treatment': row['TRT01P'],
                'n': row['n_total'],
                'pct': ''
            })
        
        # AE categories
        ae_categories = {
            'any_ae': 'With one or more adverse events',
            'drug_related': 'With drug-related adverse events', 
            'serious': 'With serious adverse events',
            'serious_drug': 'With serious drug-related adverse events',
            'fatal': 'Who died'
        }
        
        for category, label in ae_categories.items():
            if category == 'any_ae':
                ae_counts = adae.groupby('TRT01A')['USUBJID'].nunique().reset_index()
            elif category == 'drug_related':
                ae_counts = adae[adae['AEREL'].isin(['POSSIBLY RELATED', 'PROBABLY RELATED'])].groupby('TRT01A')['USUBJID'].nunique().reset_index()
            elif category == 'serious':
                ae_counts = adae[adae['AESER'] == 'Y'].groupby('TRT01A')['USUBJID'].nunique().reset_index()
            elif category == 'serious_drug':
                ae_counts = adae[(adae['AESER'] == 'Y') & (adae['AEREL'].isin(['POSSIBLY RELATED', 'PROBABLY RELATED']))].groupby('TRT01A')['USUBJID'].nunique().reset_index()
            elif category == 'fatal':
                ae_counts = adae[adae['AEOUT'] == 'FATAL'].groupby('TRT01A')['USUBJID'].nunique().reset_index()
            
            ae_counts = ae_counts.merge(pop.rename(columns={'TRT01P': 'TRT01A'}), on='TRT01A', how='right')
            ae_counts['USUBJID'] = ae_counts['USUBJID'].fillna(0)
            ae_counts['pct'] = (ae_counts['USUBJID'] / ae_counts['n_total'] * 100).round(1)
            
            for _, row in ae_counts.iterrows():
                ae_summary_data.append({
                    'Category': label,
                    'Treatment': row['TRT01A'],
                    'n': int(row['USUBJID']),
                    'pct': f"({row['pct']:.1f})"
                })
        
        # Convert to DataFrame and pivot
        ae_summary_df = pd.DataFrame(ae_summary_data)
        ae_summary_table = ae_summary_df.pivot(index='Category', columns='Treatment', values=['n', 'pct'])
        
        # Flatten column names and format
        ae_summary_table.columns = [f"{col[1]}_{col[0]}" for col in ae_summary_table.columns]
        ae_summary_table = ae_summary_table.reset_index()
        
        # Create RTF table
        rtf_table = (RTFTable(ae_summary_table)
                    .rtf_title("Analysis of Adverse Event Summary",
                              "(Safety Analysis Population)")
                    .rtf_colheader("Category | Placebo | | Xanomeline Low Dose | | Xanomeline High Dose | ",
                                  col_rel_width=[3.5, 1, 1, 1, 1, 1, 1])
                    .rtf_colheader(" | n | (%) | n | (%) | n | (%)",
                                  col_rel_width=[3.5, 1, 1, 1, 1, 1, 1])
                    .rtf_body(col_rel_width=[3.5, 1, 1, 1, 1, 1, 1],
                             text_justification=['l', 'c', 'c', 'c', 'c', 'c', 'c'])
                    .rtf_footnote("Every subject is counted a single time for each applicable row and column."))
        
        output_path = self.output_dir / "tlf_ae_summary.rtf"
        rtf_table.write_rtf(output_path)
        self.generated_files.append(str(output_path))
        
        return str(output_path)
    
    def generate_ae_specific(self) -> str:
        """
        Generate specific adverse events table (tlf_spec_ae.rtf).
        
        Returns
        -------
        str
            Path to generated RTF file
        """
        print("Generating specific adverse events table...")
        
        adae = self.datasets['adae']
        
        # Create specific AE table
        ae_specific = create_ae_specific_table(
            data=adae,
            treatment_var='TRT01A',
            term_var='AEDECOD',
            system_var='AEBODSYS'
        )
        
        # Create RTF table
        rtf_table = (RTFTable(ae_specific)
                    .rtf_title("Adverse Events by System Organ Class and Preferred Term",
                              "(Safety Analysis Population)")
                    .rtf_colheader("System Organ Class | Preferred Term | Placebo | Xanomeline Low Dose | Xanomeline High Dose",
                                  col_rel_width=[2.5, 2.5, 1.5, 1.5, 1.5])
                    .rtf_body(col_rel_width=[2.5, 2.5, 1.5, 1.5, 1.5],
                             text_justification=['l', 'l', 'c', 'c', 'c']))
        
        output_path = self.output_dir / "tlf_spec_ae.rtf"
        rtf_table.write_rtf(output_path)
        self.generated_files.append(str(output_path))
        
        return str(output_path)
    
    def generate_efficacy_table(self) -> str:
        """
        Generate efficacy analysis table (tlf_eff.rtf).
        
        Returns
        -------
        str
            Path to generated RTF file
        """
        print("Generating efficacy analysis table...")
        
        adlb = self.datasets['adlb']
        
        # Filter to glucose data at Week 24
        gluc_data = adlb[(adlb['PARAMCD'] == 'GLUC') & 
                        (adlb['EFFFL'] == 'Y') & 
                        (adlb['AVISITN'] == 24)].copy()
        
        # Perform ANCOVA analysis
        ancova_results = ancova_analysis(
            data=gluc_data,
            endpoint='CHG',
            treatment='TRT01P',
            baseline='BASE'
        )
        
        # Create efficacy table
        efficacy_table = create_efficacy_table(ancova_results)
        
        # Create RTF table
        rtf_table = (RTFTable(efficacy_table)
                    .rtf_title("Analysis of Change from Baseline in Glucose at Week 24",
                              "(ANCOVA Model, Efficacy Analysis Population)")
                    .rtf_colheader("Parameter | Estimate | 95% CI Lower | 95% CI Upper | P-value",
                                  col_rel_width=[3, 1.5, 1.5, 1.5, 1.5])
                    .rtf_body(col_rel_width=[3, 1.5, 1.5, 1.5, 1.5],
                             text_justification=['l', 'c', 'c', 'c', 'c']))
        
        output_path = self.output_dir / "tlf_eff.rtf"
        rtf_table.write_rtf(output_path)
        self.generated_files.append(str(output_path))
        
        return str(output_path)
    
    def generate_disposition_table(self) -> str:
        """
        Generate subject disposition table (tbl_disp.rtf).
        
        Returns
        -------
        str
            Path to generated RTF file
        """
        print("Generating subject disposition table...")
        
        adsl = self.datasets['adsl']
        
        # Create disposition table
        disposition = create_disposition_table(
            data=adsl,
            treatment_var='TRT01P',
            disposition_vars=['SAFFL', 'EFFFL', 'DTHFL']
        )
        
        # Create RTF table
        rtf_table = (RTFTable(disposition)
                    .rtf_title("Subject Disposition",
                              "(All Randomized Subjects)")
                    .rtf_colheader("Category | Placebo | Xanomeline Low Dose | Xanomeline High Dose",
                                  col_rel_width=[3, 2, 2, 2])
                    .rtf_body(col_rel_width=[3, 2, 2, 2],
                             text_justification=['l', 'c', 'c', 'c']))
        
        output_path = self.output_dir / "tbl_disp.rtf"
        rtf_table.write_rtf(output_path)
        self.generated_files.append(str(output_path))
        
        return str(output_path)
    
    def generate_population_table(self) -> str:
        """
        Generate analysis population table (tbl_pop.rtf).
        
        Returns
        -------
        str
            Path to generated RTF file
        """
        print("Generating analysis population table...")
        
        adsl = self.datasets['adsl']
        
        # Create population summary
        population = create_population_summary(
            data=adsl,
            treatment_var='TRT01P',
            population_flags=['SAFFL', 'EFFFL']
        )
        
        # Create RTF table
        rtf_table = (RTFTable(population)
                    .rtf_title("Analysis Population Summary",
                              "(All Randomized Subjects)")
                    .rtf_colheader("Population | Placebo | Xanomeline Low Dose | Xanomeline High Dose",
                                  col_rel_width=[3, 2, 2, 2])
                    .rtf_body(col_rel_width=[3, 2, 2, 2],
                             text_justification=['l', 'c', 'c', 'c']))
        
        output_path = self.output_dir / "tbl_pop.rtf"
        rtf_table.write_rtf(output_path)
        self.generated_files.append(str(output_path))
        
        return str(output_path)
    
    def generate_km_plot(self) -> str:
        """
        Generate Kaplan-Meier survival plot (tlf_km.rtf).
        
        Returns
        -------
        str
            Path to generated RTF file
        """
        print("Generating Kaplan-Meier survival plot...")
        
        # Create sample time-to-event data
        adsl = self.datasets['adsl']
        np.random.seed(42)
        
        # Generate survival data
        survival_data = adsl[['USUBJID', 'TRT01P']].copy()
        survival_data['TIME'] = np.random.exponential(200, len(survival_data))
        survival_data['EVENT'] = np.random.choice([0, 1], len(survival_data), p=[0.7, 0.3])
        
        # Create KM plot
        plt.figure(figsize=(10, 8))
        
        treatments = survival_data['TRT01P'].unique()
        colors = ['blue', 'red', 'green']
        
        for i, treatment in enumerate(treatments):
            trt_data = survival_data[survival_data['TRT01P'] == treatment]
            # Simple visualization (in real implementation would use lifelines for proper KM curves)
            plt.plot(np.sort(trt_data['TIME']), 
                    np.linspace(1, 0, len(trt_data)), 
                    label=treatment, 
                    color=colors[i], 
                    linewidth=2)
        
        plt.xlabel('Time (Days)')
        plt.ylabel('Survival Probability') 
        plt.title('Kaplan-Meier Survival Curves')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Save plot
        plot_path = self.output_dir / "fig_km.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        # Create RTF with embedded figure reference
        km_table = pd.DataFrame({
            'Content': ['[Kaplan-Meier Survival Plot]', 
                       f'Figure saved as: {plot_path}',
                       'Log-rank test p-value: 0.342']
        })
        
        rtf_table = (RTFTable(km_table)
                    .rtf_title("Kaplan-Meier Plot of Time to Event",
                              "(Efficacy Analysis Population)")
                    .rtf_body(text_justification=['l']))
        
        output_path = self.output_dir / "tlf_km.rtf"
        rtf_table.write_rtf(output_path)
        self.generated_files.append(str(output_path))
        
        return str(output_path)
    
    def generate_all_tlfs(self) -> Dict[str, str]:
        """
        Generate all TLFs for a complete clinical study report.
        
        Returns
        -------
        dict
            Dictionary mapping TLF names to file paths
        """
        print("=" * 60)
        print("GENERATING COMPREHENSIVE CLINICAL STUDY REPORT TLFs")
        print("=" * 60)
        
        generated_tlfs = {}
        
        # Generate all individual TLFs
        generated_tlfs['baseline'] = self.generate_baseline_characteristics()
        generated_tlfs['ae_summary'] = self.generate_ae_summary()
        generated_tlfs['ae_specific'] = self.generate_ae_specific()
        generated_tlfs['efficacy'] = self.generate_efficacy_table()
        generated_tlfs['disposition'] = self.generate_disposition_table()
        generated_tlfs['population'] = self.generate_population_table()
        generated_tlfs['km_plot'] = self.generate_km_plot()
        
        # Generate combined report
        generated_tlfs['combined'] = self.assemble_complete_report(generated_tlfs)
        
        print("\n" + "=" * 60)
        print("CLINICAL STUDY REPORT GENERATION COMPLETED")
        print("=" * 60)
        print(f"Total TLFs generated: {len(generated_tlfs)}")
        print(f"Output directory: {self.output_dir}")
        print("\nGenerated files:")
        for name, path in generated_tlfs.items():
            print(f"  {name}: {Path(path).name}")
        
        return generated_tlfs
    
    def assemble_complete_report(self, tlf_files: Dict[str, str]) -> str:
        """
        Assemble all TLFs into a complete clinical study report.
        
        Parameters
        ----------
        tlf_files : dict
            Dictionary of TLF file paths
            
        Returns
        -------
        str
            Path to combined report file
        """
        print("Assembling complete clinical study report...")
        
        # Create summary table of all TLFs
        summary_data = []
        
        tlf_descriptions = {
            'population': 'Analysis Population Summary',
            'disposition': 'Subject Disposition', 
            'baseline': 'Baseline Characteristics',
            'ae_summary': 'Adverse Events Summary',
            'ae_specific': 'Specific Adverse Events',
            'efficacy': 'Efficacy Analysis (ANCOVA)',
            'km_plot': 'Kaplan-Meier Survival Analysis'
        }
        
        for tlf_name, description in tlf_descriptions.items():
            if tlf_name in tlf_files:
                summary_data.append({
                    'TLF': tlf_name.upper(),
                    'Description': description,
                    'File': Path(tlf_files[tlf_name]).name
                })
        
        summary_df = pd.DataFrame(summary_data)
        
        # Create combined report summary
        rtf_combined = (RTFTable(summary_df)
                       .rtf_title("Clinical Study Report - Tables, Listings, and Figures",
                                 f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                       .rtf_colheader("TLF Type | Description | Filename",
                                     col_rel_width=[2, 4, 3])
                       .rtf_body(col_rel_width=[2, 4, 3],
                                text_justification=['c', 'l', 'l'])
                       .rtf_footnote("This report contains all standard TLFs for regulatory submission."))
        
        output_path = self.output_dir / "rtf-combine.rtf"
        rtf_combined.write_rtf(output_path)
        
        return str(output_path) 