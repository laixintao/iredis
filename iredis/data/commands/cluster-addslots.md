This command is useful in order to modify a node's view of the cluster
configuration. Specifically it assigns a set of hash slots to the node receiving
the command. If the command is successful, the node will map the specified hash
slots to itself, and will start broadcasting the new configuration.

However note that:

1. The command only works if all the specified slots are, from the point of view
   of the node receiving the command, currently not assigned. A node will refuse
   to take ownership for slots that already belong to some other node (including
   itself).
2. The command fails if the same slot is specified multiple times.
3. As a side effect of the command execution, if a slot among the ones specified
   as argument is set as `importing`, this state gets cleared once the node
   assigns the (previously unbound) slot to itself.

## Example

For example the following command assigns slots 1 2 3 to the node receiving the
command:

    > CLUSTER ADDSLOTS 1 2 3
    OK

However trying to execute it again results into an error since the slots are
already assigned:

    > CLUSTER ADDSLOTS 1 2 3
    ERR Slot 1 is already busy

## Usage in Redis Cluster

This command only works in cluster mode and is useful in the following Redis
Cluster operations:

1. To create a new cluster ADDSLOTS is used in order to initially setup master
   nodes splitting the available hash slots among them.
2. In order to fix a broken cluster where certain slots are unassigned.

## Information about slots propagation and warnings

Note that once a node assigns a set of slots to itself, it will start
propagating this information in heartbeat packet headers. However the other
nodes will accept the information only if they have the slot as not already
bound with another node, or if the configuration epoch of the node advertising
the new hash slot, is greater than the node currently listed in the table.

This means that this command should be used with care only by applications
orchestrating Redis Cluster, like `redis-trib`, and the command if used out of
the right context can leave the cluster in a wrong state or cause data loss.

@return

@simple-string-reply: `OK` if the command was successful. Otherwise an error is
returned.
