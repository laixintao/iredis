The command returns the number of _failure reports_ for the specified node.
Failure reports are the way Redis Cluster uses in order to promote a `PFAIL`
state, that means a node is not reachable, to a `FAIL` state, that means that
the majority of masters in the cluster agreed within a window of time that the
node is not reachable.

A few more details:

- A node flags another node with `PFAIL` when the node is not reachable for a
  time greater than the configured _node timeout_, which is a fundamental
  configuration parameter of a Redis Cluster.
- Nodes in `PFAIL` state are provided in gossip sections of heartbeat packets.
- Every time a node processes gossip packets from other nodes, it creates (and
  refreshes the TTL if needed) **failure reports**, remembering that a given
  node said another given node is in `PFAIL` condition.
- Each failure report has a time to live of two times the _node timeout_ time.
- If at a given time a node has another node flagged with `PFAIL`, and at the
  same time collected the majority of other master nodes _failure reports_ about
  this node (including itself if it is a master), then it elevates the failure
  state of the node from `PFAIL` to `FAIL`, and broadcasts a message forcing all
  the nodes that can be reached to flag the node as `FAIL`.

This command returns the number of failure reports for the current node which
are currently not expired (so received within two times the _node timeout_
time). The count does not include what the node we are asking this count
believes about the node ID we pass as argument, the count _only_ includes the
failure reports the node received from other nodes.

This command is mainly useful for debugging, when the failure detector of Redis
Cluster is not operating as we believe it should.

@return

@integer-reply: the number of active failure reports for the node.
