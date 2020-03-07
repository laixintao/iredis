Set `key` to hold the string `value`. If `key` already holds a value, it is
overwritten, regardless of its type. Any previous time to live associated with
the key is discarded on successful `SET` operation.

## Options

The `SET` command supports a set of options that modify its behavior:

- `EX` _seconds_ -- Set the specified expire time, in seconds.
- `PX` _milliseconds_ -- Set the specified expire time, in milliseconds.
- `NX` -- Only set the key if it does not already exist.
- `XX` -- Only set the key if it already exist.
- `KEEPTTL` -- Retain the time to live associated with the key.

Note: Since the `SET` command options can replace `SETNX`, `SETEX`, `PSETEX`, it
is possible that in future versions of Redis these three commands will be
deprecated and finally removed.

@return

@simple-string-reply: `OK` if `SET` was executed correctly. @nil-reply: a Null
Bulk Reply is returned if the `SET` operation was not performed because the user
specified the `NX` or `XX` option but the condition was not met.

@history

- `>= 2.6.12`: Added the `EX`, `PX`, `NX` and `XX` options.
- `>= 6.0`: Added the `KEEPTTL` option.

@examples

```cli
SET mykey "Hello"
GET mykey

SET anotherkey "will expire in a minute" EX 60
```

## Patterns

**Note:** The following pattern is discouraged in favor of
[the Redlock algorithm](http://redis.io/topics/distlock) which is only a bit
more complex to implement, but offers better guarantees and is fault tolerant.

The command `SET resource-name anystring NX EX max-lock-time` is a simple way to
implement a locking system with Redis.

A client can acquire the lock if the above command returns `OK` (or retry after
some time if the command returns Nil), and remove the lock just using `DEL`.

The lock will be auto-released after the expire time is reached.

It is possible to make this system more robust modifying the unlock schema as
follows:

- Instead of setting a fixed string, set a non-guessable large random string,
  called token.
- Instead of releasing the lock with `DEL`, send a script that only removes the
  key if the value matches.

This avoids that a client will try to release the lock after the expire time
deleting the key created by another client that acquired the lock later.

An example of unlock script would be similar to the following:

    if redis.call("get",KEYS[1]) == ARGV[1]
    then
        return redis.call("del",KEYS[1])
    else
        return 0
    end

The script should be called with `EVAL ...script... 1 resource-name token-value`
