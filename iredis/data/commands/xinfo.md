This is an introspection command used in order to retrieve different information
about the streams and associated consumer groups. Three forms are possible:

* `XINFO STREAM <key>`

In this form the command returns general information about the stream stored
at the specified key.

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

In the above example you can see that the reported information are the number
of elements of the stream, details about the radix tree representing the
stream mostly useful for optimization and debugging tasks, the number of
consumer groups associated with the stream, the last generated ID that may
not be the same as the last entry ID in case some entry was deleted. Finally
the full first and last entry in the stream are shown, in order to give some
sense about what is the stream content.

* `XINFO GROUPS <key>`

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
2) 1) name
   2) "some-other-group"
   3) consumers
   4) (integer) 1
   5) pending
   6) (integer) 0
```

For each consumer group listed the command also shows the number of consumers
known in that group and the pending messages (delivered but not yet acknowledged)
in that group.

* `XINFO CONSUMERS <key> <group>`

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

We can see the idle time in milliseconds (last field) together with the
consumer name and the number of pending messages for this specific
consumer.

**Note that you should not rely on the fields exact position**, nor on the
number of fields, new fields may be added in the future. So a well behaving
client should fetch the whole list, and report it to the user, for example,
as a dictionary data structure. Low level clients such as C clients where
the items will likely be reported back in a linear array should document
that the order is undefined.

Finally it is possible to get help from the command, in case the user can't
remember the exact syntax, by using the `HELP` subcommnad:

```
> XINFO HELP
1) XINFO <subcommand> arg arg ... arg. Subcommands are:
2) CONSUMERS <key> <groupname>  -- Show consumer groups of group <groupname>.
3) GROUPS <key>                 -- Show the stream consumer groups.
4) STREAM <key>                 -- Show information about the stream.
5) HELP
```
