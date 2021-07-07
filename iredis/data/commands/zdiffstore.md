Computes the difference between the first and all successive input sorted sets
and stores the result in `destination`. The total number of input keys is
specified by `numkeys`.

Keys that do not exist are considered to be empty sets.

If `destination` already exists, it is overwritten.

@return

@integer-reply: the number of elements in the resulting sorted set at
`destination`.

@examples

```cli
ZADD zset1 1 "one"
ZADD zset1 2 "two"
ZADD zset1 3 "three"
ZADD zset2 1 "one"
ZADD zset2 2 "two"
ZDIFFSTORE out 2 zset1 zset2
ZRANGE out 0 -1 WITHSCORES
```
