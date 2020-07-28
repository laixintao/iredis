The `OBJECT` command allows to inspect the internals of Redis Objects associated
with keys. It is useful for debugging or to understand if your keys are using
the specially encoded data types to save space. Your application may also use
the information reported by the `OBJECT` command to implement application level
key eviction policies when using Redis as a Cache.

The `OBJECT` command supports multiple sub commands:

- `OBJECT REFCOUNT <key>` returns the number of references of the value
  associated with the specified key. This command is mainly useful for
  debugging.
- `OBJECT ENCODING <key>` returns the kind of internal representation used in
  order to store the value associated with a key.
- `OBJECT IDLETIME <key>` returns the number of seconds since the object stored
  at the specified key is idle (not requested by read or write operations).
  While the value is returned in seconds the actual resolution of this timer is
  10 seconds, but may vary in future implementations. This subcommand is
  available when `maxmemory-policy` is set to an LRU policy or `noeviction` and
  `maxmemory` is set.
- `OBJECT FREQ <key>` returns the logarithmic access frequency counter of the
  object stored at the specified key. This subcommand is available when
  `maxmemory-policy` is set to an LFU policy.
- `OBJECT HELP` returns a succinct help text.

Objects can be encoded in different ways:

- Strings can be encoded as `raw` (normal string encoding) or `int` (strings
  representing integers in a 64 bit signed interval are encoded in this way in
  order to save space).
- Lists can be encoded as `ziplist` or `linkedlist`. The `ziplist` is the
  special representation that is used to save space for small lists.
- Sets can be encoded as `intset` or `hashtable`. The `intset` is a special
  encoding used for small sets composed solely of integers.
- Hashes can be encoded as `ziplist` or `hashtable`. The `ziplist` is a special
  encoding used for small hashes.
- Sorted Sets can be encoded as `ziplist` or `skiplist` format. As for the List
  type small sorted sets can be specially encoded using `ziplist`, while the
  `skiplist` encoding is the one that works with sorted sets of any size.

All the specially encoded types are automatically converted to the general type
once you perform an operation that makes it impossible for Redis to retain the
space saving encoding.

@return

Different return values are used for different subcommands.

- Subcommands `refcount` and `idletime` return integers.
- Subcommand `encoding` returns a bulk reply.

If the object you try to inspect is missing, a null bulk reply is returned.

@examples

```
redis> lpush mylist "Hello World"
(integer) 4
redis> object refcount mylist
(integer) 1
redis> object encoding mylist
"ziplist"
redis> object idletime mylist
(integer) 10
```

In the following example you can see how the encoding changes once Redis is no
longer able to use the space saving encoding.

```
redis> set foo 1000
OK
redis> object encoding foo
"int"
redis> append foo bar
(integer) 7
redis> get foo
"1000bar"
redis> object encoding foo
"raw"
```
