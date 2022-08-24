This command is similar to `SINTER`, but instead of returning the result set, it returns just the cardinality of the result.
Returns the cardinality of the set which would result from the intersection of all the given sets.

Keys that do not exist are considered to be empty sets.
With one of the keys being an empty set, the resulting set is also empty (since set intersection with an empty set always results in an empty set).

By default, the command calculates the cardinality of the intersection of all given sets.
When provided with the optional `LIMIT` argument (which defaults to 0 and means unlimited), if the intersection cardinality reaches limit partway through the computation, the algorithm will exit and yield limit as the cardinality.
Such implementation ensures a significant speedup for queries where the limit is lower than the actual intersection cardinality.

@return

@integer-reply: the number of elements in the resulting intersection.

@examples

```cli
SADD key1 "a"
SADD key1 "b"
SADD key1 "c"
SADD key1 "d"
SADD key2 "c"
SADD key2 "d"
SADD key2 "e"
SINTER key1 key2
SINTERCARD 2 key1 key2
SINTERCARD 2 key1 key2 LIMIT 1
```
