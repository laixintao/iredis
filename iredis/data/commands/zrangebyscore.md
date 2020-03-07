Returns all the elements in the sorted set at `key` with a score between `min`
and `max` (including elements with score equal to `min` or `max`). The elements
are considered to be ordered from low to high scores.

The elements having the same score are returned in lexicographical order (this
follows from a property of the sorted set implementation in Redis and does not
involve further computation).

The optional `LIMIT` argument can be used to only get a range of the matching
elements (similar to _SELECT LIMIT offset, count_ in SQL). A negative `count`
returns all elements from the `offset`. Keep in mind that if `offset` is large,
the sorted set needs to be traversed for `offset` elements before getting to the
elements to return, which can add up to O(N) time complexity.

The optional `WITHSCORES` argument makes the command return both the element and
its score, instead of the element alone. This option is available since Redis
2.0.

## Exclusive intervals and infinity

`min` and `max` can be `-inf` and `+inf`, so that you are not required to know
the highest or lowest score in the sorted set to get all elements from or up to
a certain score.

By default, the interval specified by `min` and `max` is closed (inclusive). It
is possible to specify an open interval (exclusive) by prefixing the score with
the character `(`. For example:

```
ZRANGEBYSCORE zset (1 5
```

Will return all elements with `1 < score <= 5` while:

```
ZRANGEBYSCORE zset (5 (10
```

Will return all the elements with `5 < score < 10` (5 and 10 excluded).

@return

@array-reply: list of elements in the specified score range (optionally with
their scores).

@examples

```cli
ZADD myzset 1 "one"
ZADD myzset 2 "two"
ZADD myzset 3 "three"
ZRANGEBYSCORE myzset -inf +inf
ZRANGEBYSCORE myzset 1 2
ZRANGEBYSCORE myzset (1 2
ZRANGEBYSCORE myzset (1 (2
```

## Pattern: weighted random selection of an element

Normally `ZRANGEBYSCORE` is simply used in order to get range of items where the
score is the indexed integer key, however it is possible to do less obvious
things with the command.

For example a common problem when implementing Markov chains and other
algorithms is to select an element at random from a set, but different elements
may have different weights that change how likely it is they are picked.

This is how we use this command in order to mount such an algorithm:

Imagine you have elements A, B and C with weights 1, 2 and 3. You compute the
sum of the weights, which is 1+2+3 = 6

At this point you add all the elements into a sorted set using this algorithm:

```
SUM = ELEMENTS.TOTAL_WEIGHT // 6 in this case.
SCORE = 0
FOREACH ELE in ELEMENTS
    SCORE += ELE.weight / SUM
    ZADD KEY SCORE ELE
END
```

This means that you set:

```
A to score 0.16
B to score .5
C to score 1
```

Since this involves approximations, in order to avoid C is set to, like, 0.998
instead of 1, we just modify the above algorithm to make sure the last score is
1 (left as an exercise for the reader...).

At this point, each time you want to get a weighted random element, just compute
a random number between 0 and 1 (which is like calling `rand()` in most
languages), so you can just do:

    RANDOM_ELE = ZRANGEBYSCORE key RAND() +inf LIMIT 0 1
