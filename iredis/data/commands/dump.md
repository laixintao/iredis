Serialize the value stored at key in a Redis-specific format and return it to
the user. The returned value can be synthesized back into a Redis key using the
`RESTORE` command.

The serialization format is opaque and non-standard, however it has a few
semantic characteristics:

- It contains a 64-bit checksum that is used to make sure errors will be
  detected. The `RESTORE` command makes sure to check the checksum before
  synthesizing a key using the serialized value.
- Values are encoded in the same format used by RDB.
- An RDB version is encoded inside the serialized value, so that different Redis
  versions with incompatible RDB formats will refuse to process the serialized
  value.

The serialized value does NOT contain expire information. In order to capture
the time to live of the current value the `PTTL` command should be used.

If `key` does not exist a nil bulk reply is returned.

@return

@bulk-string-reply: the serialized value.

@examples

```cli
SET mykey 10
DUMP mykey
```
