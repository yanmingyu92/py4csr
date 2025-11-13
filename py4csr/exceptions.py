"""
Custom exceptions for py4csr package.

This module defines all custom exceptions used throughout the py4csr package
to provide clear, informative error messages for different types of failures.
"""


class Py4csrError(Exception):
    """
    Base exception class for all py4csr errors.

    All custom exceptions in py4csr inherit from this base class,
    making it easy to catch all py4csr-specific errors.

    Examples
    --------
    >>> try:
    ...     # Some py4csr operation
    ...     pass
    ... except Py4csrError as e:
    ...     print(f"py4csr error occurred: {e}")
    """

    pass


class DataValidationError(Py4csrError):
    """
    Raised when input data fails validation checks.

    This exception is raised when:
    - Required columns are missing from input datasets
    - Data types are incorrect
    - Data values are out of expected range
    - Data integrity constraints are violated

    Parameters
    ----------
    message : str
        Description of the validation error
    column : str, optional
        Name of the column that failed validation
    expected : str, optional
        Expected value or format
    actual : str, optional
        Actual value or format found

    Examples
    --------
    >>> raise DataValidationError(
    ...     "Missing required column",
    ...     column="USUBJID",
    ...     expected="Column USUBJID in dataset",
    ...     actual="Column not found"
    ... )
    """

    def __init__(self, message, column=None, expected=None, actual=None):
        self.column = column
        self.expected = expected
        self.actual = actual

        # Build detailed error message
        full_message = message
        if column:
            full_message += f"\n  Column: {column}"
        if expected:
            full_message += f"\n  Expected: {expected}"
        if actual:
            full_message += f"\n  Actual: {actual}"

        super().__init__(full_message)


class ConfigurationError(Py4csrError):
    """
    Raised when configuration is invalid or incomplete.

    This exception is raised when:
    - Required configuration parameters are missing
    - Configuration values are invalid
    - Configuration file cannot be loaded
    - Environment variables are not set

    Parameters
    ----------
    message : str
        Description of the configuration error
    parameter : str, optional
        Name of the configuration parameter
    value : str, optional
        Invalid value that was provided

    Examples
    --------
    >>> raise ConfigurationError(
    ...     "Invalid output format",
    ...     parameter="output_format",
    ...     value="invalid_format"
    ... )
    """

    def __init__(self, message, parameter=None, value=None):
        self.parameter = parameter
        self.value = value

        # Build detailed error message
        full_message = message
        if parameter:
            full_message += f"\n  Parameter: {parameter}"
        if value:
            full_message += f"\n  Value: {value}"

        super().__init__(full_message)


class OutputFormatError(Py4csrError):
    """
    Raised when output format operations fail.

    This exception is raised when:
    - Unsupported output format is requested
    - Output file cannot be created
    - Formatting operation fails
    - Required formatter dependencies are missing

    Parameters
    ----------
    message : str
        Description of the output format error
    format : str, optional
        Output format that caused the error
    reason : str, optional
        Specific reason for the failure

    Examples
    --------
    >>> raise OutputFormatError(
    ...     "PDF output requires reportlab",
    ...     format="pdf",
    ...     reason="reportlab package not installed"
    ... )
    """

    def __init__(self, message, format=None, reason=None):
        self.format = format
        self.reason = reason

        # Build detailed error message
        full_message = message
        if format:
            full_message += f"\n  Format: {format}"
        if reason:
            full_message += f"\n  Reason: {reason}"

        super().__init__(full_message)


class StatisticalError(Py4csrError):
    """
    Raised when statistical calculations fail.

    This exception is raised when:
    - Statistical method cannot be applied to data
    - Insufficient data for statistical calculation
    - Statistical assumptions are violated
    - Numerical computation fails

    Parameters
    ----------
    message : str
        Description of the statistical error
    method : str, optional
        Statistical method that failed
    reason : str, optional
        Specific reason for the failure

    Examples
    --------
    >>> raise StatisticalError(
    ...     "Cannot compute mean of empty array",
    ...     method="mean",
    ...     reason="No valid data points"
    ... )
    """

    def __init__(self, message, method=None, reason=None):
        self.method = method
        self.reason = reason

        # Build detailed error message
        full_message = message
        if method:
            full_message += f"\n  Method: {method}"
        if reason:
            full_message += f"\n  Reason: {reason}"

        super().__init__(full_message)


class MetadataError(Py4csrError):
    """
    Raised when metadata operations fail.

    This exception is raised when:
    - Metadata file cannot be loaded
    - Required metadata is missing
    - Metadata format is invalid
    - Metadata values are inconsistent

    Parameters
    ----------
    message : str
        Description of the metadata error
    file : str, optional
        Metadata file that caused the error
    key : str, optional
        Metadata key that is missing or invalid

    Examples
    --------
    >>> raise MetadataError(
    ...     "Cannot load metadata file",
    ...     file="TitleFootnote.xlsx",
    ...     key="title"
    ... )
    """

    def __init__(self, message, file=None, key=None):
        self.file = file
        self.key = key

        # Build detailed error message
        full_message = message
        if file:
            full_message += f"\n  File: {file}"
        if key:
            full_message += f"\n  Key: {key}"

        super().__init__(full_message)


class SessionError(Py4csrError):
    """
    Raised when session operations fail.

    This exception is raised when:
    - Session is not properly initialized
    - Session methods are called in wrong order
    - Session state is invalid
    - Required session data is missing

    Parameters
    ----------
    message : str
        Description of the session error
    state : str, optional
        Current session state
    expected_state : str, optional
        Expected session state

    Examples
    --------
    >>> raise SessionError(
    ...     "Cannot finalize session before defining table",
    ...     state="initialized",
    ...     expected_state="table_defined"
    ... )
    """

    def __init__(self, message, state=None, expected_state=None):
        self.state = state
        self.expected_state = expected_state

        # Build detailed error message
        full_message = message
        if state:
            full_message += f"\n  Current state: {state}"
        if expected_state:
            full_message += f"\n  Expected state: {expected_state}"

        super().__init__(full_message)


# Convenience function for raising validation errors
def validate_required_columns(df, required_columns, dataset_name="dataset"):
    """
    Validate that required columns exist in a DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame to validate
    required_columns : list of str
        List of required column names
    dataset_name : str, optional
        Name of the dataset for error messages

    Raises
    ------
    DataValidationError
        If any required columns are missing

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    >>> validate_required_columns(df, ['A', 'B', 'C'], 'test_data')
    Traceback (most recent call last):
        ...
    DataValidationError: Missing required columns in test_data
      Column: C
      Expected: Column C in dataset
      Actual: Column not found
    """
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise DataValidationError(
            f"Missing required columns in {dataset_name}",
            column=", ".join(missing),
            expected=f"Columns {missing} in dataset",
            actual="Columns not found",
        )
