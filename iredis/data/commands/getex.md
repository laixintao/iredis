Get the value of `key` and optionally set its expiration.
`GETEX` is similar to `GET`, but is a write command with additional options.

## Options

The `GETEX` command supports a set of options that modify its behavior:

* `EX` *seconds* -- Set the specified expire time, in seconds.
* `PX` *milliseconds* -- Set the specified expire time, in milliseconds.
* `EXAT` *timestamp-seconds* -- Set the specified Unix time at which the key will expire, in seconds.
* `PXAT` *timestamp-milliseconds* -- Set the specified Unix time at which the key will expire, in milliseconds.
* `PERSIST` -- Remove the time to live associated with the key.

@return

@bulk-string-reply: the value of `key`, or `nil` when `key` does not exist.

@examples

```cli
SET mykey "Hello"
GETEX mykey
TTL mykey
GETEX mykey EX 60
TTL mykey
```
