The `CLIENT NO-EVICT` command sets the [client eviction](/topics/clients#client-eviction) mode for the current connection.

When turned on and client eviction is configured, the current connection will be excluded from the client eviction process even if we're above the configured client eviction threshold.

When turned off, the current client will be re-included in the pool of potential clients to be evicted (and evicted if needed).

See [client eviction](/topics/clients#client-eviction) for more details.

@return

@simple-string-reply: `OK`.
