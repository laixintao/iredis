Loads a module from a dynamic library at runtime with configuration directives.

This is an extended version of the `MODULE LOAD` command.

It loads and initializes the Redis module from the dynamic library specified by the `path` argument. The `path` should be the absolute path of the library, including the full filename.

You can use the optional `!CONFIG` argument to provide the module with configuration directives.
Any additional arguments that follow the `ARGS` keyword are passed unmodified to the module.

**Note**: modules can also be loaded at server startup with `loadmodule`
configuration directive in `redis.conf`.

@return

@simple-string-reply: `OK` if module was loaded.
