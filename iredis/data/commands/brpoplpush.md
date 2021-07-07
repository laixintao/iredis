`BRPOPLPUSH` is the blocking variant of `RPOPLPUSH`. When `source` contains
elements, this command behaves exactly like `RPOPLPUSH`. When used inside a
`MULTI`/`EXEC` block, this command behaves exactly like `RPOPLPUSH`. When
`source` is empty, Redis will block the connection until another client pushes
to it or until `timeout` is reached. A `timeout` of zero can be used to block
indefinitely.

As per Redis 6.2.0, BRPOPLPUSH is considered deprecated. Please prefer `BLMOVE`
in new code.

See `RPOPLPUSH` for more information.

@return

@bulk-string-reply: the element being popped from `source` and pushed to
`destination`. If `timeout` is reached, a @nil-reply is returned.

@history

- `>= 6.0`: `timeout` is interpreted as a double instead of an integer.

## Pattern: Reliable queue

Please see the pattern description in the `RPOPLPUSH` documentation.

## Pattern: Circular list

Please see the pattern description in the `RPOPLPUSH` documentation.
