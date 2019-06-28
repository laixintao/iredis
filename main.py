# -*- coding: utf-8 -*-
import os
from pathlib import Path
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

HISTORY_FILE = Path(os.path.expanduser("~")) / ".rdcli_history"

# Create history file if not exists.
if not os.path.exists(HISTORY_FILE):
    f = open(HISTORY_FILE, "w+")
    f.close()
session = PromptSession(history=FileHistory(HISTORY_FILE))


while True:
    session.prompt()
