Removes the specified members from the sorted set stored at `key`.
Non existing members are ignored.

An error is returned when `key` exists and does not hold a sorted set.

@return

@integer-reply, specifically:

* The number of members removed from the sorted set, not including non existing
  members.

@examples

```cli
ZADD myzset 1 "one"
ZADD myzset 2 "two"
ZADD myzset 3 "three"
ZREM myzset "two"
ZRANGE myzset 0 -1 WITHSCORES
```
