class UsageError(Exception):
    pass


class InvalidArguments(UsageError):
    """Invalid argument(s)"""
