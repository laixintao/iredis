`CLUSTER SLOTS` returns details about which cluster slots map to which Redis instances. 
The command is suitable to be used by Redis Cluster client libraries implementations in order to retrieve (or update when a redirection is received) the map associating cluster *hash slots* with actual nodes network information, so that when a command is received, it can be sent to what is likely the right instance for the keys specified in the command. 

The networking information for each node is an array containing the following elements:

* Preferred endpoint (Either an IP address, hostname, or NULL)
* Port number
* The node ID
* A map of additional networking metadata

The preferred endpoint, along with the port, defines the location that clients should use to send requests for a given slot.
A NULL value for the endpoint indicates the node has an unknown endpoint and the client should connect to the same endpoint it used to send the `CLUSTER SLOTS` command but with the port returned from the command.
This unknown endpoint configuration is useful when the Redis nodes are behind a load balancer that Redis doesn't know the endpoint of.
Which endpoint is set as preferred is determined by the `cluster-preferred-endpoint-type` config.

Additional networking metadata is provided as a map on the fourth argument for each node. 
The following networking metadata may be returned:

* IP: When the preferred endpoint is not set to IP.
* Hostname: When a node has an announced hostname but the primary endpoint is not set to hostname.

## Nested Result Array
Each nested result is:

  - Start slot range
  - End slot range
  - Master for slot range represented as nested networking information
  - First replica of master for slot range
  - Second replica
  - ...continues until all replicas for this master are returned.

Each result includes all active replicas of the master instance
for the listed slot range.  Failed replicas are not returned.

The third nested reply is guaranteed to be the networking information of the master instance for the slot range.
All networking information after the third nested reply are replicas of the master.

If a cluster instance has non-contiguous slots (e.g. 1-400,900,1800-6000) then master and replica networking information results will be duplicated for each top-level slot range reply.

@return

@array-reply: nested list of slot ranges with networking information.

@examples

```
> CLUSTER SLOTS
1) 1) (integer) 0
   2) (integer) 5460
   3) 1) "127.0.0.1"
      2) (integer) 30001
      3) "09dbe9720cda62f7865eabc5fd8857c5d2678366"
      4) 1) hostname
         2) "host-1.redis.example.com"
   4) 1) "127.0.0.1"
      2) (integer) 30004
      3) "821d8ca00d7ccf931ed3ffc7e3db0599d2271abf"
      4) 1) hostname
         2) "host-2.redis.example.com"
2) 1) (integer) 5461
   2) (integer) 10922
   3) 1) "127.0.0.1"
      2) (integer) 30002
      3) "c9d93d9f2c0c524ff34cc11838c2003d8c29e013"
      4) 1) hostname
         2) "host-3.redis.example.com"
   4) 1) "127.0.0.1"
      2) (integer) 30005
      3) "faadb3eb99009de4ab72ad6b6ed87634c7ee410f"
      4) 1) hostname
         2) "host-4.redis.example.com"
3) 1) (integer) 10923
   2) (integer) 16383
   3) 1) "127.0.0.1"
      2) (integer) 30003
      3) "044ec91f325b7595e76dbcb18cc688b6a5b434a1"
      4) 1) hostname
         2) "host-5.redis.example.com"
   4) 1) "127.0.0.1"
      2) (integer) 30006
      3) "58e6e48d41228013e5d9c1c37c5060693925e97e"
      4) 1) hostname
         2) "host-6.redis.example.com"
```

**Warning:** In future versions there could be more elements describing the node better.
In general a client implementation should just rely on the fact that certain parameters are at fixed positions as specified, but more parameters may follow and should be ignored.
Similarly a client library should try if possible to cope with the fact that older versions may just have the primary endpoint and port parameter.

## Behavior change history

*   `>= 7.0.0`: Added support for hostnames and unknown endpoints in first field of node response.