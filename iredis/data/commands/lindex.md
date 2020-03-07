Returns the element at index `index` in the list stored at `key`. The index is
zero-based, so `0` means the first element, `1` the second element and so on.
Negative indices can be used to designate elements starting at the tail of the
list. Here, `-1` means the last element, `-2` means the penultimate and so
forth.

When the value at `key` is not a list, an error is returned.

@return

@bulk-string-reply: the requested element, or `nil` when `index` is out of
range.

@examples

```cli
LPUSH mylist "World"
LPUSH mylist "Hello"
LINDEX mylist 0
LINDEX mylist -1
LINDEX mylist 3
```
