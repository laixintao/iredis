Lists the currently *active shard channels*.

An active shard channel is a Pub/Sub shard channel with one or more subscribers.

If no `pattern` is specified, all the channels are listed, otherwise if pattern is specified only channels matching the specified glob-style pattern are listed.

The information returned about the active shard channels are at the shard level and not at the cluster level.

@return

@array-reply: a list of active channels, optionally matching the specified pattern.

@examples

```
> PUBSUB SHARDCHANNELS
1) "orders"
PUBSUB SHARDCHANNELS o*
1) "orders"
```
