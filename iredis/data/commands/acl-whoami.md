Return the username the current connection is authenticated with. New
connections are authenticated with the "default" user. They can change user
using `AUTH`.

@return

@bulk-string-reply: the username of the current connection.

@examples

```
> ACL WHOAMI
"default"
```
