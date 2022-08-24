Returns the number of unique patterns that are subscribed to by clients (that are performed using the `PSUBSCRIBE` command).

Note that this isn't the count of clients subscribed to patterns, but the total number of unique patterns all the clients are subscribed to.

Cluster note: in a Redis Cluster clients can subscribe to every node, and can also publish to every other node. The cluster will make sure that published messages are forwarded as needed. That said, `PUBSUB`'s replies in a cluster only report information from the node's Pub/Sub context, rather than the entire cluster.

@return

@integer-reply: the number of patterns all the clients are subscribed to.
