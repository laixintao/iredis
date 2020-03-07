The command behavior is the following:

- Stop all the clients.
- Perform a blocking SAVE if at least one **save point** is configured.
- Flush the Append Only File if AOF is enabled.
- Quit the server.

If persistence is enabled this commands makes sure that Redis is switched off
without the lost of any data. This is not guaranteed if the client uses simply
`SAVE` and then `QUIT` because other clients may alter the DB data between the
two commands.

Note: A Redis instance that is configured for not persisting on disk (no AOF
configured, nor "save" directive) will not dump the RDB file on `SHUTDOWN`, as
usually you don't want Redis instances used only for caching to block on when
shutting down.

## SAVE and NOSAVE modifiers

It is possible to specify an optional modifier to alter the behavior of the
command. Specifically:

- **SHUTDOWN SAVE** will force a DB saving operation even if no save points are
  configured.
- **SHUTDOWN NOSAVE** will prevent a DB saving operation even if one or more
  save points are configured. (You can think of this variant as an hypothetical
  **ABORT** command that just stops the server).

## Conditions where a SHUTDOWN fails

When the Append Only File is enabled the shutdown may fail because the system is
in a state that does not allow to safely immediately persist on disk.

Normally if there is an AOF child process performing an AOF rewrite, Redis will
simply kill it and exit. However there are two conditions where it is unsafe to
do so, and the **SHUTDOWN** command will be refused with an error instead. This
happens when:

- The user just turned on AOF, and the server triggered the first AOF rewrite in
  order to create the initial AOF file. In this context, stopping will result in
  losing the dataset at all: once restarted, the server will potentially have
  AOF enabled without having any AOF file at all.
- A replica with AOF enabled, reconnected with its master, performed a full
  resynchronization, and restarted the AOF file, triggering the initial AOF
  creation process. In this case not completing the AOF rewrite is dangerous
  because the latest dataset received from the master would be lost. The new
  master can actually be even a different instance (if the **REPLICAOF** or
  **SLAVEOF** command was used in order to reconfigure the replica), so it is
  important to finish the AOF rewrite and start with the correct data set
  representing the data set in memory when the server was terminated.

There are conditions when we want just to terminate a Redis instance ASAP,
regardless of what its content is. In such a case, the right combination of
commands is to send a **CONFIG appendonly no** followed by a **SHUTDOWN
NOSAVE**. The first command will turn off the AOF if needed, and will terminate
the AOF rewriting child if there is one active. The second command will not have
any problem to execute since the AOF is no longer enabled.

@return

@simple-string-reply on error. On success nothing is returned since the server
quits and the connection is closed.
