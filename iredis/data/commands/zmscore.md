Returns the scores associated with the specified `members` in the sorted set stored at `key`.

For every `member` that does not exist in the sorted set, a `nil` value is returned.

@return

@array-reply: list of scores or `nil` associated with the specified `member` values (a double precision floating point number),
represented as strings.

@examples

```cli
ZADD myzset 1 "one"
ZADD myzset 2 "two"
ZMSCORE myzset "one" "two" "nofield"
```
