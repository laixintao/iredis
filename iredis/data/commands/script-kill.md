Kills the currently executing Lua script, assuming no write operation was yet
performed by the script.

This command is mainly useful to kill a script that is running for too much
time(for instance because it entered an infinite loop because of a bug). The
script will be killed and the client currently blocked into EVAL will see the
command returning with an error.

If the script already performed write operations it can not be killed in this
way because it would violate Lua script atomicity contract. In such a case only
`SHUTDOWN NOSAVE` is able to kill the script, killing the Redis process in an
hard way preventing it to persist with half-written information.

Please refer to the `EVAL` documentation for detailed information about Redis
Lua scripting.

@return

@simple-string-reply
