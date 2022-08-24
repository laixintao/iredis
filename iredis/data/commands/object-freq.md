This command returns the logarithmic access frequency counter of a Redis object stored at `<key>`.

The command is only available when the `maxmemory-policy` configuration directive is set to one of the LFU policies.

@return

@integer-reply

The counter's value.