class UsageError(Exception):
    pass


class InvalidArguments(UsageError):
    """Invalid argument(s)"""


class NotRedisCommand(UsageError):
    """Not a Redis command"""
