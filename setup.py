"""
Setup configuration for py4csr package.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="py4csr",
    version="0.1.0",
    author="py4csr Contributors",
    author_email="info@py4csr.com",
    description="Python for Clinical Study Reporting - Professional clinical trial reporting package",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/py4csr",
    project_urls={
        "Bug Tracker": "https://github.com/your-org/py4csr/issues",
        "Documentation": "https://py4csr.readthedocs.io",
        "Source Code": "https://github.com/your-org/py4csr",
        "Changelog": "https://github.com/your-org/py4csr/blob/main/CHANGELOG.md",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Natural Language :: English",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
        "sas": [
            "pyreadstat>=1.1.0",
            "sas7bdat>=2.2.0",
        ],
        "plotting": [
            "plotly>=5.0",
            "bokeh>=2.0",
            "seaborn>=0.11",
        ],
        "all": [
            "pyreadstat>=1.1.0",
            "sas7bdat>=2.2.0",
            "plotly>=5.0",
            "bokeh>=2.0",
            "seaborn>=0.11",
        ],
    },
    entry_points={
        "console_scripts": [
            "py4csr=py4csr.cli.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "py4csr": [
            "templates/*.yaml",
            "templates/*.json",
            "config/*.yaml",
            "examples/data/*.csv",
        ],
    },
    keywords=[
        "clinical trials",
        "pharmaceutical",
        "biostatistics",
        "regulatory",
        "CDISC",
        "ADaM",
        "SAS",
        "reporting",
        "statistics",
        "clinical research",
    ],
    zip_safe=False,
) 