class Config:
    """
    Global config, set once on start, then
    become readonly, never change again.
    """

    def __init__(self):
        self.raw = False
        self.decode = None


config = Config()
