This is an introspection command used in order to retrieve different information
about the streams and associated consumer groups. Three forms are possible:

- `XINFO STREAM <key>`

In this form the command returns general information about the stream stored at
the specified key.

```
> XINFO STREAM mystream
 1) length
 2) (integer) 2
 3) radix-tree-keys
 4) (integer) 1
 5) radix-tree-nodes
 6) (integer) 2
 7) groups
 8) (integer) 2
 9) last-generated-id
10) 1538385846314-0
11) first-entry
12) 1) 1538385820729-0
    2) 1) "foo"
       2) "bar"
13) last-entry
14) 1) 1538385846314-0
    2) 1) "field"
       2) "value"
```

In the above example you can see that the reported information are the number of
elements of the stream, details about the radix tree representing the stream
mostly useful for optimization and debugging tasks, the number of consumer
groups associated with the stream, the last generated ID that may not be the
same as the last entry ID in case some entry was deleted. Finally the full first
and last entry in the stream are shown, in order to give some sense about what
is the stream content.

- `XINFO STREAM <key> FULL [COUNT <count>]`

In this form the command returns the entire state of the stream, including
entries, groups, consumers and PELs. This form is available since Redis 6.0.

```
> XADD mystream * foo bar
"1588152471065-0"
> XADD mystream * foo bar2
"1588152473531-0"
> XGROUP CREATE mystream mygroup 0-0
OK
> XREADGROUP GROUP mygroup Alice COUNT 1 STREAMS mystream >
1) 1) "mystream"
   2) 1) 1) "1588152471065-0"
         2) 1) "foo"
            2) "bar"
> XINFO STREAM mystream FULL
 1) "length"
 2) (integer) 2
 3) "radix-tree-keys"
 4) (integer) 1
 5) "radix-tree-nodes"
 6) (integer) 2
 7) "last-generated-id"
 8) "1588152473531-0"
 9) "entries"
10) 1) 1) "1588152471065-0"
       2) 1) "foo"
          2) "bar"
    2) 1) "1588152473531-0"
       2) 1) "foo"
          2) "bar2"
11) "groups"
12) 1)  1) "name"
        2) "mygroup"
        3) "last-delivered-id"
        4) "1588152471065-0"
        5) "pel-count"
        6) (integer) 1
        7) "pending"
        8) 1) 1) "1588152471065-0"
              2) "Alice"
              3) (integer) 1588152520299
              4) (integer) 1
        9) "consumers"
       10) 1) 1) "name"
              2) "Alice"
              3) "seen-time"
              4) (integer) 1588152520299
              5) "pel-count"
              6) (integer) 1
              7) "pending"
              8) 1) 1) "1588152471065-0"
                    2) (integer) 1588152520299
                    3) (integer) 1
```

The reported information contains all of the fields reported by the simple form
of `XINFO STREAM`, with some additional information:

1. Stream entries are returned, including fields and values.
2. Groups, consumers and PELs are returned.

The `COUNT` option is used to limit the amount of stream/PEL entries that are
returned (The first `<count>` entries are returned). The default `COUNT` is 10
and a `COUNT` of 0 means that all entries will be returned (Execution time may
be long if the stream has a lot of entries)

- `XINFO GROUPS <key>`

In this form we just get as output all the consumer groups associated with the
stream:

```
> XINFO GROUPS mystream
1) 1) name
   2) "mygroup"
   3) consumers
   4) (integer) 2
   5) pending
   6) (integer) 2
   7) last-delivered-id
   8) "1588152489012-0"
2) 1) name
   2) "some-other-group"
   3) consumers
   4) (integer) 1
   5) pending
   6) (integer) 0
   7) last-delivered-id
   8) "1588152498034-0"
```

For each consumer group listed the command also shows the number of consumers
known in that group and the pending messages (delivered but not yet
acknowledged) in that group.

- `XINFO CONSUMERS <key> <group>`

Finally it is possible to get the list of every consumer in a specific consumer
group:

```
> XINFO CONSUMERS mystream mygroup
1) 1) name
   2) "Alice"
   3) pending
   4) (integer) 1
   5) idle
   6) (integer) 9104628
2) 1) name
   2) "Bob"
   3) pending
   4) (integer) 1
   5) idle
   6) (integer) 83841983
```

We can see the idle time in milliseconds (last field) together with the consumer
name and the number of pending messages for this specific consumer.

**Note that you should not rely on the fields exact position**, nor on the
number of fields, new fields may be added in the future. So a well behaving
client should fetch the whole list, and report it to the user, for example, as a
dictionary data structure. Low level clients such as C clients where the items
will likely be reported back in a linear array should document that the order is
undefined.

Finally it is possible to get help from the command, in case the user can't
remember the exact syntax, by using the `HELP` subcommand:

```
> XINFO HELP
1) XINFO <subcommand> arg arg ... arg. Subcommands are:
2) CONSUMERS <key> <groupname>  -- Show consumer groups of group <groupname>.
3) GROUPS <key>                 -- Show the stream consumer groups.
4) STREAM <key>                 -- Show information about the stream.
5) HELP
```

@history

- `>= 6.0.0`: Added the `FULL` option to `XINFO STREAM`.
