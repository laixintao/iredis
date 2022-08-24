Returns the absolute Unix timestamp (since January 1, 1970) in seconds at which the given key will expire.

See also the `PEXPIRETIME` command which returns the same information with milliseconds resolution.

@return

@integer-reply: Expiration Unix timestamp in seconds, or a negative value in order to signal an error (see the description below).

* The command returns `-1` if the key exists but has no associated expiration time.
* The command returns `-2` if the key does not exist.

@examples

```cli
SET mykey "Hello"
EXPIREAT mykey 33177117420
EXPIRETIME mykey
```
