Each node in a Redis Cluster maintains a pair of long-lived TCP link with each peer in the cluster: One for sending outbound messages towards the peer and one for receiving inbound messages from the peer.

`CLUSTER LINKS` outputs information of all such peer links as an array, where each array element is a map that contains attributes and their values for an individual link.

@examples

The following is an example output:

```
> CLUSTER LINKS
1)  1) "direction"
    2) "to"
    3) "node"
    4) "8149d745fa551e40764fecaf7cab9dbdf6b659ae"
    5) "create-time"
    6) (integer) 1639442739375
    7) "events"
    8) "rw"
    9) "send-buffer-allocated"
   10) (integer) 4512
   11) "send-buffer-used"
   12) (integer) 0
2)  1) "direction"
    2) "from"
    3) "node"
    4) "8149d745fa551e40764fecaf7cab9dbdf6b659ae"
    5) "create-time"
    6) (integer) 1639442739411
    7) "events"
    8) "r"
    9) "send-buffer-allocated"
   10) (integer) 0
   11) "send-buffer-used"
   12) (integer) 0
```

Each map is composed of the following attributes of the corresponding cluster link and their values:

1. `direction`: This link is established by the local node `to` the peer, or accepted by the local node `from` the peer.
2. `node`: The node id of the peer.
3. `create-time`: Creation time of the link. (In the case of a `to` link, this is the time when the TCP link is created by the local node, not the time when it is actually established.)
4. `events`: Events currently registered for the link. `r` means readable event, `w` means writable event.
5. `send-buffer-allocated`: Allocated size of the link's send buffer, which is used to buffer outgoing messages toward the peer.
6. `send-buffer-used`: Size of the portion of the link's send buffer that is currently holding data(messages).

@return

@array-reply: An array of maps where each map contains various attributes and their values of a cluster link.
