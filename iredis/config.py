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
        self.compiling = True  # is loading redis commands?


config = Config()
