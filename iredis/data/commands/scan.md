The `SCAN` command and the closely related commands `SSCAN`, `HSCAN` and `ZSCAN` are used in order to incrementally iterate over a collection of elements.

* `SCAN` iterates the set of keys in the currently selected Redis database.
* `SSCAN` iterates elements of Sets types.
* `HSCAN` iterates fields of Hash types and their associated values.
* `ZSCAN` iterates elements of Sorted Set types and their associated scores.

Since these commands allow for incremental iteration, returning only a small number of elements per call, they can be used in production without the downside of commands like `KEYS` or `SMEMBERS` that may block the server for a long time (even several seconds) when called against big collections of keys or elements.

However while blocking commands like `SMEMBERS` are able to provide all the elements that are part of a Set in a given moment, The SCAN family of commands only offer limited guarantees about the returned elements since the collection that we incrementally iterate can change during the iteration process.

Note that `SCAN`, `SSCAN`, `HSCAN` and `ZSCAN` all work very similarly, so this documentation covers all the four commands. However an obvious difference is that in the case of `SSCAN`, `HSCAN` and `ZSCAN` the first argument is the name of the key holding the Set, Hash or Sorted Set value. The `SCAN` command does not need any key name argument as it iterates keys in the current database, so the iterated object is the database itself.


For more information on `SCAN` please refer to the [The Redis Keyspace](/docs/manual/keyspace) tutorial.

## Return value

`SCAN`, `SSCAN`, `HSCAN` and `ZSCAN` return a two elements multi-bulk reply, where the first element is a string representing an unsigned 64 bit number (the cursor), and the second element is a multi-bulk with an array of elements.

* `SCAN` array of elements is a list of keys.
* `SSCAN` array of elements is a list of Set members.
* `HSCAN` array of elements contain two elements, a field and a value, for every returned element of the Hash.
* `ZSCAN` array of elements contain two elements, a member and its associated score, for every returned element of the sorted set.

## Additional examples

Iteration of a Hash value.

```
redis 127.0.0.1:6379> hmset hash name Jack age 33
OK
redis 127.0.0.1:6379> hscan hash 0
1) "0"
2) 1) "name"
   2) "Jack"
   3) "age"
   4) "33"
```
