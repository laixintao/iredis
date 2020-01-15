Returns the sorted set cardinality (number of elements) of the sorted set stored
at `key`.

@return

@integer-reply: the cardinality (number of elements) of the sorted set, or `0`
if `key` does not exist.

@examples

```cli
ZADD myzset 1 "one"
ZADD myzset 2 "two"
ZCARD myzset
```
