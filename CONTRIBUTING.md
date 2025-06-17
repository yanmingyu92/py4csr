# Contributing to py4csr

Thank you for your interest in contributing to py4csr! This guide will help you get started with contributing to our clinical study reporting package.

## 🎯 How to Contribute

There are many ways to contribute to py4csr:

- **Report bugs** and request features
- **Improve documentation** and examples
- **Submit code** for new features or bug fixes
- **Review pull requests** from other contributors
- **Share your experience** using py4csr in clinical research

## 🚀 Getting Started

### 1. Fork and Clone the Repository

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR-USERNAME/py4csr.git
cd py4csr
```

### 2. Set Up Development Environment

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-number
```

## 🧪 Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/test_functional.py -v
pytest -m "not slow"  # Skip slow tests
pytest -m "real_data"  # Run only real data tests

# Run with coverage
pytest --cov=py4csr --cov-report=html
```

### Code Quality

We use several tools to maintain code quality:

```bash
# Format code with black
black py4csr tests

# Sort imports with isort
isort py4csr tests

# Check code style with flake8
flake8 py4csr tests

# Type checking with mypy
mypy py4csr
```

### Documentation

```bash
# Build documentation locally
cd docs
make html

# View documentation
open _build/html/index.html
```

## 📝 Coding Standards

### Code Style
- Follow **PEP 8** style guidelines
- Use **Black** for code formatting (line length: 88)
- Use **isort** for import sorting
- Add **type hints** for all public functions

### Documentation
- Write **docstrings** for all public functions and classes
- Use **Google-style** docstrings
- Include **examples** in docstrings when helpful
- Update **README.md** and docs for new features

### Testing
- Write **unit tests** for all new functionality
- Include **integration tests** for complex features
- Test with **real clinical data** when applicable
- Aim for **>90% test coverage**

## 🏥 Clinical Research Guidelines

Since py4csr is used in clinical research, please follow these guidelines:

### Data Privacy
- **Never commit real patient data** to the repository
- Use **synthetic or anonymized data** for examples
- Follow **HIPAA and GDPR** guidelines in documentation

### Regulatory Compliance
- Ensure new features support **ICH E3** and **CTD** requirements
- Maintain **CDISC compliance** for data structures
- Document **validation** and **traceability** for statistical functions

### Industry Standards
- Follow **pharmaceutical industry** best practices
- Use **standard terminology** (CDISC, MedDRA, etc.)
- Consider **regulatory submission** requirements

## 🐛 Reporting Issues

### Bug Reports
When reporting bugs, please include:

1. **Python version** and operating system
2. **py4csr version** (`py4csr.__version__`)
3. **Minimal reproducible example**
4. **Expected vs actual behavior**
5. **Error messages** and stack traces

### Feature Requests
For new features, please describe:

1. **Use case** and clinical context
2. **Proposed API** or interface
3. **Examples** of how it would be used
4. **Regulatory considerations** if applicable

## 🔄 Pull Request Process

### Before Submitting
1. **Run all tests** and ensure they pass
2. **Update documentation** for new features
3. **Add tests** for new functionality
4. **Check code quality** with linting tools
5. **Update CHANGELOG.md** with your changes

### Pull Request Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Clinical Context
How does this relate to clinical research?

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Tested with real data (if applicable)

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass locally
```

### Review Process
1. **Automated checks** must pass (CI/CD)
2. **Code review** by maintainers
3. **Testing** with real clinical data (if applicable)
4. **Documentation review**
5. **Merge** after approval

## 🏗️ Development Areas

### High Priority
- **Statistical functions** for clinical endpoints
- **CDISC metadata** integration
- **Performance optimization** for large datasets
- **Regulatory compliance** features

### Medium Priority
- **Interactive dashboards** for clinical data
- **Cloud deployment** templates
- **Additional output formats**
- **Machine learning** integration

### Documentation Needs
- **More examples** with real clinical scenarios
- **Video tutorials** for common workflows
- **Best practices** guides
- **Regulatory submission** templates

## 🤝 Community Guidelines

### Code of Conduct
- Be **respectful** and **inclusive**
- Focus on **constructive feedback**
- Help **newcomers** to clinical research
- Maintain **professional standards**

### Communication
- Use **GitHub Issues** for bug reports and feature requests
- Use **GitHub Discussions** for questions and ideas
- Join our **community calls** (monthly)
- Follow us on **social media** for updates

## 🎓 Learning Resources

### Clinical Research
- [CDISC Standards](https://www.cdisc.org/)
- [ICH Guidelines](https://www.ich.org/)
- [FDA Guidance Documents](https://www.fda.gov/drugs/guidance-compliance-regulatory-information)

### Python Development
- [Python Style Guide (PEP 8)](https://pep8.org/)
- [Type Hints (PEP 484)](https://www.python.org/dev/peps/pep-0484/)
- [Testing with pytest](https://docs.pytest.org/)

### Statistical Computing
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [SciPy Documentation](https://docs.scipy.org/)
- [Clinical Statistics Resources](https://www.appliedclinicaltrialsonline.com/)

## 🏆 Recognition

Contributors will be recognized in:
- **CHANGELOG.md** for each release
- **Contributors section** in README
- **Annual contributor report**
- **Conference presentations** (with permission)

## 📞 Getting Help

If you need help contributing:

1. **Read the documentation** thoroughly
2. **Search existing issues** and discussions
3. **Ask in GitHub Discussions**
4. **Join our community calls**
5. **Email the maintainers**: dev@py4csr.org

## 📄 License

By contributing to py4csr, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping make py4csr better for the clinical research community! 🚀 