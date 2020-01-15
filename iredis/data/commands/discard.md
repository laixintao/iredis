Flushes all previously queued commands in a [transaction][tt] and restores the
connection state to normal.

[tt]: /topics/transactions

If `WATCH` was used, `DISCARD` unwatches all keys watched by the connection.

@return

@simple-string-reply: always `OK`.
