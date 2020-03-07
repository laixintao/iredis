Remove the existing timeout on `key`, turning the key from _volatile_ (a key
with an expire set) to _persistent_ (a key that will never expire as no timeout
is associated).

@return

@integer-reply, specifically:

- `1` if the timeout was removed.
- `0` if `key` does not exist or does not have an associated timeout.

@examples

```cli
SET mykey "Hello"
EXPIRE mykey 10
TTL mykey
PERSIST mykey
TTL mykey
```
