Forces a node to save the `nodes.conf` configuration on disk. Before to return
the command calls `fsync(2)` in order to make sure the configuration is flushed
on the computer disk.

This command is mainly used in the event a `nodes.conf` node state file gets
lost / deleted for some reason, and we want to generate it again from scratch.
It can also be useful in case of mundane alterations of a node cluster
configuration via the `CLUSTER` command in order to ensure the new configuration
is persisted on disk, however all the commands should normally be able to auto
schedule to persist the configuration on disk when it is important to do so for
the correctness of the system in the event of a restart.

@return

@simple-string-reply: `OK` or an error if the operation fails.
