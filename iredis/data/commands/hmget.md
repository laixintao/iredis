Returns the values associated with the specified `fields` in the hash stored at
`key`.

For every `field` that does not exist in the hash, a `nil` value is returned.
Because non-existing keys are treated as empty hashes, running `HMGET` against a
non-existing `key` will return a list of `nil` values.

@return

@array-reply: list of values associated with the given fields, in the same order
as they are requested.

```cli
HSET myhash field1 "Hello"
HSET myhash field2 "World"
HMGET myhash field1 field2 nofield
```
