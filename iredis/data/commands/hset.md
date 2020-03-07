Sets `field` in the hash stored at `key` to `value`. If `key` does not exist, a
new key holding a hash is created. If `field` already exists in the hash, it is
overwritten.

As of Redis 4.0.0, HSET is variadic and allows for multiple `field`/`value`
pairs.

@return

@integer-reply: The number of fields that were added.

@examples

```cli
HSET myhash field1 "Hello"
HGET myhash field1
```
