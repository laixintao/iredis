Delete all the keys of all the existing databases, not just the currently selected one.
This command never fails.

By default, `FLUSHALL` will synchronously flush all the databases.
Starting with Redis 6.2, setting the **lazyfree-lazy-user-flush** configuration directive to "yes" changes the default flush mode to asynchronous.

It is possible to use one of the following modifiers to dictate the flushing mode explicitly:

* `ASYNC`: flushes the databases asynchronously
* `!SYNC`: flushes the databases synchronously

Note: an asynchronous `FLUSHALL` command only deletes keys that were present at the time the command was invoked. Keys created during an asynchronous flush will be unaffected.

@return

@simple-string-reply

## Behavior change history

*   `>= 6.2.0`: Default flush behavior now configurable by the **lazyfree-lazy-user-flush** configuration directive. 