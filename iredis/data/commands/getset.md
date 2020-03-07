Atomically sets `key` to `value` and returns the old value stored at `key`.
Returns an error when `key` exists but does not hold a string value.

## Design pattern

`GETSET` can be used together with `INCR` for counting with atomic reset. For
example: a process may call `INCR` against the key `mycounter` every time some
event occurs, but from time to time we need to get the value of the counter and
reset it to zero atomically. This can be done using `GETSET mycounter "0"`:

```cli
INCR mycounter
GETSET mycounter "0"
GET mycounter
```

@return

@bulk-string-reply: the old value stored at `key`, or `nil` when `key` did not
exist.

@examples

```cli
SET mykey "Hello"
GETSET mykey "World"
GET mykey
```
