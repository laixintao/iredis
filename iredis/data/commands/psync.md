Initiates a replication stream from the master.

The `PSYNC` command is called by Redis replicas for initiating a replication
stream from the master.

For more information about replication in Redis please check the [replication
page][tr].

[tr]: /topics/replication

@return

**Non standard return value**, a bulk transfer of the data followed by `PING`
and write requests from the master.
