This command is like `ZRANGE`, but stores the result in the `<dst>` destination key.

@return

@integer-reply: the number of elements in the resulting sorted set.

@examples

```cli
ZADD srczset 1 "one" 2 "two" 3 "three" 4 "four"
ZRANGESTORE dstzset srczset 2 -1
ZRANGE dstzset 0 -1
```
