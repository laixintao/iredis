Read-only variant of the `BITFIELD` command.
It is like the original `BITFIELD` but only accepts `!GET` subcommand and can safely be used in read-only replicas.

Since the original `BITFIELD` has `!SET` and `!INCRBY` options it is technically flagged as a writing command in the Redis command table.
For this reason read-only replicas in a Redis Cluster will redirect it to the master instance even if the connection is in read-only mode (see the `READONLY` command of Redis Cluster).

Since Redis 6.2, the `BITFIELD_RO` variant was introduced in order to allow `BITFIELD` behavior in read-only replicas without breaking compatibility on command flags.

See original `BITFIELD` for more details.

@examples

```
BITFIELD_RO hello GET i8 16
```

@return

@array-reply: An array with each entry being the corresponding result of the subcommand given at the same position.
