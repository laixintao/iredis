The `CONFIG SET` command is used in order to reconfigure the server at run time
without the need to restart Redis.
You can change both trivial parameters or switch from one to another persistence
option using this command.

The list of configuration parameters supported by `CONFIG SET` can be obtained
issuing a `CONFIG GET *` command, that is the symmetrical command used to obtain
information about the configuration of a running Redis instance.

All the configuration parameters set using `CONFIG SET` are immediately loaded
by Redis and will take effect starting with the next command executed.

All the supported parameters have the same meaning of the equivalent
configuration parameter used in the [redis.conf][hgcarr22rc] file.

[hgcarr22rc]: http://github.com/redis/redis/raw/unstable/redis.conf

Note that you should look at the redis.conf file relevant to the version you're
working with as configuration options might change between versions. The link
above is to the latest development version.

It is possible to switch persistence from RDB snapshotting to append-only file
(and the other way around) using the `CONFIG SET` command.
For more information about how to do that please check the [persistence
page][tp].

[tp]: /topics/persistence

In general what you should know is that setting the `appendonly` parameter to
`yes` will start a background process to save the initial append-only file
(obtained from the in memory data set), and will append all the subsequent
commands on the append-only file, thus obtaining exactly the same effect of a
Redis server that started with AOF turned on since the start.

You can have both the AOF enabled with RDB snapshotting if you want, the two
options are not mutually exclusive.

@return

@simple-string-reply: `OK` when the configuration was set properly.
Otherwise an error is returned.
