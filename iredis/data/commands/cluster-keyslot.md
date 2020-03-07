Returns an integer identifying the hash slot the specified key hashes to. This
command is mainly useful for debugging and testing, since it exposes via an API
the underlying Redis implementation of the hashing algorithm. Example use cases
for this command:

1. Client libraries may use Redis in order to test their own hashing algorithm,
   generating random keys and hashing them with both their local implementation
   and using Redis `CLUSTER KEYSLOT` command, then checking if the result is the
   same.
2. Humans may use this command in order to check what is the hash slot, and then
   the associated Redis Cluster node, responsible for a given key.

## Example

```
> CLUSTER KEYSLOT somekey
11058
> CLUSTER KEYSLOT foo{hash_tag}
(integer) 2515
> CLUSTER KEYSLOT bar{hash_tag}
(integer) 2515
```

Note that the command implements the full hashing algorithm, including support
for **hash tags**, that is the special property of Redis Cluster key hashing
algorithm, of hashing just what is between `{` and `}` if such a pattern is
found inside the key name, in order to force multiple keys to be handled by the
same node.

@return

@integer-reply: The hash slot number.
