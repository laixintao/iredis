This command is similar to `ZINTER`, but instead of returning the result set, it returns just the cardinality of the result.

Keys that do not exist are considered to be empty sets.
With one of the keys being an empty set, the resulting set is also empty (since set intersection with an empty set always results in an empty set).

By default, the command calculates the cardinality of the intersection of all given sets.
When provided with the optional `LIMIT` argument (which defaults to 0 and means unlimited), if the intersection cardinality reaches limit partway through the computation, the algorithm will exit and yield limit as the cardinality.
Such implementation ensures a significant speedup for queries where the limit is lower than the actual intersection cardinality.

@return

@integer-reply: the number of elements in the resulting intersection.

@examples

```cli
ZADD zset1 1 "one"
ZADD zset1 2 "two"
ZADD zset2 1 "one"
ZADD zset2 2 "two"
ZADD zset2 3 "three"
ZINTER 2 zset1 zset2
ZINTERCARD 2 zset1 zset2
ZINTERCARD 2 zset1 zset2 LIMIT 1
```
