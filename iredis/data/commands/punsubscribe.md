Unsubscribes the client from the given patterns, or from all of them if none is
given.

When no patterns are specified, the client is unsubscribed from all the
previously subscribed patterns.
In this case, a message for every unsubscribed pattern will be sent to the
client.

@return

When successful, this command doesn't return anything.
Instead, for each pattern, one message with the first element being the string "punsubscribe" is pushed as a confirmation that the command succeeded.
