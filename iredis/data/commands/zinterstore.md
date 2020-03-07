Computes the intersection of `numkeys` sorted sets given by the specified keys,
and stores the result in `destination`. It is mandatory to provide the number of
input keys (`numkeys`) before passing the input keys and the other (optional)
arguments.

By default, the resulting score of an element is the sum of its scores in the
sorted sets where it exists. Because intersection requires an element to be a
member of every given sorted set, this results in the score of every element in
the resulting sorted set to be equal to the number of input sorted sets.

For a description of the `WEIGHTS` and `AGGREGATE` options, see `ZUNIONSTORE`.

If `destination` already exists, it is overwritten.

@return

@integer-reply: the number of elements in the resulting sorted set at
`destination`.

@examples

```cli
ZADD zset1 1 "one"
ZADD zset1 2 "two"
ZADD zset2 1 "one"
ZADD zset2 2 "two"
ZADD zset2 3 "three"
ZINTERSTORE out 2 zset1 zset2 WEIGHTS 2 3
ZRANGE out 0 -1 WITHSCORES
```
