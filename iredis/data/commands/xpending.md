Fetching data from a stream via a consumer group, and not acknowledging such
data, has the effect of creating _pending entries_. This is well explained in
the `XREADGROUP` command, and even better in our
[introduction to Redis Streams](/topics/streams-intro). The `XACK` command will
immediately remove the pending entry from the Pending Entry List (PEL) since
once a message is successfully processed, there is no longer need for the
consumer group to track it and to remember the current owner of the message.

The `XPENDING` command is the interface to inspect the list of pending messages,
and is as thus a very important command in order to observe and understand what
is happening with a streams consumer groups: what clients are active, what
messages are pending to be consumed, or to see if there are idle messages.
Moreover this command, together with `XCLAIM` is used in order to implement
recovering of consumers that are failing for a long time, and as a result
certain messages are not processed: a different consumer can claim the message
and continue. This is better explained in the
[streams intro](/topics/streams-intro) and in the `XCLAIM` command page, and is
not covered here.

## Summary form of XPENDING

When `XPENDING` is called with just a key name and a consumer group name, it
just outputs a summary about the pending messages in a given consumer group. In
the following example, we create a consumer group and immediately create a
pending message by reading from the group with `XREADGROUP`.

```
> XGROUP CREATE mystream group55 0-0
OK

> XREADGROUP GROUP group55 consumer-123 COUNT 1 STREAMS mystream >
1) 1) "mystream"
   2) 1) 1) 1526984818136-0
         2) 1) "duration"
            2) "1532"
            3) "event-id"
            4) "5"
            5) "user-id"
            6) "7782813"
```

We expect the pending entries list for the consumer group `group55` to have a
message right now: consumer named `consumer-123` fetched the message without
acknowledging its processing. The simple `XPENDING` form will give us this
information:

```
> XPENDING mystream group55
1) (integer) 1
2) 1526984818136-0
3) 1526984818136-0
4) 1) 1) "consumer-123"
      2) "1"
```

In this form, the command outputs the total number of pending messages for this
consumer group, which is one, followed by the smallest and greatest ID among the
pending messages, and then list every consumer in the consumer group with at
least one pending message, and the number of pending messages it has.

This is a good overview, but sometimes we are interested in the details. In
order to see all the pending messages with more associated information we need
to also pass a range of IDs, in a similar way we do it with `XRANGE`, and a non
optional _count_ argument, to limit the number of messages returned per call:

```
> XPENDING mystream group55 - + 10
1) 1) 1526984818136-0
   2) "consumer-123"
   3) (integer) 196415
   4) (integer) 1
```

In the extended form we no longer see the summary information, instead there are
detailed information for each message in the pending entries list. For each
message four attributes are returned:

1. The ID of the message.
2. The name of the consumer that fetched the message and has still to
   acknowledge it. We call it the current _owner_ of the message.
3. The number of milliseconds that elapsed since the last time this message was
   delivered to this consumer.
4. The number of times this message was delivered.

The deliveries counter, that is the fourth element in the array, is incremented
when some other consumer _claims_ the message with `XCLAIM`, or when the message
is delivered again via `XREADGROUP`, when accessing the history of a consumer in
a consumer group (see the `XREADGROUP` page for more info).

Finally it is possible to pass an additional argument to the command, in order
to see the messages having a specific owner:

```
> XPENDING mystream group55 - + 10 consumer-123
```

But in the above case the output would be the same, since we have pending
messages only for a single consumer. However what is important to keep in mind
is that this operation, filtering by a specific consumer, is not inefficient
even when there are many pending messages from many consumers: we have a pending
entries list data structure both globally, and for every consumer, so we can
very efficiently show just messages pending for a single consumer.

@return

@array-reply, specifically:

The command returns data in different format depending on the way it is called,
as previously explained in this page. However the reply is always an array of
items.
