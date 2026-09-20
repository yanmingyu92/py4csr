# Contributing to py4csr

Thank you for your interest in contributing to py4csr — an ARD-first summary
table engine for clinical research reporting in Python.

> **New here?** Start with issues labeled
> [`good first issue`](https://github.com/yanmingyu92/py4csr/labels/good%20first%20issue) —
> each one is written to be self-contained. For the big picture of what the
> project is (and deliberately is not), read [`ARCHITECTURE.md`](ARCHITECTURE.md).
> Design proposals under discussion live in [`docs/design/`](docs/design/) and
> in [GitHub Discussions](https://github.com/yanmingyu92/py4csr/discussions).

## Ways to contribute

- **Report bugs** and request features (open an issue)
- **Improve documentation** and examples
- **Review design docs** — the [ARD schema RFC](docs/design/ard-schema-v0.1.md)
  explicitly asks for critique; a well-argued comment is a full contribution
- **Submit code** for new features or bug fixes
- **Extend the validation harness** — every new comparison against a trusted
  reference makes the engine more credible

## Getting started

### 1. Fork and clone

```bash
git clone https://github.com/YOUR-USERNAME/py4csr.git
cd py4csr
```

### 2. Set up a development environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -e ".[dev]"

pre-commit install
```

### 3. Create a branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-number
```

## Development workflow

### Running tests

```bash
# All tests
pytest

# Unit tests only (fastest loop while developing)
pytest tests/unit -v

# Skip slow tests
pytest -m "not slow"

# Only tests requiring real clinical data
pytest -m "real_data"

# With coverage
pytest --cov=py4csr --cov-report=html
```

Test layout: `tests/unit/`, `tests/integration/`, plus top-level
`tests/test_real_data.py` for optional real-data runs.

### Code quality

Pre-commit runs the full suite automatically:

```bash
pre-commit run --all-files
```

This covers: **black** (formatting, line length 88), **isort**, **flake8**,
**mypy**, **bandit** (security), and **interrogate** (docstring coverage ≥ 80%).

### Documentation

Docs are Sphinx-based:

```bash
sphinx-build -M html docs docs/_build
```

## Coding standards

### Code style
- Follow **PEP 8**; formatting is enforced by **black** (line length 88)
- Imports sorted by **isort** (black profile)
- Add **type hints** for all public functions

### Documentation
- **Google-style** docstrings for all public functions and classes
- Include a minimal runnable **example** in docstrings when helpful
- Update **README.md** / docs for new features

### Testing
- Write **unit tests** for all new functionality (`tests/unit/`)
- Include **integration tests** for complex features (`tests/integration/`)
- Use **synthetic data** for examples and tests (never real patient data)
- Keep the suite green: `pytest` before every push

## Clinical research guidelines

Because py4csr serves clinical research:

### Data privacy
- **Never commit real patient data**
- Use **synthetic or fully anonymized** data in all examples and tests
- Follow HIPAA/GDPR principles in anything you publish

### Statistical definitions
- Default statistical definitions follow the references the field already
  trusts (gtsummary / SAS conventions). See
  [validation/gtsummary_comparison.md](validation/gtsummary_comparison.md)
  for what that means in practice, and the [ARD schema](docs/design/ard-schema-v0.1.md)
  for the output contract.
- If a change alters a computed number, it must be reflected in the
  validation harness, not just the docs.

## Reporting issues

### Bug reports
Please include:

1. Python version and operating system
2. py4csr version (`py4csr.__version__`)
3. Minimal reproducible example (synthetic data)
4. Expected vs. actual behavior
5. Error messages / stack traces

### Design discussions
Bigger ideas (schema changes, new backends, API changes) belong in
[GitHub Discussions](https://github.com/yanmingyu92/py4csr/discussions) —
ideally as a comment on an open RFC — so they are visible before any code
exists.

## Pull request process

### Before submitting
1. Run all tests and ensure they pass
2. Run `pre-commit run --all-files`
3. Update documentation for user-facing changes
4. Add tests for new functionality
5. Update `CHANGELOG.md`

### Pull request template
```markdown
## Description
Brief description of changes

## Type of change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Validation harness extension

## Clinical context
How does this relate to clinical reporting?

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated (if applicable)

## Checklist
- [ ] Code follows style guidelines (pre-commit passes)
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass locally
```

### Review
1. Automated checks must pass
2. Maintainer review
3. Merge after approval

## Current development areas

(See the [public roadmap](https://github.com/users/yanmingyu92/projects/1)
for the live version.)

### High priority
- **Table engine hardening** — edge cases and docs for `tbl_summary()`
- **ARD schema v0.2** — driven by the [RFC](docs/design/ard-schema-v0.1.md)
- **Rendering backends** — great_tables (HTML/Word) and rtflite (RTF)
  integration
- **Validation extensions** — new datasets and comparison targets

### Welcome contributions
- Examples and notebooks (AE tables, shift tables)
- Windows/macOS setup walkthroughs
- Schema critique and naming review
- Synthetic data generators

## Code of conduct

This project follows the [Code of Conduct](CODE_OF_CONDUCT.md). By
participating, you agree to uphold it.

## Getting help

1. Read the [documentation](https://github.com/yanmingyu92/py4csr/tree/main/docs)
2. Search existing issues
3. Open a new issue (bugs) or discussion (questions/ideas)

## License

By contributing, you agree that your contributions will be licensed under the
MIT License.
