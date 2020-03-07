Read data from one or multiple streams, only returning entries with an ID
greater than the last received ID reported by the caller. This command has an
option to block if items are not available, in a similar fashion to `BRPOP` or
`BZPOPMIN` and others.

Please note that before reading this page, if you are new to streams, we
recommend to read [our introduction to Redis Streams](/topics/streams-intro).

## Non-blocking usage

If the **BLOCK** option is not used, the command is synchronous, and can be
considered somewhat related to `XRANGE`: it will return a range of items inside
streams, however it has two fundamental differences compared to `XRANGE` even if
we just consider the synchronous usage:

- This command can be called with multiple streams if we want to read at the
  same time from a number of keys. This is a key feature of `XREAD` because
  especially when blocking with **BLOCK**, to be able to listen with a single
  connection to multiple keys is a vital feature.
- While `XRANGE` returns items in a range of IDs, `XREAD` is more suited in
  order to consume the stream starting from the first entry which is greater
  than any other entry we saw so far. So what we pass to `XREAD` is, for each
  stream, the ID of the last element that we received from that stream.

For example, if I have two streams `mystream` and `writers`, and I want to read
data from both the streams starting from the first element they contain, I could
call `XREAD` like in the following example.

Note: we use the **COUNT** option in the example, so that for each stream the
call will return at maximum two elements per stream.

```
> XREAD COUNT 2 STREAMS mystream writers 0-0 0-0
1) 1) "mystream"
   2) 1) 1) 1526984818136-0
         2) 1) "duration"
            2) "1532"
            3) "event-id"
            4) "5"
            5) "user-id"
            6) "7782813"
      2) 1) 1526999352406-0
         2) 1) "duration"
            2) "812"
            3) "event-id"
            4) "9"
            5) "user-id"
            6) "388234"
2) 1) "writers"
   2) 1) 1) 1526985676425-0
         2) 1) "name"
            2) "Virginia"
            3) "surname"
            4) "Woolf"
      2) 1) 1526985685298-0
         2) 1) "name"
            2) "Jane"
            3) "surname"
            4) "Austen"
```

The **STREAMS** option is mandatory and MUST be the final option because such
option gets a variable length of argument in the following format:

    STREAMS key_1 key_2 key_3 ... key_N ID_1 ID_2 ID_3 ... ID_N

So we start with a list of keys, and later continue with all the associated IDs,
representing _the last ID we received for that stream_, so that the call will
serve us only greater IDs from the same stream.

For instance in the above example, the last items that we received for the
stream `mystream` has ID `1526999352406-0`, while for the stream `writers` has
the ID `1526985685298-0`.

To continue iterating the two streams I'll call:

```
> XREAD COUNT 2 STREAMS mystream writers 1526999352406-0 1526985685298-0
1) 1) "mystream"
   2) 1) 1) 1526999626221-0
         2) 1) "duration"
            2) "911"
            3) "event-id"
            4) "7"
            5) "user-id"
            6) "9488232"
2) 1) "writers"
   2) 1) 1) 1526985691746-0
         2) 1) "name"
            2) "Toni"
            3) "surname"
            4) "Morrison"
      2) 1) 1526985712947-0
         2) 1) "name"
            2) "Agatha"
            3) "surname"
            4) "Christie"
```

And so forth. Eventually, the call will not return any item, but just an empty
array, then we know that there is nothing more to fetch from our stream (and we
would have to retry the operation, hence this command also supports a blocking
mode).

## Incomplete IDs

To use incomplete IDs is valid, like it is valid for `XRANGE`. However here the
sequence part of the ID, if missing, is always interpreted as zero, so the
command:

```
> XREAD COUNT 2 STREAMS mystream writers 0 0
```

is exactly equivalent to

```
> XREAD COUNT 2 STREAMS mystream writers 0-0 0-0
```

## Blocking for data

In its synchronous form, the command can get new data as long as there are more
items available. However, at some point, we'll have to wait for producers of
data to use `XADD` to push new entries inside the streams we are consuming. In
order to avoid polling at a fixed or adaptive interval the command is able to
block if it could not return any data, according to the specified streams and
IDs, and automatically unblock once one of the requested keys accept data.

It is important to understand that this command _fans out_ to all the clients
that are waiting for the same range of IDs, so every consumer will get a copy of
the data, unlike to what happens when blocking list pop operations are used.

In order to block, the **BLOCK** option is used, together with the number of
milliseconds we want to block before timing out. Normally Redis blocking
commands take timeouts in seconds, however this command takes a millisecond
timeout, even if normally the server will have a timeout resolution near to 0.1
seconds. This time it is possible to block for a shorter time in certain use
cases, and if the server internals will improve over time, it is possible that
the resolution of timeouts will improve.

When the **BLOCK** command is passed, but there is data to return at least in
one of the streams passed, the command is executed synchronously _exactly like
if the BLOCK option would be missing_.

This is an example of blocking invocation, where the command later returns a
null reply because the timeout has elapsed without new data arriving:

```
> XREAD BLOCK 1000 STREAMS mystream 1526999626221-0
(nil)
```

## The special `$` ID.

When blocking sometimes we want to receive just entries that are added to the
stream via `XADD` starting from the moment we block. In such a case we are not
interested in the history of already added entries. For this use case, we would
have to check the stream top element ID, and use such ID in the `XREAD` command
line. This is not clean and requires to call other commands, so instead it is
possible to use the special `$` ID to signal the stream that we want only the
new things.

It is **very important** to understand that you should use the `$` ID only for
the first call to `XREAD`. Later the ID should be the one of the last reported
item in the stream, otherwise you could miss all the entries that are added in
between.

This is how a typical `XREAD` call looks like in the first iteration of a
consumer willing to consume only new entries:

```
> XREAD BLOCK 5000 COUNT 100 STREAMS mystream $
```

Once we get some replies, the next call will be something like:

```
> XREAD BLOCK 5000 COUNT 100 STREAMS mystream 1526999644174-3
```

And so forth.

## How multiple clients blocked on a single stream are served

Blocking list operations on lists or sorted sets have a _pop_ behavior.
Basically, the element is removed from the list or sorted set in order to be
returned to the client. In this scenario you want the items to be consumed in a
fair way, depending on the moment clients blocked on a given key arrived.
Normally Redis uses the FIFO semantics in this use cases.

However note that with streams this is not a problem: stream entries are not
removed from the stream when clients are served, so every client waiting will be
served as soon as an `XADD` command provides data to the stream.

@return

@array-reply, specifically:

The command returns an array of results: each element of the returned array is
an array composed of a two element containing the key name and the entries
reported for that key. The entries reported are full stream entries, having IDs
and the list of all the fields and values. Field and values are guaranteed to be
reported in the same order they were added by `XADD`.

When **BLOCK** is used, on timeout a null reply is returned.

Reading the [Redis Streams introduction](/topics/streams-intro) is highly
suggested in order to understand more about the streams overall behavior and
semantics.
