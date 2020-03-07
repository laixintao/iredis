Increments the number stored at `key` by one. If the key does not exist, it is
set to `0` before performing the operation. An error is returned if the key
contains a value of the wrong type or contains a string that can not be
represented as integer. This operation is limited to 64 bit signed integers.

**Note**: this is a string operation because Redis does not have a dedicated
integer type. The string stored at the key is interpreted as a base-10 **64 bit
signed integer** to execute the operation.

Redis stores integers in their integer representation, so for string values that
actually hold an integer, there is no overhead for storing the string
representation of the integer.

@return

@integer-reply: the value of `key` after the increment

@examples

```cli
SET mykey "10"
INCR mykey
GET mykey
```

## Pattern: Counter

The counter pattern is the most obvious thing you can do with Redis atomic
increment operations. The idea is simply send an `INCR` command to Redis every
time an operation occurs. For instance in a web application we may want to know
how many page views this user did every day of the year.

To do so the web application may simply increment a key every time the user
performs a page view, creating the key name concatenating the User ID and a
string representing the current date.

This simple pattern can be extended in many ways:

- It is possible to use `INCR` and `EXPIRE` together at every page view to have
  a counter counting only the latest N page views separated by less than the
  specified amount of seconds.
- A client may use GETSET in order to atomically get the current counter value
  and reset it to zero.
- Using other atomic increment/decrement commands like `DECR` or `INCRBY` it is
  possible to handle values that may get bigger or smaller depending on the
  operations performed by the user. Imagine for instance the score of different
  users in an online game.

## Pattern: Rate limiter

The rate limiter pattern is a special counter that is used to limit the rate at
which an operation can be performed. The classical materialization of this
pattern involves limiting the number of requests that can be performed against a
public API.

We provide two implementations of this pattern using `INCR`, where we assume
that the problem to solve is limiting the number of API calls to a maximum of
_ten requests per second per IP address_.

## Pattern: Rate limiter 1

The more simple and direct implementation of this pattern is the following:

```
FUNCTION LIMIT_API_CALL(ip)
ts = CURRENT_UNIX_TIME()
keyname = ip+":"+ts
current = GET(keyname)
IF current != NULL AND current > 10 THEN
    ERROR "too many requests per second"
ELSE
    MULTI
        INCR(keyname,1)
        EXPIRE(keyname,10)
    EXEC
    PERFORM_API_CALL()
END
```

Basically we have a counter for every IP, for every different second. But this
counters are always incremented setting an expire of 10 seconds so that they'll
be removed by Redis automatically when the current second is a different one.

Note the used of `MULTI` and `EXEC` in order to make sure that we'll both
increment and set the expire at every API call.

## Pattern: Rate limiter 2

An alternative implementation uses a single counter, but is a bit more complex
to get it right without race conditions. We'll examine different variants.

```
FUNCTION LIMIT_API_CALL(ip):
current = GET(ip)
IF current != NULL AND current > 10 THEN
    ERROR "too many requests per second"
ELSE
    value = INCR(ip)
    IF value == 1 THEN
        EXPIRE(ip,1)
    END
    PERFORM_API_CALL()
END
```

The counter is created in a way that it only will survive one second, starting
from the first request performed in the current second. If there are more than
10 requests in the same second the counter will reach a value greater than 10,
otherwise it will expire and start again from 0.

**In the above code there is a race condition**. If for some reason the client
performs the `INCR` command but does not perform the `EXPIRE` the key will be
leaked until we'll see the same IP address again.

This can be fixed easily turning the `INCR` with optional `EXPIRE` into a Lua
script that is send using the `EVAL` command (only available since Redis version
2.6).

```
local current
current = redis.call("incr",KEYS[1])
if tonumber(current) == 1 then
    redis.call("expire",KEYS[1],1)
end
```

There is a different way to fix this issue without using scripting, but using
Redis lists instead of counters. The implementation is more complex and uses
more advanced features but has the advantage of remembering the IP addresses of
the clients currently performing an API call, that may be useful or not
depending on the application.

```
FUNCTION LIMIT_API_CALL(ip)
current = LLEN(ip)
IF current > 10 THEN
    ERROR "too many requests per second"
ELSE
    IF EXISTS(ip) == FALSE
        MULTI
            RPUSH(ip,ip)
            EXPIRE(ip,1)
        EXEC
    ELSE
        RPUSHX(ip,ip)
    END
    PERFORM_API_CALL()
END
```

The `RPUSHX` command only pushes the element if the key already exists.

Note that we have a race here, but it is not a problem: `EXISTS` may return
false but the key may be created by another client before we create it inside
the `MULTI` / `EXEC` block. However this race will just miss an API call under
rare conditions, so the rate limiting will still work correctly.
