The `CLIENT GETNAME` returns the name of the current connection as set by
`CLIENT SETNAME`. Since every new connection starts without an associated name,
if no name was assigned a null bulk reply is returned.

@return

@bulk-string-reply: The connection name, or a null bulk reply if no name is set.
