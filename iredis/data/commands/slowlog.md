This command is used in order to read and reset the Redis slow queries log.

## Redis slow log overview

The Redis Slow Log is a system to log queries that exceeded a specified
execution time. The execution time does not include I/O operations like talking
with the client, sending the reply and so forth, but just the time needed to
actually execute the command (this is the only stage of command execution where
the thread is blocked and can not serve other requests in the meantime).

You can configure the slow log with two parameters: _slowlog-log-slower-than_
tells Redis what is the execution time, in microseconds, to exceed in order for
the command to get logged. Note that a negative number disables the slow log,
while a value of zero forces the logging of every command. _slowlog-max-len_ is
the length of the slow log. The minimum value is zero. When a new command is
logged and the slow log is already at its maximum length, the oldest one is
removed from the queue of logged commands in order to make space.

The configuration can be done by editing `redis.conf` or while the server is
running using the `CONFIG GET` and `CONFIG SET` commands.

## Reading the slow log

The slow log is accumulated in memory, so no file is written with information
about the slow command executions. This makes the slow log remarkably fast at
the point that you can enable the logging of all the commands (setting the
_slowlog-log-slower-than_ config parameter to zero) with minor performance hit.

To read the slow log the **SLOWLOG GET** command is used, that returns every
entry in the slow log. It is possible to return only the N most recent entries
passing an additional argument to the command (for instance **SLOWLOG GET 10**).

Note that you need a recent version of redis-cli in order to read the slow log
output, since it uses some features of the protocol that were not formerly
implemented in redis-cli (deeply nested multi bulk replies).

## Output format

```
redis 127.0.0.1:6379> slowlog get 2
1) 1) (integer) 14
   2) (integer) 1309448221
   3) (integer) 15
   4) 1) "ping"
2) 1) (integer) 13
   2) (integer) 1309448128
   3) (integer) 30
   4) 1) "slowlog"
      2) "get"
      3) "100"
```

There are also optional fields emitted only by Redis 4.0 or greater:

```
5) "127.0.0.1:58217"
6) "worker-123"
```

Every entry is composed of four (or six starting with Redis 4.0) fields:

- A unique progressive identifier for every slow log entry.
- The unix timestamp at which the logged command was processed.
- The amount of time needed for its execution, in microseconds.
- The array composing the arguments of the command.
- Client IP address and port (4.0 only).
- Client name if set via the `CLIENT SETNAME` command (4.0 only).

The entry's unique ID can be used in order to avoid processing slow log entries
multiple times (for instance you may have a script sending you an email alert
for every new slow log entry).

The ID is never reset in the course of the Redis server execution, only a server
restart will reset it.

## Obtaining the current length of the slow log

It is possible to get just the length of the slow log using the command
**SLOWLOG LEN**.

## Resetting the slow log.

You can reset the slow log using the **SLOWLOG RESET** command. Once deleted the
information is lost forever.
