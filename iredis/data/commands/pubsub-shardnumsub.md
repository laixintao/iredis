Returns the number of subscribers for the specified shard channels.

Note that it is valid to call this command without channels, in this case it will just return an empty list.

Cluster note: in a Redis Cluster, `PUBSUB`'s replies in a cluster only report information from the node's Pub/Sub context, rather than the entire cluster.

@return

@array-reply: a list of channels and number of subscribers for every channel.

The format is channel, count, channel, count, ..., so the list is flat. The order in which the channels are listed is the same as the order of the shard channels specified in the command call.

@examples

```
> PUBSUB SHARDNUMSUB orders
1) "orders"
2) (integer) 1
```
