Sets the specified fields to their respective values in the hash stored at
`key`. This command overwrites any specified fields already existing in the
hash. If `key` does not exist, a new key holding a hash is created.

As per Redis 4.0.0, HMSET is considered deprecated. Please use `HSET` in new
code.

@return

@simple-string-reply

@examples

```cli
HMSET myhash field1 "Hello" field2 "World"
HGET myhash field1
HGET myhash field2
```
