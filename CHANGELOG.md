### 0.9.2

* Feature: Support `EXIT` to exit iredis REPL.
* Feature: Support `CLEAR` to clear screen.

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
to [Wooden-Robot](https://github.com/Wooden-Robot)

### 0.8.7

* Support connect shell utilities with pipeline
