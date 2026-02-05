`CLUSTER SHARDS` returns details about the shards of the cluster.
A shard is defined as a collection of nodes that serve the same set of slots and that replicate from each other.
A shard may only have a single master at a given time, but may have multiple or no replicas.
It is possible for a shard to not be serving any slots while still having replicas.

This command replaces the `CLUSTER SLOTS` command, by providing a more efficient and extensible representation of the cluster. 

The command is suitable to be used by Redis Cluster client libraries in order to understand the topology of the cluster.
A client should issue this command on startup in order to retrieve the map associating cluster *hash slots* with actual node information.
This map should be used to direct commands to the node that is likely serving the slot associated with a given command.
In the event the command is sent to the wrong node, in that it received a '-MOVED' redirect, this command can then be used to update the topology of the cluster.

The command returns an array of shards, with each shard containing two fields, 'slots' and 'nodes'. 

The 'slots' field is a list of slot ranges served by this shard, stored as pair of integers representing the inclusive start and end slots of the ranges.
For example, if a node owns the slots 1, 2, 3, 5, 7, 8 and 9, the slots ranges would be stored as [1-3], [5-5], [7-9].
The slots field would therefore be represented by the following list of integers.

```
1) 1) "slots"
   2) 1) (integer) 1
      2) (integer) 3
      3) (integer) 5
      4) (integer) 5
      5) (integer) 7
      6) (integer) 9
```

The 'nodes' field contains a list of all nodes within the shard.
Each individual node is a map of attributes that describe the node. 
Some attributes are optional and more attributes may be added in the future. 
The current list of attributes:

* id: The unique node id for this particular node.
* endpoint: The preferred endpoint to reach the node, see below for more information about the possible values of this field.
* ip: The IP address to send requests to for this node.
* hostname (optional): The announced hostname to send requests to for this node.
* port (optional): The TCP (non-TLS) port of the node. At least one of port or tls-port will be present.
* tls-port (optional): The TLS port of the node. At least one of port or tls-port will be present.
* role: The replication role of this node.
* replication-offset: The replication offset of this node. This information can be used to send commands to the most up to date replicas.
* health: Either `online`, `failed`, or `loading`. This information should be used to determine which nodes should be sent traffic. The `loading` health state should be used to know that a node is not currently eligible to serve traffic, but may be eligible in the future. 

The endpoint, along with the port, defines the location that clients should use to send requests for a given slot.
A NULL value for the endpoint indicates the node has an unknown endpoint and the client should connect to the same endpoint it used to send the `CLUSTER SHARDS` command but with the port returned from the command.
This unknown endpoint configuration is useful when the Redis nodes are behind a load balancer that Redis doesn't know the endpoint of.
Which endpoint is set is determined by the `cluster-preferred-endpoint-type` config.
An empty string `""` is another abnormal value of the endpoint field, as well as for the ip field, which is returned if the node doesn't know its own IP address.
This can happen in a cluster that consists of only one node or the node has not yet been joined with the rest of the cluster.
The value `?` is displayed if the node is incorrectly configured to use announced hostnames but no hostname is configured using `cluster-announce-hostname`.
Clients may treat the empty string in the same way as NULL, that is the same endpoint it used to send the current command to, while `"?"` should be treated as an unknown node, not necessarily the same node as the one serving the current command.

@return

@array-reply: nested list of a map of hash ranges and shard nodes.

@examples

```
> CLUSTER SHARDS
1) 1) "slots"
   2) 1) (integer) 0
      2) (integer) 5460
   3) "nodes"
   4) 1)  1) "id"
          2) "e10b7051d6bf2d5febd39a2be297bbaea6084111"
          3) "port"
          4) (integer) 30001
          5) "ip"
          6) "127.0.0.1"
          7) "endpoint"
          8) "127.0.0.1"
          9) "role"
         10) "master"
         11) "replication-offset"
         12) (integer) 72156
         13) "health"
         14) "online"
      2)  1) "id"
          2) "1901f5962d865341e81c85f9f596b1e7160c35ce"
          3) "port"
          4) (integer) 30006
          5) "ip"
          6) "127.0.0.1"
          7) "endpoint"
          8) "127.0.0.1"
          9) "role"
         10) "replica"
         11) "replication-offset"
         12) (integer) 72156
         13) "health"
         14) "online"
2) 1) "slots"
   2) 1) (integer) 10923
      2) (integer) 16383
   3) "nodes"
   4) 1)  1) "id"
          2) "fd20502fe1b32fc32c15b69b0a9537551f162f1f"
          3) "port"
          4) (integer) 30003
          5) "ip"
          6) "127.0.0.1"
          7) "endpoint"
          8) "127.0.0.1"
          9) "role"
         10) "master"
         11) "replication-offset"
         12) (integer) 72156
         13) "health"
         14) "online"
      2)  1) "id"
          2) "6daa25c08025a0c7e4cc0d1ab255949ce6cee902"
          3) "port"
          4) (integer) 30005
          5) "ip"
          6) "127.0.0.1"
          7) "endpoint"
          8) "127.0.0.1"
          9) "role"
         10) "replica"
         11) "replication-offset"
         12) (integer) 72156
         13) "health"
         14) "online"
3) 1) "slots"
   2) 1) (integer) 5461
      2) (integer) 10922
   3) "nodes"
   4) 1)  1) "id"
          2) "a4a3f445ead085eb3eb9ee7d8c644ec4481ec9be"
          3) "port"
          4) (integer) 30002
          5) "ip"
          6) "127.0.0.1"
          7) "endpoint"
          8) "127.0.0.1"
          9) "role"
         10) "master"
         11) "replication-offset"
         12) (integer) 72156
         13) "health"
         14) "online"
      2)  1) "id"
          2) "da6d5847aa019e9b9d2a8aa24a75f856fd3456cc"
          3) "port"
          4) (integer) 30004
          5) "ip"
          6) "127.0.0.1"
          7) "endpoint"
          8) "127.0.0.1"
          9) "role"
         10) "replica"
         11) "replication-offset"
         12) (integer) 72156
         13) "health"
         14) "online"
```
