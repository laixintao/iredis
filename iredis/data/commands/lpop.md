Removes and returns the first element of the list stored at `key`.

@return

@bulk-string-reply: the value of the first element, or `nil` when `key` does not
exist.

@examples

```cli
RPUSH mylist "one"
RPUSH mylist "two"
RPUSH mylist "three"
LPOP mylist
LRANGE mylist 0 -1
```
