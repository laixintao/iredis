The command behavior is the following:

* If there are any replicas lagging behind in replication:
  * Pause clients attempting to write by performing a `CLIENT PAUSE` with the `WRITE` option.
  * Wait up to the configured `shutdown-timeout` (default 10 seconds) for replicas to catch up the replication offset.
* Stop all the clients.
* Perform a blocking SAVE if at least one **save point** is configured.
* Flush the Append Only File if AOF is enabled.
* Quit the server.

If persistence is enabled this commands makes sure that Redis is switched off
without any data loss.

Note: A Redis instance that is configured for not persisting on disk (no AOF
configured, nor "save" directive) will not dump the RDB file on `SHUTDOWN`, as
usually you don't want Redis instances used only for caching to block on when
shutting down.

Also note: If Redis receives one of the signals `SIGTERM` and `SIGINT`, the same shutdown sequence is performed.
See also [Signal Handling](/topics/signals).

## Modifiers

It is possible to specify optional modifiers to alter the behavior of the command.
Specifically:

* **SAVE** will force a DB saving operation even if no save points are configured.
* **NOSAVE** will prevent a DB saving operation even if one or more save points are configured.
* **NOW** skips waiting for lagging replicas, i.e. it bypasses the first step in the shutdown sequence.
* **FORCE** ignores any errors that would normally prevent the server from exiting.
  For details, see the following section.
* **ABORT** cancels an ongoing shutdown and cannot be combined with other flags.

## Conditions where a SHUTDOWN fails

When a save point is configured or the **SAVE** modifier is specified, the shutdown may fail if the RDB file can't be saved.
Then, the server continues to run in order to ensure no data loss.
This may be bypassed using the **FORCE** modifier, causing the server to exit anyway.

When the Append Only File is enabled the shutdown may fail because the
system is in a state that does not allow to safely immediately persist
on disk.

Normally if there is an AOF child process performing an AOF rewrite, Redis
will simply kill it and exit.
However, there are situations where it is unsafe to do so and, unless the **FORCE** modifier is specified, the **SHUTDOWN** command will be refused with an error instead.
This happens in the following situations:

* The user just turned on AOF, and the server triggered the first AOF rewrite in order to create the initial AOF file. In this context, stopping will result in losing the dataset at all: once restarted, the server will potentially have AOF enabled without having any AOF file at all.
* A replica with AOF enabled, reconnected with its master, performed a full resynchronization, and restarted the AOF file, triggering the initial AOF creation process. In this case not completing the AOF rewrite is dangerous because the latest dataset received from the master would be lost. The new master can actually be even a different instance (if the **REPLICAOF** or **SLAVEOF** command was used in order to reconfigure the replica), so it is important to finish the AOF rewrite and start with the correct data set representing the data set in memory when the server was terminated.

There are situations when we want just to terminate a Redis instance ASAP, regardless of what its content is.
In such a case, the command **SHUTDOWN NOW NOSAVE FORCE** can be used.
In versions before 7.0, where the **NOW** and **FORCE** flags are not available, the right combination of commands is to send a **CONFIG appendonly no** followed by a **SHUTDOWN NOSAVE**.
The first command will turn off the AOF if needed, and will terminate the AOF rewriting child if there is one active.
The second command will not have any problem to execute since the AOF is no longer enabled.

## Minimize the risk of data loss

Since Redis 7.0, the server waits for lagging replicas up to a configurable `shutdown-timeout`, by default 10 seconds, before shutting down.
This provides a best effort minimizing the risk of data loss in a situation where no save points are configured and AOF is disabled.
Before version 7.0, shutting down a heavily loaded master node in a diskless setup was more likely to result in data loss.
To minimize the risk of data loss in such setups, it's advised to trigger a manual `FAILOVER` (or `CLUSTER FAILOVER`) to demote the master to a replica and promote one of the replicas to be the new master, before shutting down a master node.

@return

@simple-string-reply: `OK` if `ABORT` was specified and shutdown was aborted.
On successful shutdown, nothing is returned since the server quits and the connection is closed.
On failure, an error is returned.

## Behavior change history

*   `>= 7.0.0`: Introduced waiting for lagging replicas before exiting.