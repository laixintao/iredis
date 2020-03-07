Returns `PONG` if no argument is provided, otherwise return a copy of the
argument as a bulk. This command is often used to test if a connection is still
alive, or to measure latency.

If the client is subscribed to a channel or a pattern, it will instead return a
multi-bulk with a "pong" in the first position and an empty bulk in the second
position, unless an argument is provided in which case it returns a copy of the
argument.

@return

@simple-string-reply

@examples

```cli
PING

PING "hello world"
```
