Renames `key` to `newkey`. It returns an error when `key` does not exist. If
`newkey` already exists it is overwritten, when this happens `RENAME` executes
an implicit `DEL` operation, so if the deleted key contains a very big value it
may cause high latency even if `RENAME` itself is usually a constant-time
operation.

In Cluster mode, both `key` and `newkey` must be in the same **hash slot**,
meaning that in practice only keys that have the same hash tag can be reliably
renamed in cluster.

@history

- `<= 3.2.0`: Before Redis 3.2.0, an error is returned if source and destination
  names are the same.

@return

@simple-string-reply

@examples

```cli
SET mykey "Hello"
RENAME mykey myotherkey
GET myotherkey
```
