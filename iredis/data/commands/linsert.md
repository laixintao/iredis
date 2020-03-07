Inserts `element` in the list stored at `key` either before or after the
reference value `pivot`.

When `key` does not exist, it is considered an empty list and no operation is
performed.

An error is returned when `key` exists but does not hold a list value.

@return

@integer-reply: the length of the list after the insert operation, or `-1` when
the value `pivot` was not found.

@examples

```cli
RPUSH mylist "Hello"
RPUSH mylist "World"
LINSERT mylist BEFORE "World" "There"
LRANGE mylist 0 -1
```
