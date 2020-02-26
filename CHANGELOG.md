## 1.0.5

* Feature: <kbd>Ctrl - X</kbd> then <kbd>Ctrl -E</kbd> to open an editor to edit
command.
* Feature: Support `completion_casing` config.

### 1.0.4

* Bugfix: command completions when a command is substring of another command. [issue#198](https://github.com/laixintao/iredis/issues/198)

### 1.0.3

* Feature: Support `bitfield` command, and a new completer for int type.

### 1.0.2

* Internal: Migrate CI from travis and circleci to github action.

### 1.0.1

* Bugfix: Fix info command decode error on decode=utf-8 #[266](https://github.com/laixintao/iredis/pull/266)

# 1.0

* Feature: Support `EXIT` to exit iredis REPL.
* Feature: Support `CLEAR` to clear screen.
* Feature: Support config log location in iredisrc file, default to None.

### 0.9.1

* Feature: Support `PEEK` Command.

## 0.9

* Refactor: split completer update and response render; Move cli tests to 
travis ci.
* Support stream commands.
	* Timestamp completer support.
	* Stream command renders and lexers.
* Bugfix: When response is None,
	`iredis.completers.udpate_completer_for_responase` will raise Exception.

### 0.8.12

* Bugfix: Multi spaces between commands can be recongnised as correct
commands now.
* Feature: Warning on dangerous command.

### 0.8.11

* Bugfix: Fix HELP command can not render markdown with a `<h3>` header.
* Bugfix: Pipeline using a builtin Python API.

### 0.8.10

* Bugfix: previous version of iredis didn't package redis-doc correctly.
* Feature: prompt for dangerous commands.

### 0.8.9

* Support config files.

### 0.8.8

* Bugfix: pipeline in iredis can run shell command include pipes. thanks
to [Wooden-Robot].

### 0.8.7

* Support connect shell utilities with pipeline

# Contributors

[Wooden-Robot]: https://github.com/Wooden-Robot
