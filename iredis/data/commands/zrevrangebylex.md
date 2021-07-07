When all the elements in a sorted set are inserted with the same score, in order
to force lexicographical ordering, this command returns all the elements in the
sorted set at `key` with a value between `max` and `min`.

Apart from the reversed ordering, `ZREVRANGEBYLEX` is similar to `ZRANGEBYLEX`.

As per Redis 6.2.0, this command is considered deprecated. Please prefer using
the `ZRANGE` command with the `BYLEX` and `REV` arguments in new code.

@return

@array-reply: list of elements in the specified score range.

@examples

```cli
ZADD myzset 0 a 0 b 0 c 0 d 0 e 0 f 0 g
ZREVRANGEBYLEX myzset [c -
ZREVRANGEBYLEX myzset (c -
ZREVRANGEBYLEX myzset (g [aaa
```
