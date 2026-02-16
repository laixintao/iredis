Unsubscribes the client from the given shard channels, or from all of them if none is given.

When no shard channels are specified, the client is unsubscribed from all the previously subscribed shard channels. 
In this case a message for every unsubscribed shard channel will be sent to the client. 

Note: The global channels and shard channels needs to be unsubscribed from separately.

For more information about sharded Pub/Sub, see [Sharded Pub/Sub](/topics/pubsub#sharded-pubsub).

@return

When successful, this command doesn't return anything.
Instead, for each shard channel, one message with the first element being the string "sunsubscribe" is pushed as a confirmation that the command succeeded.
