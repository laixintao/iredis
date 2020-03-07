Returns the string representation of the type of the value stored at `key`. The
different types that can be returned are: `string`, `list`, `set`, `zset`,
`hash` and `stream`.

@return

@simple-string-reply: type of `key`, or `none` when `key` does not exist.

@examples

```cli
SET key1 "value"
LPUSH key2 "value"
SADD key3 "value"
TYPE key1
TYPE key2
TYPE key3
```
