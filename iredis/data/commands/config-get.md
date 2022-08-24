The `CONFIG GET` command is used to read the configuration parameters of a
running Redis server.
Not all the configuration parameters are supported in Redis 2.4, while Redis 2.6
can read the whole configuration of a server using this command.

The symmetric command used to alter the configuration at run time is `CONFIG
SET`.

`CONFIG GET` takes multiple arguments, which are glob-style patterns.
Any configuration parameter matching any of the patterns are reported as a list
of key-value pairs.
Example:

```
redis> config get *max-*-entries* maxmemory
 1) "maxmemory"
 2) "0"
 3) "hash-max-listpack-entries"
 4) "512"
 5) "hash-max-ziplist-entries"
 6) "512"
 7) "set-max-intset-entries"
 8) "512"
 9) "zset-max-listpack-entries"
10) "128"
11) "zset-max-ziplist-entries"
12) "128"
```

You can obtain a list of all the supported configuration parameters by typing
`CONFIG GET *` in an open `redis-cli` prompt.

All the supported parameters have the same meaning of the equivalent
configuration parameter used in the [redis.conf][hgcarr22rc] file:

[hgcarr22rc]: http://github.com/redis/redis/raw/unstable/redis.conf

Note that you should look at the redis.conf file relevant to the version you're
working with as configuration options might change between versions. The link
above is to the latest development version.


@return

The return type of the command is a @array-reply.
