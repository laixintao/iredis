This command is similar to `ZDIFFSTORE`, but instead of storing the resulting
sorted set, it is returned to the client.

@return

@array-reply: the result of the difference (optionally with their scores, in case
the `WITHSCORES` option is given).

@examples

```cli
ZADD zset1 1 "one"
ZADD zset1 2 "two"
ZADD zset1 3 "three"
ZADD zset2 1 "one"
ZADD zset2 2 "two"
ZDIFF 2 zset1 zset2
ZDIFF 2 zset1 zset2 WITHSCORES
```
