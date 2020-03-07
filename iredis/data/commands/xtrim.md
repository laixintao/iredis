`XTRIM` trims the stream to a given number of items, evicting older items (items
with lower IDs) if needed. The command is conceived to accept multiple trimming
strategies, however currently only a single one is implemented, which is
`MAXLEN`, and works exactly as the `MAXLEN` option in `XADD`.

For example the following command will trim the stream to exactly the latest
1000 items:

```
XTRIM mystream MAXLEN 1000
```

It is possible to give the command in the following special form in order to
make it more efficient:

```
XTRIM mystream MAXLEN ~ 1000
```

The `~` argument between the **MAXLEN** option and the actual count means that
the user is not really requesting that the stream length is exactly 1000 items,
but instead it could be a few tens of entries more, but never less than 1000
items. When this option modifier is used, the trimming is performed only when
Redis is able to remove a whole macro node. This makes it much more efficient,
and it is usually what you want.

@return

@integer-reply, specifically:

The command returns the number of entries deleted from the stream.

```cli
XADD mystream * field1 A field2 B field3 C field4 D
XTRIM mystream MAXLEN 2
XRANGE mystream - +
```
