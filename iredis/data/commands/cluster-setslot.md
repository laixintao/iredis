`CLUSTER SETSLOT` is responsible of changing the state of a hash slot in the
receiving node in different ways. It can, depending on the subcommand used:

1. `MIGRATING` subcommand: Set a hash slot in _migrating_ state.
2. `IMPORTING` subcommand: Set a hash slot in _importing_ state.
3. `STABLE` subcommand: Clear any importing / migrating state from hash slot.
4. `NODE` subcommand: Bind the hash slot to a different node.

The command with its set of subcommands is useful in order to start and end
cluster live resharding operations, which are accomplished by setting a hash
slot in migrating state in the source node, and importing state in the
destination node.

Each subcommand is documented below. At the end you'll find a description of how
live resharding is performed using this command and other related commands.

## CLUSTER SETSLOT `<slot>` MIGRATING `<destination-node-id>`

This subcommand sets a slot to _migrating_ state. In order to set a slot in this
state, the node receiving the command must be the hash slot owner, otherwise an
error is returned.

When a slot is set in migrating state, the node changes behavior in the
following way:

1. If a command is received about an existing key, the command is processed as
   usually.
2. If a command is received about a key that does not exists, an `ASK`
   redirection is emitted by the node, asking the client to retry only that
   specific query into `destination-node`. In this case the client should not
   update its hash slot to node mapping.
3. If the command contains multiple keys, in case none exist, the behavior is
   the same as point 2, if all exist, it is the same as point 1, however if only
   a partial number of keys exist, the command emits a `TRYAGAIN` error in order
   for the keys interested to finish being migrated to the target node, so that
   the multi keys command can be executed.

## CLUSTER SETSLOT `<slot>` IMPORTING `<source-node-id>`

This subcommand is the reverse of `MIGRATING`, and prepares the destination node
to import keys from the specified source node. The command only works if the
node is not already owner of the specified hash slot.

When a slot is set in importing state, the node changes behavior in the
following way:

1. Commands about this hash slot are refused and a `MOVED` redirection is
   generated as usually, but in the case the command follows an `ASKING`
   command, in this case the command is executed.

In this way when a node in migrating state generates an `ASK` redirection, the
client contacts the target node, sends `ASKING`, and immediately after sends the
command. This way commands about non-existing keys in the old node or keys
already migrated to the target node are executed in the target node, so that:

1. New keys are always created in the target node. During a hash slot migration
   we'll have to move only old keys, not new ones.
2. Commands about keys already migrated are correctly processed in the context
   of the node which is the target of the migration, the new hash slot owner, in
   order to guarantee consistency.
3. Without `ASKING` the behavior is the same as usually. This guarantees that
   clients with a broken hash slots mapping will not write for error in the
   target node, creating a new version of a key that has yet to be migrated.

## CLUSTER SETSLOT `<slot>` STABLE

This subcommand just clears migrating / importing state from the slot. It is
mainly used to fix a cluster stuck in a wrong state by `redis-trib fix`.
Normally the two states are cleared automatically at the end of the migration
using the `SETSLOT ... NODE ...` subcommand as explained in the next section.

## CLUSTER SETSLOT `<slot>` NODE `<node-id>`

The `NODE` subcommand is the one with the most complex semantics. It associates
the hash slot with the specified node, however the command works only in
specific situations and has different side effects depending on the slot state.
The following is the set of pre-conditions and side effects of the command:

1. If the current hash slot owner is the node receiving the command, but for
   effect of the command the slot would be assigned to a different node, the
   command will return an error if there are still keys for that hash slot in
   the node receiving the command.
2. If the slot is in _migrating_ state, the state gets cleared when the slot is
   assigned to another node.
3. If the slot was in _importing_ state in the node receiving the command, and
   the command assigns the slot to this node (which happens in the target node
   at the end of the resharding of a hash slot from one node to another), the
   command has the following side effects: A) the _importing_ state is cleared.
   B) If the node config epoch is not already the greatest of the cluster, it
   generates a new one and assigns the new config epoch to itself. This way its
   new hash slot ownership will win over any past configuration created by
   previous failovers or slot migrations.

It is important to note that step 3 is the only time when a Redis Cluster node
will create a new config epoch without agreement from other nodes. This only
happens when a manual configuration is operated. However it is impossible that
this creates a non-transient setup where two nodes have the same config epoch,
since Redis Cluster uses a config epoch collision resolution algorithm.

@return

@simple-string-reply: All the subcommands return `OK` if the command was
successful. Otherwise an error is returned.

## Redis Cluster live resharding explained

The `CLUSTER SETSLOT` command is an important piece used by Redis Cluster in
order to migrate all the keys contained in one hash slot from one node to
another. This is how the migration is orchestrated, with the help of other
commands as well. We'll call the node that has the current ownership of the hash
slot the `source` node, and the node where we want to migrate the `destination`
node.

1. Set the destination node slot to _importing_ state using
   `CLUSTER SETSLOT <slot> IMPORTING <source-node-id>`.
2. Set the source node slot to _migrating_ state using
   `CLUSTER SETSLOT <slot> MIGRATING <destination-node-id>`.
3. Get keys from the source node with `CLUSTER GETKEYSINSLOT` command and move
   them into the destination node using the `MIGRATE` command.
4. Use `CLUSTER SETSLOT <slot> NODE <destination-node-id>` in the source or
   destination.

Notes:

- The order of step 1 and 2 is important. We want the destination node to be
  ready to accept `ASK` redirections when the source node is configured to
  redirect.
- Step 4 does not technically need to use `SETSLOT` in the nodes not involved in
  the resharding, since the configuration will eventually propagate itself,
  however it is a good idea to do so in order to stop nodes from pointing to the
  wrong node for the hash slot moved as soon as possible, resulting in less
  redirections to find the right node.
