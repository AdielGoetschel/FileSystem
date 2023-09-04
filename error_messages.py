from enum import Enum


class ErrorMessages(Enum):
    FileNotFoundError = "File not found: "
    DirectoryNotFoundError = "Directory not found: "
    InvalidPath = "Invalid path: "
    ExistsError = " already exists in the destination"
    ReadPermissionError = "Read permission denied"
    WritePermissionError = "Write permission denied"
    IsADirectoryError = "IsADirectoryError: "
    InvalidCommandError = "Invalid Command: "
    GeneralError = "Please try again"
    InvalidMinSizeError = "Invalid minimum size. Please provide a positive integer value"
    InvalidMaxSizeError = "Invalid maximum size. Please provide a positive integer value"
    NoSearchCriteriaError = "Error: You must specify at least one search criteria."

