This command is similar to `ZINTERSTORE`, but instead of storing the resulting
sorted set, it is returned to the client.

For a description of the `WEIGHTS` and `AGGREGATE` options, see `ZUNIONSTORE`.

@return

@array-reply: the result of intersection (optionally with their scores, in case 
the `WITHSCORES` option is given).

@examples

```cli
ZADD zset1 1 "one"
ZADD zset1 2 "two"
ZADD zset2 1 "one"
ZADD zset2 2 "two"
ZADD zset2 3 "three"
ZINTER 2 zset1 zset2
ZINTER 2 zset1 zset2 WITHSCORES
```
