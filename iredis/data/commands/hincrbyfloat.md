Increment the specified `field` of a hash stored at `key`, and representing a
floating point number, by the specified `increment`. If the increment value is
negative, the result is to have the hash field value **decremented** instead of
incremented. If the field does not exist, it is set to `0` before performing the
operation. An error is returned if one of the following conditions occur:

- The field contains a value of the wrong type (not a string).
- The current field content or the specified increment are not parsable as a
  double precision floating point number.

The exact behavior of this command is identical to the one of the `INCRBYFLOAT`
command, please refer to the documentation of `INCRBYFLOAT` for further
information.

@return

@bulk-string-reply: the value of `field` after the increment.

@examples

```cli
HSET mykey field 10.50
HINCRBYFLOAT mykey field 0.1
HINCRBYFLOAT mykey field -5
HSET mykey field 5.0e3
HINCRBYFLOAT mykey field 2.0e2
```

## Implementation details

The command is always propagated in the replication link and the Append Only
File as a `HSET` operation, so that differences in the underlying floating point
math implementation will not be sources of inconsistency.
