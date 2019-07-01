# -*- coding: utf-8 -*-
import os
import logging
from pathlib import Path

import redis
import click
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

logging.basicConfig(
    filename="rdcli.log",
    filemode="a",
    format="%(levelname)5s %(message)s",
    level="DEBUG",
)
logger = logging.getLogger(__name__)

HISTORY_FILE = Path(os.path.expanduser("~")) / ".rdcli_history"


class Client:
    def __init__(self, host, port, db):
        self.host = host
        self.port = port
        self.db = db
        self._redis_client = redis.StrictRedis(host, port, db)

    def __str__(self):
        return f"{self.host}:{self.port}[{self.db}]> "

    def send_command(self, command):
        return self._redis_client.execute_command(command)


def repl(client, session):
    while True:
        logger.debug("REPL waiting for command...")
        command = session.prompt(str(client))
        logger.info(f"Command: {command}")

        # blank input
        if not command:
            continue
        
        try:
            answer = client.send_command(command)

        # Error with previous command or exception
        except Exception as e:
            print("(error)", str(e))
        # Fine with answer
        else:
            print(answer)


@click.command()
@click.option("-h", help="Server hostname", default="127.0.0.1")
@click.option("-p", help="Server port", default="6379")
@click.option("-n", help="Database number.", default="0")
def rdcli(h, p, n):
    logger.info(f"rdcli start, host={h}, port={p}, db={n}.")
    # Create history file if not exists.
    if not os.path.exists(HISTORY_FILE):
        logger.info(f"History file {HISTORY_FILE} not exists, create now...")
        f = open(HISTORY_FILE, "w+")
        f.close()

    session = PromptSession(history=FileHistory(HISTORY_FILE))

    client = Client(h, p, n)
    repl(client, session)


if __name__ == "__main__":

    try:
        rdcli()
    except click.exceptions.Abort as e:
        logger.warn(e)
