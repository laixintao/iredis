Sometimes it can be useful for clients to completely disable replies from the
Redis server. For example when the client sends fire and forget commands or
performs a mass loading of data, or in caching contexts where new data is
streamed constantly. In such contexts to use server time and bandwidth in order
to send back replies to clients, which are going to be ignored, is considered
wasteful.

The `CLIENT REPLY` command controls whether the server will reply the client's
commands. The following modes are available:

- `ON`. This is the default mode in which the server returns a reply to every
  command.
- `OFF`. In this mode the server will not reply to client commands.
- `SKIP`. This mode skips the reply of command immediately after it.

@return

When called with either `OFF` or `SKIP` subcommands, no reply is made. When
called with `ON`:

@simple-string-reply: `OK`.
