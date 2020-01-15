Flushes all the previously watched keys for a [transaction][tt].

[tt]: /topics/transactions

If you call `EXEC` or `DISCARD`, there's no need to manually call `UNWATCH`.

@return

@simple-string-reply: always `OK`.
