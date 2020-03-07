Get the value of `key`. If the key does not exist the special value `nil` is
returned. An error is returned if the value stored at `key` is not a string,
because `GET` only handles string values.

@return

@bulk-string-reply: the value of `key`, or `nil` when `key` does not exist.

@examples

```cli
GET nonexisting
SET mykey "Hello"
GET mykey
```
