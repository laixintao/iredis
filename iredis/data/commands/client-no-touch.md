The `CLIENT NO-TOUCH` command controls whether commands sent by the client will alter the LRU/LFU of the keys they access.

When turned on, the current client will not change LFU/LRU stats, unless it sends the `TOUCH` command.

When turned off, the client touches LFU/LRU stats just as a normal client.

@return

@simple-string-reply: `OK`.
