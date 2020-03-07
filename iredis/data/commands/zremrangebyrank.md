Removes all elements in the sorted set stored at `key` with rank between `start`
and `stop`. Both `start` and `stop` are `0` -based indexes with `0` being the
element with the lowest score. These indexes can be negative numbers, where they
indicate offsets starting at the element with the highest score. For example:
`-1` is the element with the highest score, `-2` the element with the second
highest score and so forth.

@return

@integer-reply: the number of elements removed.

@examples

```cli
ZADD myzset 1 "one"
ZADD myzset 2 "two"
ZADD myzset 3 "three"
ZREMRANGEBYRANK myzset 0 1
ZRANGE myzset 0 -1 WITHSCORES
```
