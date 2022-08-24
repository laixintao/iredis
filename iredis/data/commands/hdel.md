Removes the specified fields from the hash stored at `key`.
Specified fields that do not exist within this hash are ignored.
If `key` does not exist, it is treated as an empty hash and this command returns
`0`.

@return

@integer-reply: the number of fields that were removed from the hash, not
including specified but non existing fields.

@examples

```cli
HSET myhash field1 "foo"
HDEL myhash field1
HDEL myhash field2
```
