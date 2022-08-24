Invoke the execution of a server-side Lua script.

The first argument is the script's source code.
Scripts are written in [Lua](https://lua.org) and executed by the embedded [Lua 5.1](/topics/lua-api) interpreter in Redis.

The second argument is the number of input key name arguments, followed by all the keys accessed by the script.
These names of input keys are available to the script as the [_KEYS_ global runtime variable](/topics/lua-api#the-keys-global-variable)
Any additional input arguments **should not** represent names of keys.

**Important:**
to ensure the correct execution of scripts, both in standalone and clustered deployments, all names of keys that a script accesses must be explicitly provided as input key arguments.
The script **should only** access keys whose names are given as input arguments.
Scripts **should never** access keys with programmatically-generated names or based on the contents of data structures stored in the database.

Please refer to the [Redis Programmability](/topics/programmability) and [Introduction to Eval Scripts](/topics/eval-intro) for more information about Lua scripts.

@examples

The following example will run a script that returns the first argument that it gets.

```
> EVAL "return ARGV[1]" 0 hello
"hello"
```
