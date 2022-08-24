Kills the currently executing `EVAL` script, assuming no write operation was yet
performed by the script.

This command is mainly useful to kill a script that is running for too much
time(for instance, because it entered an infinite loop because of a bug).
The script will be killed, and the client currently blocked into EVAL will see
the command returning with an error.

If the script has already performed write operations, it can not be killed in this
way because it would violate Lua's script atomicity contract.
In such a case, only `SHUTDOWN NOSAVE` can kill the script, killing
the Redis process in a hard way and preventing it from persisting with half-written
information.

For more information about `EVAL` scripts please refer to [Introduction to Eval Scripts](/topics/eval-intro).

@return

@simple-string-reply
