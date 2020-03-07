Increments the number stored at `field` in the hash stored at `key` by
`increment`. If `key` does not exist, a new key holding a hash is created. If
`field` does not exist the value is set to `0` before the operation is
performed.

The range of values supported by `HINCRBY` is limited to 64 bit signed integers.

@return

@integer-reply: the value at `field` after the increment operation.

@examples

Since the `increment` argument is signed, both increment and decrement
operations can be performed:

```cli
HSET myhash field 5
HINCRBY myhash field 1
HINCRBY myhash field -1
HINCRBY myhash field -10
```
