The `CLUSTER ADDSLOTSRANGE` is similar to the `CLUSTER ADDSLOTS` command in that they both assign hash slots to nodes.

The difference between the two commands is that `ADDSLOTS` takes a list of slots to assign to the node, while `ADDSLOTSRANGE` takes a list of slot ranges (specified by start and end slots) to assign to the node.

## Example

To assign slots 1 2 3 4 5 to the node, the `ADDSLOTS` command is:

    > CLUSTER ADDSLOTS 1 2 3 4 5
    OK

The same operation can be completed with the following `ADDSLOTSRANGE` command:

    > CLUSTER ADDSLOTSRANGE 1 5
    OK


## Usage in Redis Cluster

This command only works in cluster mode and is useful in the following Redis Cluster operations:

1. To create a new cluster ADDSLOTSRANGE is used in order to initially setup master nodes splitting the available hash slots among them.
2. In order to fix a broken cluster where certain slots are unassigned.

@return

@simple-string-reply: `OK` if the command was successful. Otherwise an error is returned.
