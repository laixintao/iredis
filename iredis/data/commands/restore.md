Create a key associated with a value that is obtained by deserializing the
provided serialized value (obtained via `DUMP`).

If `ttl` is 0 the key is created without any expire, otherwise the specified
expire time (in milliseconds) is set.

If the `ABSTTL` modifier was used, `ttl` should represent an absolute [Unix
timestamp][hewowu] (in milliseconds) in which the key will expire. (Redis 5.0 or
greater).

[hewowu]: http://en.wikipedia.org/wiki/Unix_time

For eviction purposes, you may use the `IDLETIME` or `FREQ` modifiers. See
`OBJECT` for more information (Redis 5.0 or greater).

`RESTORE` will return a "Target key name is busy" error when `key` already
exists unless you use the `REPLACE` modifier (Redis 3.0 or greater).

`RESTORE` checks the RDB version and data checksum. If they don't match an error
is returned.

@return

@simple-string-reply: The command returns OK on success.

@examples

```
redis> DEL mykey
0
redis> RESTORE mykey 0 "\n\x17\x17\x00\x00\x00\x12\x00\x00\x00\x03\x00\
                        x00\xc0\x01\x00\x04\xc0\x02\x00\x04\xc0\x03\x00\
                        xff\x04\x00u#<\xc0;.\xe9\xdd"
OK
redis> TYPE mykey
list
redis> LRANGE mykey 0 -1
1) "1"
2) "2"
3) "3"
```
