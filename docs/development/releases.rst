Release Process
================

Guide for releasing new versions of py4csr.

Version Numbering
-----------------

py4csr follows Semantic Versioning (SemVer):

- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

Release Checklist
-----------------

Pre-Release
~~~~~~~~~~~

1. **Update Version Number**

.. code-block:: bash

   # Update version in pyproject.toml
   version = "0.2.0"

   # Update version in py4csr/__init__.py
   __version__ = "0.2.0"

2. **Update CHANGELOG.md**

.. code-block:: markdown

   ## [0.2.0] - 2025-10-29

   ### Added
   - New feature X
   - New feature Y

   ### Changed
   - Improved performance of Z

   ### Fixed
   - Bug fix for issue #123

3. **Run Full Test Suite**

.. code-block:: bash

   pytest tests/ --cov=py4csr --cov-report=term

4. **Build Documentation**

.. code-block:: bash

   cd docs
   sphinx-build -b html . _build/html

5. **Create Git Tag**

.. code-block:: bash

   git tag -a v0.2.0 -m "Release version 0.2.0"
   git push origin v0.2.0

Release to PyPI
~~~~~~~~~~~~~~~

1. **Build Distribution**

.. code-block:: bash

   # Clean previous builds
   rm -rf dist/ build/ *.egg-info

   # Build wheel and source distribution
   python -m build

2. **Upload to TestPyPI**

.. code-block:: bash

   # Upload to test repository
   python -m twine upload --repository testpypi dist/*

   # Test installation
   pip install --index-url https://test.pypi.org/simple/ py4csr

3. **Upload to PyPI**

.. code-block:: bash

   # Upload to production
   python -m twine upload dist/*

Post-Release
~~~~~~~~~~~~

1. **Create GitHub Release**

- Go to GitHub releases page
- Create new release from tag
- Add release notes from CHANGELOG
- Attach distribution files

2. **Announce Release**

- Update README badges
- Post announcement
- Update documentation

Hotfix Process
--------------

For urgent bug fixes:

1. Create hotfix branch from main
2. Fix bug and add tests
3. Update version (patch number)
4. Follow release process
5. Merge back to main and develop

Next Steps
----------

- :doc:`contributing` - Contributing guide
- :doc:`testing` - Testing guide

