This command transfers ownership of pending stream entries that match the
specified criteria. Conceptually, `XAUTOCLAIM` is equivalent to calling
`XPENDING` and then `XCLAIM`, but provides a more straightforward way to deal
with message delivery failures via `SCAN`-like semantics.

Like `XCLAIM`, the command operates on the stream entries at `<key>` and in the
context of the provided `<group>`. It transfers ownership to `<consumer>` of
messages pending for more than `<min-idle-time>` milliseconds and having an
equal or greater ID than `<start>`.

The optional `<count>` argument, which defaults to 100, is the upper limit of
the number of entries that the command attempts to claim. Internally, the
command begins scanning the consumer group's Pending Entries List (PEL) from
`<start>` and filters out entries having an idle time less than or equal to
`<min-idle-time>`. The maximum number of pending entries that the command scans
is the product of multiplying `<count>`'s value by 10 (hard-coded). It is
possible, therefore, that the number of entries claimed will be less than the
specified value.

The optional `JUSTID` argument changes the reply to return just an array of IDs
of messages successfully claimed, without returning the actual message. Using
this option means the retry counter is not incremented.

The command returns the claimed entries as an array. It also returns a stream ID
intended for cursor-like use as the `<start>` argument for its subsequent call.
When there are no remaining PEL entries, the command returns the special `0-0`
ID to signal completion. However, note that you may want to continue calling
`XAUTOCLAIM` even after the scan is complete with the `0-0` as `<start>` ID,
because enough time passed, so older pending entries may now be eligible for
claiming.

Note that only messages that are idle longer than `<min-idle-time>` are claimed,
and claiming a message resets its idle time. This ensures that only a single
consumer can successfully claim a given pending message at a specific instant of
time and trivially reduces the probability of processing the same message
multiple times.

Lastly, claiming a message with `XAUTOCLAIM` also increments the attempted
deliveries count for that message, unless the `JUSTID` option has been specified
(which only delivers the message ID, not the message itself). Messages that
cannot be processed for some reason - for example, because consumers
systematically crash when processing them - will exhibit high attempted delivery
counts that can be detected by monitoring.

@return

@array-reply, specifically:

An array with two elements:

1. The first element is a stream ID to be used as the `<start>` argument for the
   next call to `XAUTOCLAIM`
2. The second element is an array containing all the successfully claimed
   messages in the same format as `XRANGE`.

@examples

```
> XAUTOCLAIM mystream mygroup Alice 3600000 0-0 COUNT 25
1) "0-0"
2) 1) 1) "1609338752495-0"
      2) 1) "field"
         2) "value"
```

In the above example, we attempt to claim up to 25 entries that are pending and
idle (not having been acknowledged or claimed) for at least an hour, starting at
the stream's beginning. The consumer "Alice" from the "mygroup" group acquires
ownership of these messages. Note that the stream ID returned in the example is
`0-0`, indicating that the entire stream was scanned.
