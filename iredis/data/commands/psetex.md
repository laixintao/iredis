`PSETEX` works exactly like `SETEX` with the sole difference that the expire
time is specified in milliseconds instead of seconds.

@examples

```cli
PSETEX mykey 1000 "Hello"
PTTL mykey
GET mykey
```
