`XTRIM` trims the stream by evicting older entries (entries with lower IDs) if needed.

Trimming the stream can be done using one of these strategies:

* `MAXLEN`: Evicts entries as long as the stream's length exceeds the specified `threshold`, where `threshold` is a positive integer.
* `MINID`: Evicts entries with IDs lower than `threshold`, where `threshold` is a stream ID.

For example, this will trim the stream to exactly the latest 1000 items:

```
XTRIM mystream MAXLEN 1000
```

Whereas in this example, all entries that have an ID lower than 649085820-0 will be evicted:

```
XTRIM mystream MINID 649085820
```

By default, or when provided with the optional `=` argument, the command performs exact trimming.

Depending on the strategy, exact trimming means:

* `MAXLEN`: the trimmed stream's length will be exactly the minimum between its original length and the specified `threshold`.
* `MINID`: the oldest ID in the stream will be exactly the maximum between its original oldest ID and the specified `threshold`.

Nearly exact trimming
---

Because exact trimming may require additional effort from the Redis server, the optional `~` argument can be provided to make it more efficient.

For example:

```
XTRIM mystream MAXLEN ~ 1000
```

The `~` argument between the `MAXLEN` strategy and the `threshold` means that the user is requesting to trim the stream so its length is **at least** the `threshold`, but possibly slightly more.
In this case, Redis will stop trimming early when performance can be gained (for example, when a whole macro node in the data structure can't be removed).
This makes trimming much more efficient, and it is usually what you want, although after trimming, the stream may have few tens of additional entries over the `threshold`.

Another way to control the amount of work done by the command when using the `~`, is the `LIMIT` clause. 
When used, it specifies the maximal `count` of entries that will be evicted.
When `LIMIT` and `count` aren't specified, the default value of 100 * the number of entries in a macro node will be implicitly used as the `count`.
Specifying the value 0 as `count` disables the limiting mechanism entirely.

@return

@integer-reply: The number of entries deleted from the stream.

@examples

```cli
XADD mystream * field1 A field2 B field3 C field4 D
XTRIM mystream MAXLEN 2
XRANGE mystream - +
```
