Instruct Redis to start an [Append Only File][tpaof] rewrite process. The
rewrite will create a small optimized version of the current Append Only File.

[tpaof]: /topics/persistence#append-only-file

If `BGREWRITEAOF` fails, no data gets lost as the old AOF will be untouched.

The rewrite will be only triggered by Redis if there is not already a background
process doing persistence.

Specifically:

- If a Redis child is creating a snapshot on disk, the AOF rewrite is
  _scheduled_ but not started until the saving child producing the RDB file
  terminates. In this case the `BGREWRITEAOF` will still return an positive
  status reply, but with an appropriate message. You can check if an AOF rewrite
  is scheduled looking at the `INFO` command as of Redis 2.6 or successive
  versions.
- If an AOF rewrite is already in progress the command returns an error and no
  AOF rewrite will be scheduled for a later time.
- If the AOF rewrite could start, but the attempt at starting it fails (for
  instance because of an error in creating the child process), an error is
  returned to the caller.

Since Redis 2.4 the AOF rewrite is automatically triggered by Redis, however the
`BGREWRITEAOF` command can be used to trigger a rewrite at any time.

Please refer to the [persistence documentation][tp] for detailed information.

[tp]: /topics/persistence

@return

@simple-string-reply: A simple string reply indicating that the rewriting
started or is about to start ASAP, when the call is executed with success.

The command may reply with an error in certain cases, as documented above.
