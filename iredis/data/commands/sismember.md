Returns if `member` is a member of the set stored at `key`.

@return

@integer-reply, specifically:

- `1` if the element is a member of the set.
- `0` if the element is not a member of the set, or if `key` does not exist.

@examples

```cli
SADD myset "one"
SISMEMBER myset "one"
SISMEMBER myset "two"
```
