The `CONFIG GET` command is used to read the configuration parameters of a
running Redis server. Not all the configuration parameters are supported in
Redis 2.4, while Redis 2.6 can read the whole configuration of a server using
this command.

The symmetric command used to alter the configuration at run time is
`CONFIG SET`.

`CONFIG GET` takes a single argument, which is a glob-style pattern. All the
configuration parameters matching this parameter are reported as a list of
key-value pairs. Example:

```
redis> config get *max-*-entries*
1) "hash-max-zipmap-entries"
2) "512"
3) "list-max-ziplist-entries"
4) "512"
5) "set-max-intset-entries"
6) "512"
```

You can obtain a list of all the supported configuration parameters by typing
`CONFIG GET *` in an open `redis-cli` prompt.

All the supported parameters have the same meaning of the equivalent
configuration parameter used in the [redis.conf][hgcarr22rc] file, with the
following important differences:

[hgcarr22rc]: http://github.com/redis/redis/raw/2.8/redis.conf

- Where bytes or other quantities are specified, it is not possible to use the
  `redis.conf` abbreviated form (`10k`, `2gb` ... and so forth), everything
  should be specified as a well-formed 64-bit integer, in the base unit of the
  configuration directive.
- The save parameter is a single string of space-separated integers. Every pair
  of integers represent a seconds/modifications threshold.

For instance what in `redis.conf` looks like:

```
save 900 1
save 300 10
```

that means, save after 900 seconds if there is at least 1 change to the dataset,
and after 300 seconds if there are at least 10 changes to the dataset, will be
reported by `CONFIG GET` as "900 1 300 10".

@return

The return type of the command is a @array-reply.
