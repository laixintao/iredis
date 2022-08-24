Add the specified members to the set stored at `key`.
Specified members that are already a member of this set are ignored.
If `key` does not exist, a new set is created before adding the specified
members.

An error is returned when the value stored at `key` is not a set.

@return

@integer-reply: the number of elements that were added to the set, not including
all the elements already present in the set.

@examples

```cli
SADD myset "Hello"
SADD myset "World"
SADD myset "World"
SMEMBERS myset
```
