Flush the Lua scripts cache.

By default, `SCRIPT FLUSH` will synchronously flush the cache.
Starting with Redis 6.2, setting the **lazyfree-lazy-user-flush** configuration directive to "yes" changes the default flush mode to asynchronous.

It is possible to use one of the following modifiers to dictate the flushing mode explicitly:

* `ASYNC`: flushes the cache asynchronously
* `!SYNC`: flushes the cache synchronously

For more information about `EVAL` scripts please refer to [Introduction to Eval Scripts](/topics/eval-intro).

@return

@simple-string-reply

## Behavior change history

*   `>= 6.2.0`: Default flush behavior now configurable by the **lazyfree-lazy-user-flush** configuration directive. 