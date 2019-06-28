# -*- coding: utf-8 -*-
import os
import logging
from pathlib import Path

import click
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

logging.basicConfig(
    filename="rdcli.log",
    filemode="a",
    format="%(levelname)s %(message)s",
    level="DEBUG",
)
logger = logging.getLogger(__name__)

HISTORY_FILE = Path(os.path.expanduser("~")) / ".rdcli_history"

# Create history file if not exists.
if not os.path.exists(HISTORY_FILE):
    f = open(HISTORY_FILE, "w+")
    f.close()
session = PromptSession(history=FileHistory(HISTORY_FILE))




def repl():
    while True:
        input_text = session.prompt()
        logger.info(f"input: {input_text}")


@click.command()
@click.option("-h", help="Server hostname", default="127.0.0.1")
@click.option("-p", help="Server port", default="6379")
def rdcli(h, p):
    logger.info(f"rdcli start, host={h}, port={p}.")
    repl()


if __name__ == "__main__":
    rdcli()
