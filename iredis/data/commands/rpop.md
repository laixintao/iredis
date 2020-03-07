Removes and returns the last element of the list stored at `key`.

@return

@bulk-string-reply: the value of the last element, or `nil` when `key` does not
exist.

@examples

```cli
RPUSH mylist "one"
RPUSH mylist "two"
RPUSH mylist "three"
RPOP mylist
LRANGE mylist 0 -1
```
