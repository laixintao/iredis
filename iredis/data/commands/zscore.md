Returns the score of `member` in the sorted set at `key`.

If `member` does not exist in the sorted set, or `key` does not exist, `nil` is
returned.

@return

@bulk-string-reply: the score of `member` (a double precision floating point
number), represented as string.

@examples

```cli
ZADD myzset 1 "one"
ZSCORE myzset "one"
```
