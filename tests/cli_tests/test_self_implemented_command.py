"""
check ascii table:
http://ascii-table.com/ansi-escape-sequences.php
"""


def test_clear(cli):
    cli.sendline("clear")
    cli.expect("\\[2J")  # clear screen
