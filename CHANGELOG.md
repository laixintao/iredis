## 1.11.1

- Bugfix: Switch `distutils.version` to `packaging.version` to fix the version parse
  for windows. (new dependency: pypi's python-packaging.

## 1.11

- Dependency: Upgrade mistune lib to ^2.0. (see
  https://github.com/laixintao/iredis/issues/232)

## 1.10

- Feature: more human readable output for `HELP` command like `ACL HELP` and
  `MEMORY HELP`.
- Feature: you can use <kbd>Ctrl</kbd> + <kbd>C</kbd> to cancel a blocking
  command like `BLPOP`.
- Test: IRedis now tested under ubuntu-latest (before is ubuntu-16.04)
- Dependency: Support Python 3.10 now, thanks to [tssujt].
- Add new command group: `bitmap`.
- Support new command in Redis:
  - `ACL GETUSER`
  - `ACL HELP`

### 1.9.4

- Bugfix: respect newbie_mode set in config, if cli flag is missing. thanks to
  [sid-maddy]

### 1.9.3

- Bugfix: When IRedis start with `--decode=utf-8`, command with shell pipe will
  fail. ( [#383](https://github.com/laixintao/iredis/issues/383)). Thanks to
  [hanaasagi].

### 1.9.2

- Bugfix: before `cluster` commands' `node-id` only accept numbers, not it's
  fixed. `node-id` can be `\w+`.
- Feature: support set client name for iredis connections via `--client-name`.

### 1.9.1

- Feature: support auto-reissue command to another Redis server, when got a
  "MOVED" error in redis cluster.

## 1.9

- Feature: Support `LPOS` command.
- Doc: Update docs in `HELP` command update to date.

## 1.8

- Feature: Fully support Redis6!
  - Support `STRALGO` command.
  - `MIGRATE` command now support `AUTH2`.
  - DISABLE `hello` command, IRedis not support RESP3.

### 1.7.4

- Bugfix: Lock wcwidth's version on `1.9.0`. Fix binary build.

### 1.7.3

- Bugfix: IRedis can be suspended by <kbd>Ctrl</kbd> + <kbd>Z</kbd>. (Thanks
  [wooden-robot])
- Bugfix: Press <kbd>Enter</kbd> when completion is open will not execute
  commands. (Thanks [wooden-robot])
- Feature: `AUTH` command is now compatible with both Redis 5 and Redis 6.
- Redis6 support: `CLIENT KILL` support kill by `USER`, `XINFO` command support
  `FULL` option.

### 1.7.2

- Feature: Support `ACL` ( [#340](https://github.com/laixintao/iredis/pull/343)
  ).
- Bugfix: Include tests in source distribution.

### 1.7.1

- Bugfix: `command in` considered as an invalid input case, due to matched with
  `command`'s syntax, and `in` as an extra args. Fixed by falling back to
  default grammar if there are ambiguous commands that can match.

## 1.7

- Update: Builtin doc was updated with latest
  redis-doc(dd4159397f115d53423c21337eedb04d3258d291).
- Feature: New command support: `CLIENT GETREDIR`, `CLIENT TRACKING` and
- Test: IRedis now was tested in both Redis 5 and Redis 6.
- Bugfix: Fix exception when transaction fails. (Thanks [brianmaissy])
- Bugfix: Merging multiple spaces bug, e.g. `set foo "hello world"` will result
  in sending `set foo "hello world"` to redis-server. `CLIENT CACHING`.
- Bugfix: `--url` options is ignored, but don't worry, it is fixed now by
  [otms61].

### 1.6.2

- Bugfix: `INFO` command accepts `section` now.
- Bugfix: refused to start when can not create connection.

### 1.6.1

- Bugfix: Dangerous command will still run even user canceled.

## 1.6

- Feature: support pager. You can disable it using `--no-pager` or in your
  `iredisrc`, or change the pager behavior by setting `pager` in `iredisrc`.

## 1.5

- Bugfix: PEEK command do not use MEMORY USAGE before redis version 4.0.
- Feature: Support disable shell pipeline feature in iredisrc. (Thanks
  [wooden-robot])

### 1.4.3

- Support `LOLWUT` command of Redis 6 version.

### 1.4.2

- Password for `AUTH` command will be hidden as `*`.

### 1.4.1

- This is a test release, nothing new.

## 1.4.0

- Bugfix: Fix PyOxidizer binary build, by locking the importlib_resources
  version.

### 1.3.1

- Bugfix: Fix PyOxidizer binary build.
- Feature: Completer for HELP command.
- Bugfix: Lowercase for `--newbie` mode.
- Bugfix: Bottom hint for IRedis builtin commands.

## 1.3.0

- Catch up with redis-doc: d19fb20..6927ef0:
  - `SET` command support `KEEPTTL` option.
  - `LPUSHX` accepts multiple elements.
  - Add commands support for:
    - CLUSTER BUMPEPOCH
    - CLUSTER FLUSHSLOTS
    - CLUSTER MYID
    - MODULE LIST
    - MODULE LOAD
    - MODULE UNLOAD
    - PSYNC
    - LATENCY DOCTOR
    - LATENCY GRAPH
    - LATENCY HISTORY
    - LATENCY LATEST
    - LATENCY RESET
    - LATENCY HELP

## 1.2.0

- Feature: Peek command now displays more friendly, before each "info" will take
  one line, now type/encoding/ttl/memory usage will display in one line, makes
  the result looks more clear.
- Support DSN. (Thanks [lyqscmy]).
- Support URL.
- Support socket connection.

### 1.1.2

- Feature: support history location config.

### 1.1.1

- This release is for testing the binary build, nothing else changed.

## 1.1

- Feature: Package into a single binary with PyOxidizer (thanks [Mac Chaffee])

### 1.0.5

- Feature: <kbd>Ctrl - X</kbd> then <kbd>Ctrl -E</kbd> to open an editor to edit
  command.
- Feature: Support `completion_casing` config.

### 1.0.4

- Bugfix: command completions when a command is substring of another command.
  [issue#198](https://github.com/laixintao/iredis/issues/198)

### 1.0.3

- Feature: Support `bitfield` command, and a new completer for int type.

### 1.0.2

- Internal: Migrate CI from travis and circleci to github action.

### 1.0.1

- Bugfix: Fix info command decode error on
  decode=utf-8 #[266](https://github.com/laixintao/iredis/pull/266)

# 1.0

- Feature: Support `EXIT` to exit iredis REPL.
- Feature: Support `CLEAR` to clear screen.
- Feature: Support config log location in iredisrc file, default to None.

### 0.9.1

- Feature: Support `PEEK` Command.

## 0.9

- Refactor: split completer update and response render; Move cli tests to travis
  ci. (Thanks: [ruohan.chen])
- Support stream commands. _ Timestamp completer support. _ Stream command
  renders and lexers.
- Bugfix: When response is None,
  `iredis.completers.udpate_completer_for_responase` will raise Exception.

### 0.8.12

- Bugfix: Multi spaces between commands can be recongnised as correct commands
  now.
- Feature: Warning on dangerous command.

### 0.8.11

- Bugfix: Fix HELP command can not render markdown with a `<h3>` header.
- Bugfix: Pipeline using a builtin Python API.

### 0.8.10

- Bugfix: previous version of iredis didn't package redis-doc correctly.
- Feature: prompt for dangerous commands.

### 0.8.9

- Support config files.

### 0.8.8

- Bugfix: pipeline in iredis can run shell command include pipes. thanks to
  [Wooden-Robot].

### 0.8.7

- Support connect shell utilities with pipeline

[wooden-robot]: https://github.com/Wooden-Robot
[ruohan.chen]: https://github.com/crhan
[mac chaffee]: https://github.com/mac-chaffee
[lyqscmy]: https://github.com/lyqscmy
[brianmaissy]: https://github.com/brianmaissy
[otms61]: https://github.com/otms61
[hanaasagi]: https://github.com/Hanaasagi
[sid-maddy]: https://github.com/sid-maddy
[tssujt]: https://github.com/tssujt
