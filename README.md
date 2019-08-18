# iRedis

[![CircleCI](https://circleci.com/gh/laixintao/iredis.svg?style=svg)](https://circleci.com/gh/laixintao/iredis)

A Terminal Client for Redis with AutoCompletion and Syntax Highlighting.

**This project is under development, any comments are welcome.**

## Features

- <kbd>Ctrl</kbd> + <kbd>C</kbd> to clear cureent line, won't exit redis-cli. Use <kbd>Ctrl</kbd> + <kbd>D</kbd>  
- Say "Goodbye!" to you when you exit!
- <kbd>Ctrl</kbd> + <kbd>R</kbd> to open **reverse-i-search** to search through command history.
- iredis is smart, `CLUSTER NODES`, then `CLUSTER COUNT-FAILURE-REPORTS node-id`, iredis will do auto complete based on previous command.
- Command validation: `CLUSTER MEET IP PORT`
- Zsh style history(use <kbd>↑</kdb> to do part history search).

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

Current implemented commands: [command_syntax.csv](command_syntax.csv).

## Planned Features


## Related Projects

- [redis-tui](https://github.com/mylxsw/redis-tui)
