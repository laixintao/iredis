The `MEMORY USAGE` command reports the number of bytes that a key and its value
require to be stored in RAM.

The reported usage is the total of memory allocations for data and
administrative overheads that a key its value require.

For nested data types, the optional `SAMPLES` option can be provided, where
`count` is the number of sampled nested values. By default, this option is set
to `5`. To sample the all of the nested values, use `SAMPLES 0`.

@examples

With Redis v4.0.1 64-bit and **jemalloc**, the empty string measures as follows:

```
> SET "" ""
OK
> MEMORY USAGE ""
(integer) 51
```

These bytes are pure overhead at the moment as no actual data is stored, and are
used for maintaining the internal data structures of the server. Longer keys and
values show asymptotically linear usage.

```
> SET foo bar
OK
> MEMORY USAGE foo
(integer) 54
> SET cento 01234567890123456789012345678901234567890123
45678901234567890123456789012345678901234567890123456789
OK
127.0.0.1:6379> MEMORY USAGE cento
(integer) 153
```

@return

@integer-reply: the memory usage in bytes
