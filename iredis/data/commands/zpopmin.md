Removes and returns up to `count` members with the lowest scores in the sorted
set stored at `key`.

When left unspecified, the default value for `count` is 1. Specifying a `count`
value that is higher than the sorted set's cardinality will not produce an
error. When returning multiple elements, the one with the lowest score will be
the first, followed by the elements with greater scores.

@return

@array-reply: list of popped elements and scores.

@examples

```cli
ZADD myzset 1 "one"
ZADD myzset 2 "two"
ZADD myzset 3 "three"
ZPOPMIN myzset
```
