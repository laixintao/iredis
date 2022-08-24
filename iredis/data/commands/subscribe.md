Subscribes the client to the specified channels.

Once the client enters the subscribed state it is not supposed to issue any
other commands, except for additional `SUBSCRIBE`, `SSUBSCRIBE`, `PSUBSCRIBE`, `UNSUBSCRIBE`, `SUNSUBSCRIBE`, 
`PUNSUBSCRIBE`, `PING`, `RESET` and `QUIT` commands.

## Behavior change history

*   `>= 6.2.0`: `RESET` can be called to exit subscribed state.