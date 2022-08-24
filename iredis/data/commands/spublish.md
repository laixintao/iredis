Posts a message to the given shard channel.

In Redis Cluster, shard channels are assigned to slots by the same algorithm used to assign keys to slots.
A shard message must be sent to a node that own the slot the shard channel is hashed to. 
The cluster makes sure that published shard messages are forwarded to all the node in the shard, so clients can subscribe to a shard channel by connecting to any one of the nodes in the shard.

For more information about sharded pubsub, see [Sharded Pubsub](/topics/pubsub#sharded-pubsub).

@return

@integer-reply: the number of clients that received the message.

@examples

For example the following command publish to channel `orders` with a subscriber already waiting for message(s).
    
```
> spublish orders hello
(integer) 1
```
