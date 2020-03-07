Marks the start of a [transaction][tt] block. Subsequent commands will be queued
for atomic execution using `EXEC`.

[tt]: /topics/transactions

@return

@simple-string-reply: always `OK`.
