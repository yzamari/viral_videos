"""
Custom exceptions for the datasources system
"""


class DatasourceError(Exception):
    """Base exception for datasource errors"""
    pass


class DatasourceNotFoundError(DatasourceError):
    """Datasource file/folder not found"""
    pass


class DatasourceFormatError(DatasourceError):
    """Invalid datasource format"""
    pass


class DatasourceSizeError(DatasourceError):
    """Datasource exceeds size limits"""
    pass


class DatasourceSecurityError(DatasourceError):
    """Security violation in datasource access"""
    pass


class DatasourceProcessingError(DatasourceError):
    """Error during datasource processing"""
    pass