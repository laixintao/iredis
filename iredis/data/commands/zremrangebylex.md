When all the elements in a sorted set are inserted with the same score, in order
to force lexicographical ordering, this command removes all elements in the
sorted set stored at `key` between the lexicographical range specified by `min`
and `max`.

The meaning of `min` and `max` are the same of the `ZRANGEBYLEX` command.
Similarly, this command actually returns the same elements that `ZRANGEBYLEX`
would return if called with the same `min` and `max` arguments.

@return

@integer-reply: the number of elements removed.

@examples

```cli
ZADD myzset 0 aaaa 0 b 0 c 0 d 0 e
ZADD myzset 0 foo 0 zap 0 zip 0 ALPHA 0 alpha
ZRANGE myzset 0 -1
ZREMRANGEBYLEX myzset [alpha [omega
ZRANGE myzset 0 -1
```
