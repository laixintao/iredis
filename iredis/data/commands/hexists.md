Returns if `field` is an existing field in the hash stored at `key`.

@return

@integer-reply, specifically:

- `1` if the hash contains `field`.
- `0` if the hash does not contain `field`, or `key` does not exist.

@examples

```cli
HSET myhash field1 "foo"
HEXISTS myhash field1
HEXISTS myhash field2
```
