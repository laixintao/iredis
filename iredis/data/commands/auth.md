The AUTH command authenticates the current connection in two cases:

1. If the Redis server is password protected via the `requirepass` option.
2. If a Redis 6.0 instance, or greater, is using the
   [Redis ACL system](/topics/acl).

Redis versions prior of Redis 6 were only able to understand the one argument
version of the command:

    AUTH <password>

This form just authenticates against the password set with `requirepass`. In
this configuration Redis will deny any command executed by the just connected
clients, unless the connection gets authenticated via `AUTH`.

If the password provided via AUTH matches the password in the configuration
file, the server replies with the `OK` status code and starts accepting
commands. Otherwise, an error is returned and the clients needs to try a new
password.

When Redis ACLs are used, the command should be given in an extended way:

    AUTH <username> <password>

In order to authenticate the current connection with one of the connections
defined in the ACL list (see `ACL SETUSER`) and the official
[ACL guide](/topics/acl) for more information.

When ACLs are used, the single argument form of the command, where only the
password is specified, assumes that the implicit username is "default".

## Security notice

Because of the high performance nature of Redis, it is possible to try a lot of
passwords in parallel in very short time, so make sure to generate a strong and
very long password so that this attack is infeasible. A good way to generate
strong passwords is via the `ACL GENPASS` command.

@return

@simple-string-reply or an error if the password, or username/password pair, is
invalid.
