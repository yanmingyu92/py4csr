Contributing to py4csr
=======================

Thank you for your interest in contributing to py4csr!

Getting Started
---------------

Development Setup
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/yanmingyu92/py4csr.git
   cd py4csr

   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install in development mode
   pip install -e ".[dev]"

   # Install pre-commit hooks
   pre-commit install

Development Workflow
--------------------

1. Create a Branch
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Create feature branch
   git checkout -b feature/your-feature-name

   # Or bug fix branch
   git checkout -b fix/bug-description

2. Make Changes
~~~~~~~~~~~~~~~

- Write code following the style guide
- Add tests for new functionality
- Update documentation as needed
- Run tests locally

3. Run Tests
~~~~~~~~~~~~

.. code-block:: bash

   # Run all tests
   pytest tests/

   # Run with coverage
   pytest tests/ --cov=py4csr --cov-report=term

   # Run specific test file
   pytest tests/unit/test_clinical_session.py

4. Run Linters
~~~~~~~~~~~~~~

.. code-block:: bash

   # Format code with black
   black py4csr tests

   # Sort imports
   isort py4csr tests

   # Run flake8
   flake8 py4csr tests

   # Run mypy
   mypy py4csr

5. Commit Changes
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Stage changes
   git add .

   # Commit with descriptive message
   git commit -m "Add feature: description of changes"

6. Push and Create PR
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Push to GitHub
   git push origin feature/your-feature-name

   # Create pull request on GitHub

Code Style Guide
----------------

Python Style
~~~~~~~~~~~~

- Follow PEP 8
- Use black for formatting (line length: 100)
- Use type hints for function signatures
- Write docstrings for all public functions

Example:

.. code-block:: python

   def calculate_statistics(
       data: pd.DataFrame,
       variable: str,
       statistics: List[str]
   ) -> Dict[str, float]:
       """Calculate statistics for a variable.

       Args:
           data: Input dataframe
           variable: Variable name to analyze
           statistics: List of statistics to calculate

       Returns:
           Dictionary of statistic names to values

       Raises:
           ValueError: If variable not in data
       """
       if variable not in data.columns:
           raise ValueError(f"Variable {variable} not found")

       results = {}
       for stat in statistics:
           results[stat] = _calculate_stat(data[variable], stat)

       return results

Documentation Style
~~~~~~~~~~~~~~~~~~~

- Use reStructuredText (RST) format
- Include code examples
- Add cross-references to related topics
- Keep examples concise and runnable

Testing Guidelines
------------------

Test Structure
~~~~~~~~~~~~~~

.. code-block:: python

   import pytest
   from py4csr.clinical import ClinicalSession

   class TestClinicalSession:
       """Tests for ClinicalSession class."""

       def test_initialization(self):
           """Test session initialization."""
           session = ClinicalSession(uri="TEST001")
           assert session.uri == "TEST001"

       def test_define_report(self, sample_adsl):
           """Test report definition."""
           session = ClinicalSession(uri="TEST001")
           session.define_report(dataset=sample_adsl, subjid="USUBJID")
           assert session.dataset is not None

Test Coverage
~~~~~~~~~~~~~

- Aim for 80%+ code coverage
- Test both success and failure cases
- Test edge cases and boundary conditions
- Use fixtures for common test data

Pull Request Guidelines
-----------------------

PR Checklist
~~~~~~~~~~~~

Before submitting a pull request:

- [ ] Tests pass locally
- [ ] Code is formatted with black
- [ ] Type hints are added
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated
- [ ] PR description explains changes

PR Description Template
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: markdown

   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Performance improvement

   ## Testing
   - [ ] Unit tests added/updated
   - [ ] Integration tests added/updated
   - [ ] Manual testing performed

   ## Checklist
   - [ ] Code follows style guide
   - [ ] Tests pass
   - [ ] Documentation updated

Code Review Process
-------------------

1. Automated checks run (tests, linters)
2. Maintainer reviews code
3. Address review comments
4. Maintainer approves and merges

Release Process
---------------

See :doc:`releases` for details on the release process.

Questions?
----------

- Open an issue on GitHub
- Contact the development team
- Check existing documentation

Thank you for contributing!

