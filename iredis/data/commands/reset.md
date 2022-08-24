This command performs a full reset of the connection's server-side context, 
mimicking the effect of disconnecting and reconnecting again.

When the command is called from a regular client connection, it does the
following:

* Discards the current `MULTI` transaction block, if one exists.
* Unwatches all keys `WATCH`ed by the connection.
* Disables `CLIENT TRACKING`, if in use.
* Sets the connection to `READWRITE` mode.
* Cancels the connection's `ASKING` mode, if previously set.
* Sets `CLIENT REPLY` to `ON`.
* Sets the protocol version to RESP2.
* `SELECT`s database 0.
* Exits `MONITOR` mode, when applicable.
* Aborts Pub/Sub's subscription state (`SUBSCRIBE` and `PSUBSCRIBE`), when
  appropriate.
* Deauthenticates the connection, requiring a call `AUTH` to reauthenticate when
  authentication is enabled.

@return

@simple-string-reply: always 'RESET'.
