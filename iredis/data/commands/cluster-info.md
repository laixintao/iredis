`CLUSTER INFO` provides `INFO` style information about Redis Cluster vital
parameters. The following is a sample output, followed by the description of
each field reported.

```
cluster_state:ok
cluster_slots_assigned:16384
cluster_slots_ok:16384
cluster_slots_pfail:0
cluster_slots_fail:0
cluster_known_nodes:6
cluster_size:3
cluster_current_epoch:6
cluster_my_epoch:2
cluster_stats_messages_sent:1483972
cluster_stats_messages_received:1483968
```

- `cluster_state`: State is `ok` if the node is able to receive queries. `fail`
  if there is at least one hash slot which is unbound (no node associated), in
  error state (node serving it is flagged with FAIL flag), or if the majority of
  masters can't be reached by this node.
- `cluster_slots_assigned`: Number of slots which are associated to some node
  (not unbound). This number should be 16384 for the node to work properly,
  which means that each hash slot should be mapped to a node.
- `cluster_slots_ok`: Number of hash slots mapping to a node not in `FAIL` or
  `PFAIL` state.
- `cluster_slots_pfail`: Number of hash slots mapping to a node in `PFAIL`
  state. Note that those hash slots still work correctly, as long as the `PFAIL`
  state is not promoted to `FAIL` by the failure detection algorithm. `PFAIL`
  only means that we are currently not able to talk with the node, but may be
  just a transient error.
- `cluster_slots_fail`: Number of hash slots mapping to a node in `FAIL` state.
  If this number is not zero the node is not able to serve queries unless
  `cluster-require-full-coverage` is set to `no` in the configuration.
- `cluster_known_nodes`: The total number of known nodes in the cluster,
  including nodes in `HANDSHAKE` state that may not currently be proper members
  of the cluster.
- `cluster_size`: The number of master nodes serving at least one hash slot in
  the cluster.
- `cluster_current_epoch`: The local `Current Epoch` variable. This is used in
  order to create unique increasing version numbers during fail overs.
- `cluster_my_epoch`: The `Config Epoch` of the node we are talking with. This
  is the current configuration version assigned to this node.
- `cluster_stats_messages_sent`: Number of messages sent via the cluster
  node-to-node binary bus.
- `cluster_stats_messages_received`: Number of messages received via the cluster
  node-to-node binary bus.

More information about the Current Epoch and Config Epoch variables are
available in the Redis Cluster specification document.

@return

@bulk-string-reply: A map between named fields and values in the form of
`<field>:<value>` lines separated by newlines composed by the two bytes `CRLF`.
