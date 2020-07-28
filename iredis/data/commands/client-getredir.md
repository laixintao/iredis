This command returns the client ID we are redirecting our
[tracking](/topics/client-side-caching) notifications to. We set a client to
redirect to when using `CLIENT TRACKING` to enable tracking. However in order to
avoid forcing client libraries implementations to remember the ID notifications
are redirected to, this command exists in order to improve introspection and
allow clients to check later if redirection is active and towards which client
ID.

@return

@integer-reply: the ID of the client we are redirecting the notifications to.
The command returns `-1` if client tracking is not enabled, or `0` if client
tracking is enabled but we are not redirecting the notifications to any client.
