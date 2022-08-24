`PEXPIRETIME` has the same semantic as `EXPIRETIME`, but returns the absolute Unix expiration timestamp in milliseconds instead of seconds.

@return

@integer-reply: Expiration Unix timestamp in milliseconds, or a negative value in order to signal an error (see the description below).

* The command returns `-1` if the key exists but has no associated expiration time.
* The command returns `-2` if the key does not exist.

@examples

```cli
SET mykey "Hello"
PEXPIREAT mykey 33177117420000
PEXPIRETIME mykey
```
