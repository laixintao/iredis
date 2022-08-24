When a cluster client receives an `-ASK` redirect, the `ASKING` command is sent to the target node followed by the command which was redirected.
This is normally done automatically by cluster clients.

If an `-ASK` redirect is received during a transaction, only one ASKING command needs to be sent to the target node before sending the complete transaction to the target node.

See [ASK redirection in the Redis Cluster Specification](/topics/cluster-spec#ask-redirection) for details.

@return

@simple-string-reply: `OK`.
