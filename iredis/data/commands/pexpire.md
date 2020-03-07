This command works exactly like `EXPIRE` but the time to live of the key is
specified in milliseconds instead of seconds.

@return

@integer-reply, specifically:

- `1` if the timeout was set.
- `0` if `key` does not exist.

@examples

```cli
SET mykey "Hello"
PEXPIRE mykey 1500
TTL mykey
PTTL mykey
```
