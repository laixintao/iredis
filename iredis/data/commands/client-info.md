The command returns information and statistics about the current client connection in a mostly human readable format.

The reply format is identical to that of `CLIENT LIST`, and the content consists only of information about the current client.

@examples

```cli
CLIENT INFO
```

@return

@bulk-string-reply: a unique string, as described at the `CLIENT LIST` page, for the current client.
