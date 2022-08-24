This command returns the list of all consumers groups of the stream stored at `<key>`.

By default, only the following information is provided for each of the groups:

* **name**: the consumer group's name
* **consumers**: the number of consumers in the group
* **pending**: the length of the group's pending entries list (PEL), which are messages that were delivered but are yet to be acknowledged
* **last-delivered-id**: the ID of the last entry delivered the group's consumers
* **entries-read**: the logical "read counter" of the last entry delivered to group's consumers
* **lag**: the number of entries in the stream that are still waiting to be delivered to the group's consumers, or a NULL when that number can't be determined.

### Consumer group lag

The lag of a given consumer group is the number of entries in the range between the group's `entries_read` and the stream's `entries_added`.
Put differently, it is the number of entries that are yet to be delivered to the group's consumers.

The values and trends of this metric are helpful in making scaling decisions about the consumer group.
You can address high lag values by adding more consumers to the group, whereas low values may indicate that you can remove consumers from the group to scale it down.

Redis reports the lag of a consumer group by keeping two counters: the number of all entries added to the stream and the number of logical reads made by the consumer group.
The lag is the difference between these two.

The stream's counter (the `entries_added` field of the `XINFO STREAM` command) is incremented by one with every `XADD` and counts all of the entries added to the stream during its lifetime.

The consumer group's counter, `entries_read`, is the logical counter of entries that the group had read.
It is important to note that this counter is only a heuristic rather than an accurate counter, and therefore the use of the term "logical".
The counter attempts to reflect the number of entries that the group **should have read** to get to its current `last-delivered-id`.
The `entries_read` counter is accurate only in a perfect world, where a consumer group starts at the stream's first entry and processes all of its entries (i.e., no entries deleted before processing).

There are two special cases in which this mechanism is unable to report the lag:

1. A consumer group is created or set with an arbitrary last delivered ID (the `XGROUP CREATE` and `XGROUP SETID` commands, respectively).
    An arbitrary ID is any ID that isn't the ID of the stream's first entry, its last entry or the zero ("0-0") ID.
2. One or more entries between the group's `last-delivered-id` and the stream's `last-generated-id` were deleted (with `XDEL` or a trimming operation).

In both cases, the group's read counter is considered invalid, and the returned value is set to NULL to signal that the lag isn't currently available.

However, the lag is only temporarily unavailable.
It is restored automatically during regular operation as consumers keep processing messages.
Once the consumer group delivers the last message in the stream to its members, it will be set with the correct logical read counter, and tracking its lag can be resumed.

@reply

@array-reply: a list of consumer groups.

@examples

```
> XINFO GROUPS mystream
1)  1) "name"
    2) "mygroup"
    3) "consumers"
    4) (integer) 2
    5) "pending"
    6) (integer) 2
    7) "last-delivered-id"
    8) "1638126030001-0"
    9) "entries-read"
   10) (integer) 2
   11) "lag"
   12) (integer) 0
2)  1) "name"
    2) "some-other-group"
    3) "consumers"
    4) (integer) 1
    5) "pending"
    6) (integer) 0
    7) "last-delivered-id"
    8) "1638126028070-0"
    9) "entries-read"
   10) (integer) 1
   11) "lag"
   12) (integer) 1
```
