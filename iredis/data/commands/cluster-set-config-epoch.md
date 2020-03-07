This command sets a specific _config epoch_ in a fresh node. It only works when:

1. The nodes table of the node is empty.
2. The node current _config epoch_ is zero.

These prerequisites are needed since usually, manually altering the
configuration epoch of a node is unsafe, we want to be sure that the node with
the higher configuration epoch value (that is the last that failed over) wins
over other nodes in claiming the hash slots ownership.

However there is an exception to this rule, and it is when a new cluster is
created from scratch. Redis Cluster _config epoch collision resolution_
algorithm can deal with new nodes all configured with the same configuration at
startup, but this process is slow and should be the exception, only to make sure
that whatever happens, two more nodes eventually always move away from the state
of having the same configuration epoch.

So, using `CONFIG SET-CONFIG-EPOCH`, when a new cluster is created, we can
assign a different progressive configuration epoch to each node before joining
the cluster together.

@return

@simple-string-reply: `OK` if the command was executed successfully, otherwise
an error is returned.
