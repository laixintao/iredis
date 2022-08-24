Subscribes the client to the specified shard channels.

In a Redis cluster, shard channels are assigned to slots by the same algorithm used to assign keys to slots. 
Client(s) can subscribe to a node covering a slot (primary/replica) to receive the messages published. 
All the specified shard channels needs to belong to a single slot to subscribe in a given `SSUBSCRIBE` call,
A client can subscribe to channels across different slots over separate `SSUBSCRIBE` call.

For more information about sharded Pub/Sub, see [Sharded Pub/Sub](/topics/pubsub#sharded-pubsub).

@examples

```
> ssubscribe orders
Reading messages... (press Ctrl-C to quit)
1) "ssubscribe"
2) "orders"
3) (integer) 1
1) "smessage"
2) "orders"
3) "hello"
```
