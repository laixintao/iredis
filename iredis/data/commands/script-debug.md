Set the debug mode for subsequent scripts executed with `EVAL`. Redis includes a
complete Lua debugger, codename LDB, that can be used to make the task of
writing complex scripts much simpler. In debug mode Redis acts as a remote
debugging server and a client, such as `redis-cli`, can execute scripts step by
step, set breakpoints, inspect variables and more - for additional information
about LDB refer to the [Redis Lua debugger](/topics/ldb) page.

**Important note:** avoid debugging Lua scripts using your Redis production
server. Use a development server instead.

LDB can be enabled in one of two modes: asynchronous or synchronous. In
asynchronous mode the server creates a forked debugging session that does not
block and all changes to the data are **rolled back** after the session
finishes, so debugging can be restarted using the same initial state. The
alternative synchronous debug mode blocks the server while the debugging session
is active and retains all changes to the data set once it ends.

- `YES`. Enable non-blocking asynchronous debugging of Lua scripts (changes are
  discarded).
- `SYNC`. Enable blocking synchronous debugging of Lua scripts (saves changes to
  data).
- `NO`. Disables scripts debug mode.

@return

@simple-string-reply: `OK`.
