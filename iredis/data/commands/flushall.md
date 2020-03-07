Delete all the keys of all the existing databases, not just the currently
selected one. This command never fails.

The time-complexity for this operation is O(N), N being the number of keys in
all existing databases.

## `FLUSHALL ASYNC` (Redis 4.0.0 or greater)

Redis is now able to delete keys in the background in a different thread without
blocking the server. An `ASYNC` option was added to `FLUSHALL` and `FLUSHDB` in
order to let the entire dataset or a single database to be freed asynchronously.

Asynchronous `FLUSHALL` and `FLUSHDB` commands only delete keys that were
present at the time the command was invoked. Keys created during an asynchronous
flush will be unaffected.

@return

@simple-string-reply
