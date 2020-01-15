Renames `key` to `newkey` if `newkey` does not yet exist.
It returns an error when `key` does not exist.

**Note:** Before Redis 3.2.0, an error is returned if source and destination names are the same.

@return

@integer-reply, specifically:

* `1` if `key` was renamed to `newkey`.
* `0` if `newkey` already exists.

@examples

```cli
SET mykey "Hello"
SET myotherkey "World"
RENAMENX mykey myotherkey
GET myotherkey
```
