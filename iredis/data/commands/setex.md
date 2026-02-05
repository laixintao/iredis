Set `key` to hold the string `value` and set `key` to timeout after a given
number of seconds.
This command is equivalent to:

```
SET key value EX seconds
```


An error is returned when `seconds` is invalid.

@return

@simple-string-reply

@examples

```cli
SETEX mykey 10 "Hello"
TTL mykey
GET mykey
```
## See also

`TTL`