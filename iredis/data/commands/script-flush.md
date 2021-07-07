Flush the Lua scripts cache.

Please refer to the `EVAL` documentation for detailed information about Redis
Lua scripting.

By default, `SCRIPT FLUSH` will synchronously flush the cache. Starting with
Redis 6.2, setting the **lazyfree-lazy-user-flush** configuration directive to
"yes" changes the default flush mode to asynchronous.

It is possible to use one of the following modifiers to dictate the flushing
mode explicitly:

- `ASYNC`: flushes the cache asynchronously
- `!SYNC`: flushes the cache synchronously

@return

@simple-string-reply

@history

- `>= 6.2.0`: Added the `ASYNC` and `!SYNC` flushing mode modifiers, as well as
  the **lazyfree-lazy-user-flush** configuration directive.
