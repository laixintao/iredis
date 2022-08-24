`EXPIREAT` has the same effect and semantic as `EXPIRE`, but instead of
specifying the number of seconds representing the TTL (time to live), it takes
an absolute [Unix timestamp][hewowu] (seconds since January 1, 1970). A
timestamp in the past will delete the key immediately.

[hewowu]: http://en.wikipedia.org/wiki/Unix_time

Please for the specific semantics of the command refer to the documentation of
`EXPIRE`.

## Background

`EXPIREAT` was introduced in order to convert relative timeouts to absolute
timeouts for the AOF persistence mode.
Of course, it can be used directly to specify that a given key should expire at
a given time in the future.

## Options

The `EXPIREAT` command supports a set of options:

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
EXISTS mykey
EXPIREAT mykey 1293840000
EXISTS mykey
```
