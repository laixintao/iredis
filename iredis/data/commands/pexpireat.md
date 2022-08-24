`PEXPIREAT` has the same effect and semantic as `EXPIREAT`, but the Unix time at
which the key will expire is specified in milliseconds instead of seconds.

## Options

The `PEXPIREAT` command supports a set of options since Redis 7.0:

* `NX` -- Set expiry only when the key has no expiry
* `XX` -- Set expiry only when the key has an existing expiry
* `GT` -- Set expiry only when the new expiry is greater than current one
* `LT` -- Set expiry only when the new expiry is less than current one

A non-volatile key is treated as an infinite TTL for the purpose of `GT` and `LT`.
The `GT`, `LT` and `NX` options are mutually exclusive.

@return

@integer-reply, specifically:

* `1` if the timeout was set.
* `0` if the timeout was not set. e.g. key doesn't exist, or operation skipped due to the provided arguments.

@examples

```cli
SET mykey "Hello"
PEXPIREAT mykey 1555555555005
TTL mykey
PTTL mykey
```
