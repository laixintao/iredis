Removes the specified keys. A key is ignored if it does not exist.

@return

@integer-reply: The number of keys that were removed.

@examples

```cli
SET key1 "Hello"
SET key2 "World"
DEL key1 key2 key3
```
