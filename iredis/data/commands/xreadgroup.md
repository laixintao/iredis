The `XREADGROUP` command is a special version of the `XREAD` command with
support for consumer groups. Probably you will have to understand the `XREAD`
command before reading this page will makes sense.

Moreover, if you are new to streams, we recommend to read our
[introduction to Redis Streams](/topics/streams-intro). Make sure to understand
the concept of consumer group in the introduction so that following how this
command works will be simpler.

## Consumer groups in 30 seconds

The difference between this command and the vanilla `XREAD` is that this one
supports consumer groups.

Without consumer groups, just using `XREAD`, all the clients are served with all
the entries arriving in a stream. Instead using consumer groups with
`XREADGROUP`, it is possible to create groups of clients that consume different
parts of the messages arriving in a given stream. If, for instance, the stream
gets the new entries A, B, and C and there are two consumers reading via a
consumer group, one client will get, for instance, the messages A and C, and the
other the message B, and so forth.

Within a consumer group, a given consumer (that is, just a client consuming
messages from the stream), has to identify with an unique _consumer name_. Which
is just a string.

One of the guarantees of consumer groups is that a given consumer can only see
the history of messages that were delivered to it, so a message has just a
single owner. However there is a special feature called _message claiming_ that
allows other consumers to claim messages in case there is a non recoverable
failure of some consumer. In order to implement such semantics, consumer groups
require explicit acknowledgement of the messages successfully processed by the
consumer, via the `XACK` command. This is needed because the stream will track,
for each consumer group, who is processing what message.

This is how to understand if you want to use a consumer group or not:

1. If you have a stream and multiple clients, and you want all the clients to
   get all the messages, you do not need a consumer group.
2. If you have a stream and multiple clients, and you want the stream to be
   _partitioned_ or _sharded_ across your clients, so that each client will get
   a sub set of the messages arriving in a stream, you need a consumer group.

## Differences between XREAD and XREADGROUP

From the point of view of the syntax, the commands are almost the same, however
`XREADGROUP` _requires_ a special and mandatory option:

    GROUP <group-name> <consumer-name>

The group name is just the name of a consumer group associated to the stream.
The group is created using the `XGROUP` command. The consumer name is the string
that is used by the client to identify itself inside the group. The consumer is
auto created inside the consumer group the first time it is saw. Different
clients should select a different consumer name.

When you read with `XREADGROUP`, the server will _remember_ that a given message
was delivered to you: the message will be stored inside the consumer group in
what is called a Pending Entries List (PEL), that is a list of message IDs
delivered but not yet acknowledged.

The client will have to acknowledge the message processing using `XACK` in order
for the pending entry to be removed from the PEL. The PEL can be inspected using
the `XPENDING` command.

The `NOACK` subcommand can be used to avoid adding the message to the PEL in
cases where reliability is not a requirement and the occasional message loss is
acceptable. This is equivalent to acknowledging the message when it is read.

The ID to specify in the **STREAMS** option when using `XREADGROUP` can be one
of the following two:

- The special `>` ID, which means that the consumer want to receive only
  messages that were _never delivered to any other consumer_. It just means,
  give me new messages.
- Any other ID, that is, 0 or any other valid ID or incomplete ID (just the
  millisecond time part), will have the effect of returning entries that are
  pending for the consumer sending the command with IDs greater than the one
  provided. So basically if the ID is not `>`, then the command will just let
  the client access its pending entries: messages delivered to it, but not yet
  acknowledged. Note that in this case, both `BLOCK` and `NOACK` are ignored.

Like `XREAD` the `XREADGROUP` command can be used in a blocking way. There are
no differences in this regard.

## What happens when a message is delivered to a consumer?

Two things:

1. If the message was never delivered to anyone, that is, if we are talking
   about a new message, then a PEL (Pending Entry List) is created.
2. If instead the message was already delivered to this consumer, and it is just
   re-fetching the same message again, then the _last delivery counter_ is
   updated to the current time, and the _number of deliveries_ is incremented by
   one. You can access those message properties using the `XPENDING` command.

## Usage example

Normally you use the command like that in order to get new messages and process
them. In pseudo-code:

```
WHILE true
    entries = XREADGROUP GROUP $GroupName $ConsumerName BLOCK 2000 COUNT 10 STREAMS mystream >
    if entries == nil
        puts "Timeout... try again"
        CONTINUE
    end

    FOREACH entries AS stream_entries
        FOREACH stream_entries as message
            process_message(message.id,message.fields)

            # ACK the message as processed
            XACK mystream $GroupName message.id
        END
    END
END
```

In this way the example consumer code will fetch only new messages, process
them, and acknowledge them via `XACK`. However the example code above is not
complete, because it does not handle recovering after a crash. What will happen
if we crash in the middle of processing messages, is that our messages will
remain in the pending entries list, so we can access our history by giving
`XREADGROUP` initially an ID of 0, and performing the same loop. Once providing
an ID of 0 the reply is an empty set of messages, we know that we processed and
acknowledged all the pending messages: we can start to use `>` as ID, in order
to get the new messages and rejoin the consumers that are processing new things.

To see how the command actually replies, please check the `XREAD` command page.
