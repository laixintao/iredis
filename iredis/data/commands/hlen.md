Returns the number of fields contained in the hash stored at `key`.

@return

@integer-reply: number of fields in the hash, or `0` when `key` does not exist.

@examples

```cli
HSET myhash field1 "Hello"
HSET myhash field2 "World"
HLEN myhash
```
