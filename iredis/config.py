COMPILING_IN_PROGRESS = 0
COMPILING_JUST_FINISH = 1
COMPILING_DONE = 2


class Config:
    """
    Global config, set once on start, then
    become readonly, never change again.

    :param raw: weather write raw bytes to stdout without any
        decoding.
    :param decode: How to decode bytes response.(For display and
        Completers)
        default is None, means show literal bytes. But completers
        will try use utf-8 decoding.
    """

    def __init__(self):
        self.raw = False
        self.decode = None
        self.compiling = COMPILING_IN_PROGRESS  # is loading redis commands?
        self.completer_max = 300


config = Config()
