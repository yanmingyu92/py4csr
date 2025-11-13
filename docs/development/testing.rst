Testing Guide
==============

Comprehensive guide to testing in py4csr.

Test Structure
--------------

Directory Layout
~~~~~~~~~~~~~~~~

.. code-block:: text

   tests/
   ├── unit/                  # Unit tests
   │   ├── test_clinical_session.py
   │   ├── test_statistical_engine.py
   │   └── ...
   ├── integration/           # Integration tests
   │   ├── test_full_workflow.py
   │   └── ...
   ├── fixtures/              # Test fixtures
   │   ├── conftest.py
   │   └── sample_data.py
   └── package/               # Package tests
       └── test_imports.py

Running Tests
-------------

Basic Commands
~~~~~~~~~~~~~~

.. code-block:: bash

   # Run all tests
   pytest tests/

   # Run with coverage
   pytest tests/ --cov=py4csr --cov-report=term

   # Run specific test file
   pytest tests/unit/test_clinical_session.py

   # Run specific test
   pytest tests/unit/test_clinical_session.py::TestClinicalSession::test_initialization

   # Run with verbose output
   pytest tests/ -v

   # Run and stop at first failure
   pytest tests/ -x

Test Markers
~~~~~~~~~~~~

.. code-block:: bash

   # Run only unit tests
   pytest tests/ -m unit

   # Run only integration tests
   pytest tests/ -m integration

   # Skip slow tests
   pytest tests/ -m "not slow"

Writing Tests
-------------

Unit Tests
~~~~~~~~~~

.. code-block:: python

   import pytest
   from py4csr.clinical import ClinicalSession

   class TestClinicalSession:
       """Unit tests for ClinicalSession."""

       def test_initialization(self):
           """Test session initialization."""
           session = ClinicalSession(uri="TEST001")
           assert session.uri == "TEST001"
           assert session.dataset is None

       def test_define_report(self, sample_adsl):
           """Test report definition."""
           session = ClinicalSession(uri="TEST001")
           session.define_report(
               dataset=sample_adsl,
               subjid="USUBJID"
           )
           assert session.dataset is not None
           assert session.subjid == "USUBJID"

Integration Tests
~~~~~~~~~~~~~~~~~

.. code-block:: python

   import pytest
   from py4csr.clinical import ClinicalSession

   @pytest.mark.integration
   class TestFullWorkflow:
       """Integration tests for complete workflows."""

       def test_demographics_table_generation(self, sample_adsl, tmp_path):
           """Test complete demographics table generation."""
           session = ClinicalSession(uri="TEST001")
           session.define_report(dataset=sample_adsl, subjid="USUBJID")
           session.add_trt(name="TRT01PN", decode="TRT01P")
           session.add_var(name="AGE", stats="n mean+sd")
           session.generate()

           output_path = tmp_path / "demographics.rtf"
           session.finalize(output_path=str(output_path), format="rtf")

           assert output_path.exists()
           assert output_path.stat().st_size > 0

Test Fixtures
-------------

Using Fixtures
~~~~~~~~~~~~~~

.. code-block:: python

   import pytest
   import pandas as pd

   @pytest.fixture
   def sample_adsl():
       """Create sample ADSL dataset."""
       return pd.DataFrame({
           'USUBJID': ['001', '002', '003'],
           'AGE': [45, 52, 38],
           'SEX': ['M', 'F', 'M'],
           'TRT01P': ['Placebo', 'Drug', 'Drug'],
           'TRT01PN': [0, 1, 1],
           'SAFFL': ['Y', 'Y', 'Y']
       })

   def test_with_fixture(sample_adsl):
       """Test using fixture."""
       assert len(sample_adsl) == 3
       assert 'USUBJID' in sample_adsl.columns

Parametrized Tests
------------------

Testing Multiple Cases
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import pytest

   @pytest.mark.parametrize("statistic,expected", [
       ("n", 3),
       ("mean", 45.0),
       ("min", 38),
       ("max", 52)
   ])
   def test_statistics(sample_adsl, statistic, expected):
       """Test different statistics."""
       from py4csr.functional import StatisticalTemplates
       templates = StatisticalTemplates()
       result = templates.calculate_continuous_statistics(
           data=sample_adsl['AGE'],
           statistics=[statistic]
       )
       assert result[statistic] == expected

Coverage Reports
----------------

Generate Coverage
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Terminal report
   pytest tests/ --cov=py4csr --cov-report=term

   # HTML report
   pytest tests/ --cov=py4csr --cov-report=html

   # Open HTML report
   open htmlcov/index.html  # On macOS
   start htmlcov/index.html  # On Windows

Coverage Goals
~~~~~~~~~~~~~~

- Overall: 80%+
- Critical modules: 90%+
- New code: 100%

Best Practices
--------------

1. **Test One Thing**

.. code-block:: python

   # Good - tests one behavior
   def test_age_calculation(self):
       result = calculate_age(birthdate, reference_date)
       assert result == expected_age

   # Avoid - tests multiple things
   def test_everything(self):
       # Tests age, sex, race, etc.
       pass

2. **Use Descriptive Names**

.. code-block:: python

   # Good
   def test_session_raises_error_when_dataset_missing(self):
       pass

   # Avoid
   def test_error(self):
       pass

3. **Arrange-Act-Assert**

.. code-block:: python

   def test_calculation(self):
       # Arrange
       data = create_test_data()

       # Act
       result = perform_calculation(data)

       # Assert
       assert result == expected_value

Next Steps
----------

- :doc:`contributing` - Contributing guide
- :doc:`releases` - Release process

