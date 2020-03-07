Returns the rank of `member` in the sorted set stored at `key`, with the scores
ordered from low to high. The rank (or index) is 0-based, which means that the
member with the lowest score has rank `0`.

Use `ZREVRANK` to get the rank of an element with the scores ordered from high
to low.

@return

- If `member` exists in the sorted set, @integer-reply: the rank of `member`.
- If `member` does not exist in the sorted set or `key` does not exist,
  @bulk-string-reply: `nil`.

@examples

```cli
ZADD myzset 1 "one"
ZADD myzset 2 "two"
ZADD myzset 3 "three"
ZRANK myzset "three"
ZRANK myzset "four"
```
