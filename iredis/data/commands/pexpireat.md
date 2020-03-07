`PEXPIREAT` has the same effect and semantic as `EXPIREAT`, but the Unix time at
which the key will expire is specified in milliseconds instead of seconds.

@return

@integer-reply, specifically:

- `1` if the timeout was set.
- `0` if `key` does not exist.

@examples

```cli
SET mykey "Hello"
PEXPIREAT mykey 1555555555005
TTL mykey
PTTL mykey
```
