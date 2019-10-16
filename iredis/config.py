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
        self.transaction = False
        # for transaction render
        self.queued_commands = []
        # show command hint?
        self.newbie_mode = False
        # display zset withscores?
        self.withscores = False
        self.version = "Unknown"
        self.no_version_reason = None

    def __setter__(self, name, value):
        # for every time start a transaction
        # clear the queued commands first
        if name == "transaction" and value is True:
            self.queued_commands = []
        super().__setattr__(name, value)


config = Config()
