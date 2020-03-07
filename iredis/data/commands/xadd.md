Appends the specified stream entry to the stream at the specified key. If the
key does not exist, as a side effect of running this command the key is created
with a stream value.

An entry is composed of a set of field-value pairs, it is basically a small
dictionary. The field-value pairs are stored in the same order they are given by
the user, and commands to read the stream such as `XRANGE` or `XREAD` are
guaranteed to return the fields and values exactly in the same order they were
added by `XADD`.

`XADD` is the _only Redis command_ that can add data to a stream, but there are
other commands, such as `XDEL` and `XTRIM`, that are able to remove data from a
stream.

## Specifying a Stream ID as an argument

A stream entry ID identifies a given entry inside a stream. The `XADD` command
will auto-generate a unique ID for you if the ID argument specified is the `*`
character (asterisk ASCII character). However, while useful only in very rare
cases, it is possible to specify a well-formed ID, so that the new entry will be
added exactly with the specified ID.

IDs are specified by two numbers separated by a `-` character:

    1526919030474-55

Both quantities are 64-bit numbers. When an ID is auto-generated, the first part
is the Unix time in milliseconds of the Redis instance generating the ID. The
second part is just a sequence number and is used in order to distinguish IDs
generated in the same millisecond.

IDs are guaranteed to be always incremental: If you compare the ID of the entry
just inserted it will be greater than any other past ID, so entries are totally
ordered inside a stream. In order to guarantee this property, if the current top
ID in the stream has a time greater than the current local time of the instance,
the top entry time will be used instead, and the sequence part of the ID
incremented. This may happen when, for instance, the local clock jumps backward,
or if after a failover the new master has a different absolute time.

When a user specified an explicit ID to `XADD`, the minimum valid ID is `0-1`,
and the user _must_ specify an ID which is greater than any other ID currently
inside the stream, otherwise the command will fail. Usually resorting to
specific IDs is useful only if you have another system generating unique IDs
(for instance an SQL table) and you really want the Redis stream IDs to match
the one of this other system.

## Capped streams

It is possible to limit the size of the stream to a maximum number of elements
using the **MAXLEN** option.

Trimming with **MAXLEN** can be expensive compared to just adding entries with
`XADD`: streams are represented by macro nodes into a radix tree, in order to be
very memory efficient. Altering the single macro node, consisting of a few tens
of elements, is not optimal. So it is possible to give the command in the
following special form:

    XADD mystream MAXLEN ~ 1000 * ... entry fields here ...

The `~` argument between the **MAXLEN** option and the actual count means that
the user is not really requesting that the stream length is exactly 1000 items,
but instead it could be a few tens of entries more, but never less than 1000
items. When this option modifier is used, the trimming is performed only when
Redis is able to remove a whole macro node. This makes it much more efficient,
and it is usually what you want.

## Additional information about streams

For further information about Redis streams please check our
[introduction to Redis Streams document](/topics/streams-intro).

@return

@bulk-string-reply, specifically:

The command returns the ID of the added entry. The ID is the one auto-generated
if `*` is passed as ID argument, otherwise the command just returns the same ID
specified by the user during insertion.

@examples

```cli
XADD mystream * name Sara surname OConnor
XADD mystream * field1 value1 field2 value2 field3 value3
XLEN mystream
XRANGE mystream - +
```
