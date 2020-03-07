Executes all previously queued commands in a [transaction][tt] and restores the
connection state to normal.

[tt]: /topics/transactions

When using `WATCH`, `EXEC` will execute commands only if the watched keys were
not modified, allowing for a [check-and-set mechanism][ttc].

[ttc]: /topics/transactions#cas

@return

@array-reply: each element being the reply to each of the commands in the atomic
transaction.

When using `WATCH`, `EXEC` can return a @nil-reply if the execution was aborted.
