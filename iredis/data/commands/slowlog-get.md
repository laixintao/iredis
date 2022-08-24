The `SLOWLOG GET` command returns entries from the slow log in chronological order.

The Redis Slow Log is a system to log queries that exceeded a specified execution time.
The execution time does not include I/O operations like talking with the client, sending the reply and so forth, but just the time needed to actually execute the command (this is the only stage of command execution where the thread is blocked and can not serve other requests in the meantime).

A new entry is added to the slow log whenever a command exceeds the execution time threshold defined by the `slowlog-log-slower-than` configuration directive.
The maximum number of entries in the slow log is governed by the `slowlog-max-len` configuration directive.

By default the command returns all of the entries in the log. The optional `count` argument limits the number of returned entries, so the command returns at most up to `count` entries.

Each entry from the slow log is comprised of the following six values:

1. A unique progressive identifier for every slow log entry.
2. The unix timestamp at which the logged command was processed.
3. The amount of time needed for its execution, in microseconds.
4. The array composing the arguments of the command.
5. Client IP address and port.
6. Client name if set via the `CLIENT SETNAME` command.

The entry's unique ID can be used in order to avoid processing slow log entries multiple times (for instance you may have a script sending you an email alert for every new slow log entry).
The ID is never reset in the course of the Redis server execution, only a server
restart will reset it.

@reply

@array-reply: a list of slow log entries.
