Returns if `key` exists.

The user should be aware that if the same existing key is mentioned in the arguments multiple times, it will be counted multiple times. So if `somekey` exists, `EXISTS somekey somekey` will return 2.

@return

@integer-reply, specifically the number of keys that exist from those specified as arguments.

@examples

```cli
SET key1 "Hello"
EXISTS key1
EXISTS nosuchkey
SET key2 "World"
EXISTS key1 key2 nosuchkey
```
