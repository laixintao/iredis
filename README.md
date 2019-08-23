# IRedis (Interactive Redis)


[![CircleCI](https://circleci.com/gh/laixintao/iredis.svg?style=svg)](https://circleci.com/gh/laixintao/iredis)

A Terminal Client for Redis with AutoCompletion and Syntax Highlighting.

![](./docs/assets/auto-complete.png)

**This project is under development, any comments are welcome.**

## Features

- Advanced code completion. If you run command `KEYS` then run `DEL`, iredis will auto complete your command based on `KEYS` result.
- Command validation: `CLUSTER MEET IP PORT`
- Command highlighting, fully based on redis grammar. Any valide command in iredis shell is a valide redis command.
- <kbd>Ctrl</kbd> + <kbd>C</kbd> to clear cureent line, won't exit redis-cli. Use <kbd>Ctrl</kbd> + <kbd>D</kbd>  
- Say "Goodbye!" to you when you exit!
- <kbd>Ctrl</kbd> + <kbd>R</kbd> to open **reverse-i-search** to search through command history.
- Auto suggestions. (Like [fish shell](http://fishshell.com/).)
- Support `--encode=utf-8`, to decode Redis' bytes responses.
- Command hint on bottom, include command syntax, supported redis version, and time complexity.

## Install

```
pip install iredis
```

## Usage

```
$ iredis -h
```

## Development

There is a full Redis command list in [commands.csv](commands.csv) file, downloaded by:

```
python scripts/download_redis_commands.py > commands.csv
```

`commands.csv` is here only for test if redis.io updated, do not package it into release.

Current implemented commands: [command_syntax.csv](command_syntax.csv).

## Planned Features

- Full help document.

## Related Projects

- [redis-tui](https://github.com/mylxsw/redis-tui)
