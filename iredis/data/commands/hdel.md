Removes the specified fields from the hash stored at `key`. Specified fields
that do not exist within this hash are ignored. If `key` does not exist, it is
treated as an empty hash and this command returns `0`.

@return

@integer-reply: the number of fields that were removed from the hash, not
including specified but non existing fields.

@history

- `>= 2.4`: Accepts multiple `field` arguments. Redis versions older than 2.4
  can only remove a field per call.

  To remove multiple fields from a hash in an atomic fashion in earlier
  versions, use a `MULTI` / `EXEC` block.

@examples

```cli
HSET myhash field1 "foo"
HDEL myhash field1
HDEL myhash field2
```
