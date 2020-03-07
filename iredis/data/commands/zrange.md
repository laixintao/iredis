Returns the specified range of elements in the sorted set stored at `key`. The
elements are considered to be ordered from the lowest to the highest score.
Lexicographical order is used for elements with equal score.

See `ZREVRANGE` when you need the elements ordered from highest to lowest score
(and descending lexicographical order for elements with equal score).

Both `start` and `stop` are zero-based indexes, where `0` is the first element,
`1` is the next element and so on. They can also be negative numbers indicating
offsets from the end of the sorted set, with `-1` being the last element of the
sorted set, `-2` the penultimate element and so on.

`start` and `stop` are **inclusive ranges**, so for example `ZRANGE myzset 0 1`
will return both the first and the second element of the sorted set.

Out of range indexes will not produce an error. If `start` is larger than the
largest index in the sorted set, or `start > stop`, an empty list is returned.
If `stop` is larger than the end of the sorted set Redis will treat it like it
is the last element of the sorted set.

It is possible to pass the `WITHSCORES` option in order to return the scores of
the elements together with the elements. The returned list will contain
`value1,score1,...,valueN,scoreN` instead of `value1,...,valueN`. Client
libraries are free to return a more appropriate data type (suggestion: an array
with (value, score) arrays/tuples).

@return

@array-reply: list of elements in the specified range (optionally with their
scores, in case the `WITHSCORES` option is given).

@examples

```cli
ZADD myzset 1 "one"
ZADD myzset 2 "two"
ZADD myzset 3 "three"
ZRANGE myzset 0 -1
ZRANGE myzset 2 3
ZRANGE myzset -2 -1
```

The following example using `WITHSCORES` shows how the command returns always an
array, but this time, populated with _element_1_, _score_1_, _element_2_,
_score_2_, ..., _element_N_, _score_N_.

```cli
ZRANGE myzset 0 1 WITHSCORES
```
