Sets the list element at `index` to `element`. For more information on the
`index` argument, see `LINDEX`.

An error is returned for out of range indexes.

@return

@simple-string-reply

@examples

```cli
RPUSH mylist "one"
RPUSH mylist "two"
RPUSH mylist "three"
LSET mylist 0 "four"
LSET mylist -2 "five"
LRANGE mylist 0 -1
```
