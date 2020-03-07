Alters the last access time of a key(s). A key is ignored if it does not exist.

@return

@integer-reply: The number of keys that were touched.

@examples

```cli
SET key1 "Hello"
SET key2 "World"
TOUCH key1 key2
```
