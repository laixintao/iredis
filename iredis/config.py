from importlib_resources import path
import os
import logging

from configobj import ConfigObj, ConfigObjError
from . import data as project_data

# TODO verbose logger to print to stdout
logger = logging.getLogger(__name__)


system_config_file = "/etc/iredisrc"
pwd_config_file = os.path.join(os.getcwd(), ".iredisrc")


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
        self.raw = None
        self.completer_max = None
        # show command hint?
        self.newbie_mode = None
        self.rainbow = None
        self.retry_times = 2
        self.socket_keepalive = None
        self.decode = None
        self.no_info = None
        self.bottom_bar = None

        self.warning = True

        self.no_version_reason = None
        self.log_location = None
        self.completion_casing = None

        # ===bad code===
        # below are not configs, it's global state, it's wrong to write this
        # please do not add more global state.
        # FIXME this should be removed.
        # use client attributes instead.
        # use kwargs in render functions.

        # for transaction render
        self.queued_commands = []
        self.transaction = False
        # display zset withscores?
        self.withscores = False
        self.version = "Unknown"

    def __setter__(self, name, value):
        # for every time start a transaction
        # clear the queued commands first
        if name == "transaction" and value is True:
            self.queued_commands = []
        super().__setattr__(name, value)


config = Config()


def read_config_file(f):
    """Read a config file."""

    if isinstance(f, str):
        f = os.path.expanduser(f)

    try:
        config = ConfigObj(f, interpolation=False, encoding="utf8")
    except ConfigObjError as e:
        logger.error(
            "Unable to parse line {0} of config file " "'{1}'.".format(e.line_number, f)
        )
        logger.error("Using successfully parsed config values.")
        return e.config
    except (IOError, OSError) as e:
        logger.error(
            "You don't have permission to read " "config file '{0}'.".format(e.filename)
        )
        return None

    return config


def load_config_files(iredisrc):
    global config

    with path(project_data, "iredisrc") as p:
        config_obj = ConfigObj(str(p))

    for _file in [system_config_file, iredisrc, pwd_config_file]:
        _config = read_config_file(_file)
        if bool(_config) is True:
            config_obj.merge(_config)
            config_obj.filename = _config.filename

    # TODO grouping them, don't put all to "main"
    config.raw = config_obj["main"].as_bool("raw")
    config.completer_max = config_obj["main"].as_int("completer_max")
    config.retry_times = config_obj["main"].as_int("retry_times")
    config.newbie_mode = config_obj["main"].as_bool("newbie_mode")
    config.rainbow = config_obj["main"].as_bool("rainbow")
    config.socket_keepalive = config_obj["main"].as_bool("socket_keepalive")
    config.no_info = config_obj["main"].as_bool("no_info")
    config.bottom_bar = config_obj["main"].as_bool("bottom_bar")
    config.warning = config_obj["main"].as_bool("warning")
    config.decode = config_obj["main"]["decode"]
    config.log_location = config_obj["main"]["log_location"]
    config.completion_casing = config_obj["main"]["completion_casing"]

    return config_obj
