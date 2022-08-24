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
The slots field would therefor be represented by the following list of integers.

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

@return

@array-reply: nested list of a map of hash ranges and shard nodes.

@examples

```
> CLUSTER SHARDS
1) 1) "slots"
   2) 1) (integer) 10923
      2) (integer) 11110
      3) (integer) 11113
      4) (integer) 16111
      5) (integer) 16113
      6) (integer) 16383
   3) "nodes"
   4) 1)  1) "id"
          2) "71f058078c142a73b94767a4e78e9033d195dfb4"
          3) "port"
          4) (integer) 6381
          5) "ip"
          6) "127.0.0.1"
          7) "role"
          8) "primary"
          9) "replication-offset"
         10) (integer) 1500
         11) "health"
         12) "online"
      2)  1) "id"
          2) "1461967c62eab0e821ed54f2c98e594fccfd8736"
          3) "port"
          4) (integer) 7381
          5) "ip"
          6) "127.0.0.1"
          7) "role"
          8) "replica"
          9) "replication-offset"
         10) (integer) 700
         11) "health"
         12) "fail"
2) 1) "slots"
   2) 1) (integer) 5461
      2) (integer) 10922
   3) "nodes"
   4) 1)  1) "id"
          2) "9215e30cd4a71070088778080565de6ef75fd459"
          3) "port"
          4) (integer) 6380
          5) "ip"
          6) "127.0.0.1"
          7) "role"
          8) "primary"
          9) "replication-offset"
         10) (integer) 1200
         11) "health"
         12) "online"
      2)  1) "id"
          2) "877fa59da72cb902d0563d3d8def3437fc3a0196"
          3) "port"
          4) (integer) 7380
          5) "ip"
          6) "127.0.0.1"
          7) "role"
          8) "replica"
          9) "replication-offset"
         10) (integer) 1100
         11) "health"
         12) "loading"
3) 1) "slots"
   2) 1) (integer) 0
      2) (integer) 5460
      3) (integer) 11111
      4) (integer) 11112
      3) (integer) 16112
      4) (integer) 16112
   3) "nodes"
   4) 1)  1) "id"
          2) "b7e9acc0def782aabe6b596f67f06c73c2ffff93"
          3) "port"
          4) (integer) 7379
          5) "ip"
          6) "127.0.0.1"
          7) "hostname"
          8) "example.com"
          9) "role"
         10) "replica"
         11) "replication-offset"
         12) "primary"
         13) "health"
         14) "online"
      2)  1) "id"
          2) "e2acf1a97c055fd09dcc2c0dcc62b19a6905dbc8"
          3) "port"
          4) (integer) 6379
          5) "ip"
          6) "127.0.0.1"
          7) "hostname"
          8) "example.com"
          9) "role"
         10) "replica"
         11) "replication-offset"
         12) (integer) 0
         13) "health"
         14) "loading"
```