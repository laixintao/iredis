Load a script into the scripts cache, without executing it. After the specified
command is loaded into the script cache it will be callable using `EVALSHA` with
the correct SHA1 digest of the script, exactly like after the first successful
invocation of `EVAL`.

The script is guaranteed to stay in the script cache forever (unless
`SCRIPT FLUSH` is called).

The command works in the same way even if the script was already present in the
script cache.

Please refer to the `EVAL` documentation for detailed information about Redis
Lua scripting.

@return

@bulk-string-reply This command returns the SHA1 digest of the script added into
the script cache.
