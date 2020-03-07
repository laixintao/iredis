The PUBSUB command is an introspection command that allows to inspect the state
of the Pub/Sub subsystem. It is composed of subcommands that are documented
separately. The general form is:

    PUBSUB <subcommand> ... args ...

# PUBSUB CHANNELS [pattern]

Lists the currently _active channels_. An active channel is a Pub/Sub channel
with one or more subscribers (not including clients subscribed to patterns).

If no `pattern` is specified, all the channels are listed, otherwise if pattern
is specified only channels matching the specified glob-style pattern are listed.

@return

@array-reply: a list of active channels, optionally matching the specified
pattern.

# `PUBSUB NUMSUB [channel-1 ... channel-N]`

Returns the number of subscribers (not counting clients subscribed to patterns)
for the specified channels.

@return

@array-reply: a list of channels and number of subscribers for every channel.
The format is channel, count, channel, count, ..., so the list is flat. The
order in which the channels are listed is the same as the order of the channels
specified in the command call.

Note that it is valid to call this command without channels. In this case it
will just return an empty list.

# `PUBSUB NUMPAT`

Returns the number of subscriptions to patterns (that are performed using the
`PSUBSCRIBE` command). Note that this is not just the count of clients
subscribed to patterns but the total number of patterns all the clients are
subscribed to.

@return

@integer-reply: the number of patterns all the clients are subscribed to.
