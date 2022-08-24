`BLMOVE` is the blocking variant of `LMOVE`.
When `source` contains elements, this command behaves exactly like `LMOVE`.
When used inside a `MULTI`/`EXEC` block, this command behaves exactly like `LMOVE`.
When `source` is empty, Redis will block the connection until another client
pushes to it or until `timeout` (a double value specifying the maximum number of seconds to block) is reached.
A `timeout` of zero can be used to block indefinitely.

This command comes in place of the now deprecated `BRPOPLPUSH`. Doing
`BLMOVE RIGHT LEFT` is equivalent.

See `LMOVE` for more information.

@return

@bulk-string-reply: the element being popped from `source` and pushed to `destination`.
If `timeout` is reached, a @nil-reply is returned.

## Pattern: Reliable queue

Please see the pattern description in the `LMOVE` documentation.

## Pattern: Circular list

Please see the pattern description in the `LMOVE` documentation.
