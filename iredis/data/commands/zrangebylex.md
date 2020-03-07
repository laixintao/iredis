When all the elements in a sorted set are inserted with the same score, in order
to force lexicographical ordering, this command returns all the elements in the
sorted set at `key` with a value between `min` and `max`.

If the elements in the sorted set have different scores, the returned elements
are unspecified.

The elements are considered to be ordered from lower to higher strings as
compared byte-by-byte using the `memcmp()` C function. Longer strings are
considered greater than shorter strings if the common part is identical.

The optional `LIMIT` argument can be used to only get a range of the matching
elements (similar to _SELECT LIMIT offset, count_ in SQL). A negative `count`
returns all elements from the `offset`. Keep in mind that if `offset` is large,
the sorted set needs to be traversed for `offset` elements before getting to the
elements to return, which can add up to O(N) time complexity.

## How to specify intervals

Valid _start_ and _stop_ must start with `(` or `[`, in order to specify if the
range item is respectively exclusive or inclusive. The special values of `+` or
`-` for _start_ and _stop_ have the special meaning or positively infinite and
negatively infinite strings, so for instance the command **ZRANGEBYLEX
myzset - +** is guaranteed to return all the elements in the sorted set, if all
the elements have the same score.

## Details on strings comparison

Strings are compared as binary array of bytes. Because of how the ASCII
character set is specified, this means that usually this also have the effect of
comparing normal ASCII characters in an obvious dictionary way. However this is
not true if non plain ASCII strings are used (for example utf8 strings).

However the user can apply a transformation to the encoded string so that the
first part of the element inserted in the sorted set will compare as the user
requires for the specific application. For example if I want to add strings that
will be compared in a case-insensitive way, but I still want to retrieve the
real case when querying, I can add strings in the following way:

    ZADD autocomplete 0 foo:Foo 0 bar:BAR 0 zap:zap

Because of the first _normalized_ part in every element (before the colon
character), we are forcing a given comparison, however after the range is
queries using `ZRANGEBYLEX` the application can display to the user the second
part of the string, after the colon.

The binary nature of the comparison allows to use sorted sets as a general
purpose index, for example the first part of the element can be a 64 bit big
endian number: since big endian numbers have the most significant bytes in the
initial positions, the binary comparison will match the numerical comparison of
the numbers. This can be used in order to implement range queries on 64 bit
values. As in the example below, after the first 8 bytes we can store the value
of the element we are actually indexing.

@return

@array-reply: list of elements in the specified score range.

@examples

```cli
ZADD myzset 0 a 0 b 0 c 0 d 0 e 0 f 0 g
ZRANGEBYLEX myzset - [c
ZRANGEBYLEX myzset - (c
ZRANGEBYLEX myzset [aaa (g
```
