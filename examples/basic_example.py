#!/usr/bin/env python3
"""
Basic py4csr Example

This example demonstrates the basic functionality of py4csr for clinical study reporting.
It shows how to create a simple clinical report using the functional programming approach.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add py4csr to path (for development)
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from py4csr.functional import ReportSession, FunctionalConfig
    print("✓ py4csr imported successfully")
except ImportError as e:
    print(f"✗ Error importing py4csr: {e}")
    print("Please install py4csr: pip install py4csr")
    sys.exit(1)


def create_sample_data():
    """Create sample clinical trial data for demonstration."""
    print("\n📊 Creating sample clinical trial data...")
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Sample ADSL (Subject-Level Analysis Dataset)
    n_subjects = 100
    
    adsl = pd.DataFrame({
        'USUBJID': [f'SUBJ-{i:03d}' for i in range(1, n_subjects + 1)],
        'STUDYID': 'DEMO-001',
        'TRT01P': np.random.choice(['Placebo', 'Treatment A', 'Treatment B'], n_subjects),
        'TRT01PN': np.random.choice([0, 1, 2], n_subjects),
        'AGE': np.random.normal(65, 12, n_subjects).round().astype(int),
        'SEX': np.random.choice(['M', 'F'], n_subjects),
        'RACE': np.random.choice(['WHITE', 'BLACK', 'ASIAN', 'OTHER'], n_subjects, 
                                p=[0.7, 0.15, 0.1, 0.05]),
        'SAFFL': 'Y',  # All subjects in safety population
        'EFFFL': np.random.choice(['Y', 'N'], n_subjects, p=[0.9, 0.1])
    })
    
    # Sample ADAE (Adverse Events Analysis Dataset)
    n_aes = 150
    
    adae = pd.DataFrame({
        'USUBJID': np.random.choice(adsl['USUBJID'], n_aes),
        'STUDYID': 'DEMO-001',
        'AEBODSYS': np.random.choice([
            'GENERAL DISORDERS', 'GASTROINTESTINAL DISORDERS',
            'NERVOUS SYSTEM DISORDERS', 'SKIN DISORDERS'
        ], n_aes),
        'AEDECOD': np.random.choice([
            'Headache', 'Nausea', 'Fatigue', 'Dizziness', 'Rash'
        ], n_aes),
        'AESEV': np.random.choice(['MILD', 'MODERATE', 'SEVERE'], n_aes, p=[0.6, 0.3, 0.1]),
        'AESER': np.random.choice(['Y', 'N'], n_aes, p=[0.05, 0.95]),
        'SAFFL': 'Y'
    })
    
    # Add treatment information to ADAE
    adae = adae.merge(adsl[['USUBJID', 'TRT01P', 'TRT01PN']], on='USUBJID')
    
    print(f"  ✓ Created ADSL with {len(adsl)} subjects")
    print(f"  ✓ Created ADAE with {len(adae)} adverse events")
    
    return {'ADSL': adsl, 'ADAE': adae}


def run_basic_example():
    """Run a basic py4csr example."""
    print("\n🚀 Running Basic py4csr Example")
    print("=" * 50)
    
    # Create sample data
    datasets = create_sample_data()
    
    # Initialize configuration
    print("\n⚙️ Initializing py4csr configuration...")
    config = FunctionalConfig()
    
    # Create report session
    print("\n📋 Creating report session...")
    try:
        session = ReportSession(config)
        print("  ✓ Report session created successfully")
    except Exception as e:
        print(f"  ✗ Error creating session: {e}")
        return
    
    # Initialize study
    print("\n🏥 Initializing clinical study...")
    try:
        session = session.init_study(
            uri="DEMO-001",
            title="py4csr Basic Example Study",
            protocol="DEMO-PROTOCOL-001"
        )
        print("  ✓ Study initialized successfully")
    except Exception as e:
        print(f"  ✗ Error initializing study: {e}")
        return
    
    # Load datasets
    print("\n📂 Loading datasets...")
    try:
        session = session.load_datasets(datasets=datasets)
        print("  ✓ Datasets loaded successfully")
    except Exception as e:
        print(f"  ✗ Error loading datasets: {e}")
        return
    
    # Define populations
    print("\n👥 Defining analysis populations...")
    try:
        session = session.define_populations(
            safety="SAFFL == 'Y'",
            efficacy="EFFFL == 'Y'"
        )
        print("  ✓ Populations defined successfully")
    except Exception as e:
        print(f"  ✗ Error defining populations: {e}")
        return
    
    # Define treatments
    print("\n💊 Defining treatments...")
    try:
        session = session.define_treatments(var='TRT01P')
        print("  ✓ Treatments defined successfully")
    except Exception as e:
        print(f"  ✗ Error defining treatments: {e}")
        return
    
    # Add tables
    print("\n📊 Adding clinical tables...")
    try:
        session = (session
            .add_demographics_table()
            .add_ae_summary()
        )
        print("  ✓ Tables added successfully")
    except Exception as e:
        print(f"  ✗ Error adding tables: {e}")
        return
    
    # Generate outputs
    print("\n📄 Generating outputs...")
    try:
        output_dir = Path("example_output")
        output_dir.mkdir(exist_ok=True)
        
        session = session.generate_all(output_dir=str(output_dir))
        print(f"  ✓ Outputs generated in {output_dir}")
    except Exception as e:
        print(f"  ✗ Error generating outputs: {e}")
        return
    
    # Finalize session
    print("\n✅ Finalizing session...")
    try:
        result = session.finalize()
        print(f"  ✓ Session finalized successfully")
        print(f"  📁 Generated files: {getattr(result, 'generated_files', 'N/A')}")
    except Exception as e:
        print(f"  ✗ Error finalizing session: {e}")
        return
    
    print("\n🎉 Basic example completed successfully!")
    print(f"Check the '{output_dir}' directory for generated reports.")


def main():
    """Main function."""
    print("py4csr Basic Example")
    print("=" * 30)
    print("This example demonstrates basic py4csr functionality")
    print("for clinical study reporting.\n")
    
    try:
        run_basic_example()
    except KeyboardInterrupt:
        print("\n\n⚠️ Example interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nFor more examples and documentation, visit:")
    print("https://py4csr.readthedocs.io")


if __name__ == "__main__":
    main() 