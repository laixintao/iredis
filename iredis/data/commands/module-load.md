Loads a module from a dynamic library at runtime.

This command loads and initializes the Redis module from the dynamic library
specified by the `path` argument. The `path` should be the absolute path of the
library, including the full filename. Any additional arguments are passed
unmodified to the module.

**Note**: modules can also be loaded at server startup with 'loadmodule'
configuration directive in `redis.conf`.

@return

@simple-string-reply: `OK` if module was loaded.
