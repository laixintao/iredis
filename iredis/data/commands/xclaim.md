In the context of a stream consumer group, this command changes the ownership of
a pending message, so that the new owner is the consumer specified as the
command argument. Normally this is what happens:

1. There is a stream with an associated consumer group.
2. Some consumer A reads a message via `XREADGROUP` from a stream, in the
   context of that consumer group.
3. As a side effect a pending message entry is created in the pending entries
   list (PEL) of the consumer group: it means the message was delivered to a
   given consumer, but it was not yet acknowledged via `XACK`.
4. Then suddenly that consumer fails forever.
5. Other consumers may inspect the list of pending messages, that are stale for
   quite some time, using the `XPENDING` command. In order to continue
   processing such messages, they use `XCLAIM` to acquire the ownership of the
   message and continue.

This dynamic is clearly explained in the
[Stream intro documentation](/topics/streams-intro).

Note that the message is claimed only if its idle time is greater the minimum
idle time we specify when calling `XCLAIM`. Because as a side effect `XCLAIM`
will also reset the idle time (since this is a new attempt at processing the
message), two consumers trying to claim a message at the same time will never
both succeed: only one will successfully claim the message. This avoids that we
process a given message multiple times in a trivial way (yet multiple processing
is possible and unavoidable in the general case).

Moreover, as a side effect, `XCLAIM` will increment the count of attempted
deliveries of the message unless the `JUSTID` option has been specified (which
only delivers the message ID, not the message itself). In this way messages that
cannot be processed for some reason, for instance because the consumers crash
attempting to process them, will start to have a larger counter and can be
detected inside the system.

## Command options

The command has multiple options, however most are mainly for internal use in
order to transfer the effects of `XCLAIM` or other commands to the AOF file and
to propagate the same effects to the slaves, and are unlikely to be useful to
normal users:

1. `IDLE <ms>`: Set the idle time (last time it was delivered) of the message.
   If IDLE is not specified, an IDLE of 0 is assumed, that is, the time count is
   reset because the message has now a new owner trying to process it.
2. `TIME <ms-unix-time>`: This is the same as IDLE but instead of a relative
   amount of milliseconds, it sets the idle time to a specific Unix time (in
   milliseconds). This is useful in order to rewrite the AOF file generating
   `XCLAIM` commands.
3. `RETRYCOUNT <count>`: Set the retry counter to the specified value. This
   counter is incremented every time a message is delivered again. Normally
   `XCLAIM` does not alter this counter, which is just served to clients when
   the XPENDING command is called: this way clients can detect anomalies, like
   messages that are never processed for some reason after a big number of
   delivery attempts.
4. `FORCE`: Creates the pending message entry in the PEL even if certain
   specified IDs are not already in the PEL assigned to a different client.
   However the message must be exist in the stream, otherwise the IDs of non
   existing messages are ignored.
5. `JUSTID`: Return just an array of IDs of messages successfully claimed,
   without returning the actual message. Using this option means the retry
   counter is not incremented.

@return

@array-reply, specifically:

The command returns all the messages successfully claimed, in the same format as
`XRANGE`. However if the `JUSTID` option was specified, only the message IDs are
reported, without including the actual message.

Example:

```
> XCLAIM mystream mygroup Alice 3600000 1526569498055-0
1) 1) 1526569498055-0
   2) 1) "message"
      2) "orange"
```

In the above example we claim the message with ID `1526569498055-0`, only if the
message is idle for at least one hour without the original consumer or some
other consumer making progresses (acknowledging or claiming it), and assigns the
ownership to the consumer `Alice`.
