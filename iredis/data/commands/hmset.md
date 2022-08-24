Sets the specified fields to their respective values in the hash stored at
`key`.
This command overwrites any specified fields already existing in the hash.
If `key` does not exist, a new key holding a hash is created.

@return

@simple-string-reply

@examples

```cli
HMSET myhash field1 "Hello" field2 "World"
HGET myhash field1
HGET myhash field2
```
