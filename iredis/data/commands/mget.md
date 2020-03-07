Returns the values of all specified keys. For every key that does not hold a
string value or does not exist, the special value `nil` is returned. Because of
this, the operation never fails.

@return

@array-reply: list of values at the specified keys.

@examples

```cli
SET key1 "Hello"
SET key2 "World"
MGET key1 key2 nonexisting
```
