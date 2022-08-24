This command returns the time in seconds since the last access to the value stored at `<key>`.

The command is only available when the `maxmemory-policy` configuration directive is not set to one of the LFU policies.

@return

@integer-reply

The idle time in seconds.