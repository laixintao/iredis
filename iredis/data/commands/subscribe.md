Subscribes the client to the specified channels.

Once the client enters the subscribed state it is not supposed to issue any
other commands, except for additional `SUBSCRIBE`, `PSUBSCRIBE`, `UNSUBSCRIBE`,
`PUNSUBSCRIBE`, `PING`, `RESET` and `QUIT` commands.

@history

- `>= 6.2`: `RESET` can be called to exit subscribed state.
