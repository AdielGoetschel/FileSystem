from enum import Enum

"""
ErrorMessages is an class that provides descriptive error messages for various file system-related error
"""


class ErrorMessages(Enum):
    NotFoundError = "Not found: "
    InvalidPath = "Invalid path: "
    ExistsError = " already exists in the destination"
    IsADirectoryError = "IsADirectoryError: "
    InvalidCommandError = "Invalid Command: "
    GeneralError = "Please try again"
    InvalidMinSizeError = "Invalid minimum size. Please provide a positive integer value"
    InvalidMaxSizeError = "Invalid maximum size. Please provide a positive integer value"
    NoSearchCriteriaError = "Error: You must specify at least one search criteria."
    ExceedsMaxMemoryFileError = "Memory allocation exceeds max memory for file: "
    ExceedsMaxSizeError = "Memory allocation exceeds memory buffer size"

