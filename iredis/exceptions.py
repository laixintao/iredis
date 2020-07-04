class IRedisException(Exception):
    pass


class UsageError(IRedisException):
    pass


class InvalidArguments(IRedisException):
    """Invalid argument(s)"""


class NotRedisCommand(IRedisException):
    """Not a Redis command"""


class AmbiguousCommand(IRedisException):
    """Command is not finished, don't it's command's name"""


class NotSupport(IRedisException):
    """IRedis currently not support this."""
