Pops one or more elements, that are member-score pairs, from the first non-empty sorted set in the provided list of key names.

`ZMPOP` and `BZMPOP` are similar to the following, more limited, commands:

- `ZPOPMIN` or `ZPOPMAX` which take only one key, and can return multiple elements.
- `BZPOPMIN` or `BZPOPMAX` which take multiple keys, but return only one element from just one key.

See `BZMPOP` for the blocking variant of this command.

When the `MIN` modifier is used, the elements popped are those with the lowest scores from the first non-empty sorted set. The `MAX` modifier causes elements with the highest scores to be popped.
The optional `COUNT` can be used to specify the number of elements to pop, and is set to 1 by default.

The number of popped elements is the minimum from the sorted set's cardinality and `COUNT`'s value.

@return

@array-reply: specifically:

* A `nil` when no element could be popped.
* A two-element array with the first element being the name of the key from which elements were popped, and the second element is an array of the popped elements. Every entry in the elements array is also an array that contains the member and its score.

@examples

```cli
ZMPOP 1 notsuchkey MIN
ZADD myzset 1 "one" 2 "two" 3 "three"
ZMPOP 1 myzset MIN
ZRANGE myzset 0 -1 WITHSCORES
ZMPOP 1 myzset MAX COUNT 10
ZADD myzset2 4 "four" 5 "five" 6 "six"
ZMPOP 2 myzset myzset2 MIN COUNT 10
ZRANGE myzset 0 -1 WITHSCORES
ZMPOP 2 myzset myzset2 MAX COUNT 10
ZRANGE myzset2 0 -1 WITHSCORES
EXISTS myzset myzset2
```
