The `CONFIG REWRITE` command rewrites the `redis.conf` file the server was
started with, applying the minimal changes needed to make it reflect the
configuration currently used by the server, which may be different compared to
the original one because of the use of the `CONFIG SET` command.

The rewrite is performed in a very conservative way:

- Comments and the overall structure of the original redis.conf are preserved as
  much as possible.
- If an option already exists in the old redis.conf file, it will be rewritten
  at the same position (line number).
- If an option was not already present, but it is set to its default value, it
  is not added by the rewrite process.
- If an option was not already present, but it is set to a non-default value, it
  is appended at the end of the file.
- Non used lines are blanked. For instance if you used to have multiple `save`
  directives, but the current configuration has fewer or none as you disabled
  RDB persistence, all the lines will be blanked.

CONFIG REWRITE is also able to rewrite the configuration file from scratch if
the original one no longer exists for some reason. However if the server was
started without a configuration file at all, the CONFIG REWRITE will just return
an error.

## Atomic rewrite process

In order to make sure the redis.conf file is always consistent, that is, on
errors or crashes you always end with the old file, or the new one, the rewrite
is performed with a single `write(2)` call that has enough content to be at
least as big as the old file. Sometimes additional padding in the form of
comments is added in order to make sure the resulting file is big enough, and
later the file gets truncated to remove the padding at the end.

@return

@simple-string-reply: `OK` when the configuration was rewritten properly.
Otherwise an error is returned.
