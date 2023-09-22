from enum import Enum


class ErrorKind(Enum):
    INVALID_INPUT = 1
    NETWORK_ERROR = 2
    FILE_NOT_FOUND = 3
    INVALID_DATE = 4
    AUTHENTICATION_ERROR = 5
    API_ERROR = 6
    MISSING_DATA = 7
