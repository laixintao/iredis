Removes and returns one or more random members from the set value store at `key`.

This operation is similar to `SRANDMEMBER`, that returns one or more random elements from a set but does not remove it.

By default, the command pops a single member from the set. When provided with
the optional `count` argument, the reply will consist of up to `count` members,
depending on the set's cardinality.

@return

When called without the `count` argument:

@bulk-string-reply: the removed member, or `nil` when `key` does not exist.

When called with the `count` argument:

@array-reply: the removed members, or an empty array when `key` does not exist.

@examples

```cli
SADD myset "one"
SADD myset "two"
SADD myset "three"
SPOP myset
SMEMBERS myset
SADD myset "four"
SADD myset "five"
SPOP myset 3
SMEMBERS myset
```
## Distribution of returned elements

Note that this command is not suitable when you need a guaranteed uniform distribution of the returned elements. For more information about the algorithms used for `SPOP`, look up both the Knuth sampling and Floyd sampling algorithms.
