Adds all the specified members with the specified scores to the sorted set
stored at `key`. It is possible to specify multiple score / member pairs. If a
specified member is already a member of the sorted set, the score is updated and
the element reinserted at the right position to ensure the correct ordering.

If `key` does not exist, a new sorted set with the specified members as sole
members is created, like if the sorted set was empty. If the key exists but does
not hold a sorted set, an error is returned.

The score values should be the string representation of a double precision
floating point number. `+inf` and `-inf` values are valid values as well.

## ZADD options (Redis 3.0.2 or greater)

ZADD supports a list of options, specified after the name of the key and before
the first score argument. Options are:

- **XX**: Only update elements that already exist. Never add elements.
- **NX**: Don't update already existing elements. Always add new elements.
- **CH**: Modify the return value from the number of new elements added, to the
  total number of elements changed (CH is an abbreviation of _changed_). Changed
  elements are **new elements added** and elements already existing for which
  **the score was updated**. So elements specified in the command line having
  the same score as they had in the past are not counted. Note: normally the
  return value of `ZADD` only counts the number of new elements added.
- **INCR**: When this option is specified `ZADD` acts like `ZINCRBY`. Only one
  score-element pair can be specified in this mode.

## Range of integer scores that can be expressed precisely

Redis sorted sets use a _double 64-bit floating point number_ to represent the
score. In all the architectures we support, this is represented as an **IEEE 754
floating point number**, that is able to represent precisely integer numbers
between `-(2^53)` and `+(2^53)` included. In more practical terms, all the
integers between -9007199254740992 and 9007199254740992 are perfectly
representable. Larger integers, or fractions, are internally represented in
exponential form, so it is possible that you get only an approximation of the
decimal number, or of the very big integer, that you set as score.

## Sorted sets 101

Sorted sets are sorted by their score in an ascending way. The same element only
exists a single time, no repeated elements are permitted. The score can be
modified both by `ZADD` that will update the element score, and as a side
effect, its position on the sorted set, and by `ZINCRBY` that can be used in
order to update the score relatively to its previous value.

The current score of an element can be retrieved using the `ZSCORE` command,
that can also be used to verify if an element already exists or not.

For an introduction to sorted sets, see the data types page on [sorted
sets][tdtss].

[tdtss]: /topics/data-types#sorted-sets

## Elements with the same score

While the same element can't be repeated in a sorted set since every element is
unique, it is possible to add multiple different elements _having the same
score_. When multiple elements have the same score, they are _ordered
lexicographically_ (they are still ordered by score as a first key, however,
locally, all the elements with the same score are relatively ordered
lexicographically).

The lexicographic ordering used is binary, it compares strings as array of
bytes.

If the user inserts all the elements in a sorted set with the same score (for
example 0), all the elements of the sorted set are sorted lexicographically, and
range queries on elements are possible using the command `ZRANGEBYLEX` (Note: it
is also possible to query sorted sets by range of scores using `ZRANGEBYSCORE`).

@return

@integer-reply, specifically:

- The number of elements added to the sorted set, not including elements already
  existing for which the score was updated.

If the `INCR` option is specified, the return value will be @bulk-string-reply:

- The new score of `member` (a double precision floating point number)
  represented as string, or `nil` if the operation was aborted (when called with
  either the `XX` or the `NX` option).

@history

- `>= 2.4`: Accepts multiple elements. In Redis versions older than 2.4 it was
  possible to add or update a single member per call.

@examples

```cli
ZADD myzset 1 "one"
ZADD myzset 1 "uno"
ZADD myzset 2 "two" 3 "three"
ZRANGE myzset 0 -1 WITHSCORES
```
