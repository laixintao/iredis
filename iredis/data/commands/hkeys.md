Returns all field names in the hash stored at `key`.

@return

@array-reply: list of fields in the hash, or an empty list when `key` does not
exist.

@examples

```cli
HSET myhash field1 "Hello"
HSET myhash field2 "World"
HKEYS myhash
```
