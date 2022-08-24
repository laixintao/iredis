Load a library to Redis.

The command's gets a single mandatory parameter which is the source code that implements the library.
The library payload must start with Shebang statement that provides a metadata about the library (like the engine to use and the library name).
Shebang format: `#!<engine name> name=<library name>`. Currently engine name must be `lua`.

For the Lua engine, the implementation should declare one or more entry points to the library with the [`redis.register_function()` API](/topics/lua-api#redis.register_function).
Once loaded, you can call the functions in the library with the `FCALL` (or `FCALL_RO` when applicable) command.

When attempting to load a library with a name that already exists, the Redis server returns an error.
The `REPLACE` modifier changes this behavior and overwrites the existing library with the new contents.

The command will return an error in the following circumstances:

* An invalid _engine-name_ was provided.
* The library's name already exists without the `REPLACE` modifier.
* A function in the library is created with a name that already exists in another library (even when `REPLACE` is specified).
* The engine failed in creating the library's functions (due to a compilation error, for example).
* No functions were declared by the library.

For more information please refer to [Introduction to Redis Functions](/topics/functions-intro).

@return

@string - the library name that was loaded

@examples

The following example will create a library named `mylib` with a single function, `myfunc`, that returns the first argument it gets.

```
redis> FUNCTION LOAD "#!lua name=mylib \n redis.register_function('myfunc', function(keys, args) return args[1] end)"
mylib
redis> FCALL myfunc 0 hello
"hello"
```
