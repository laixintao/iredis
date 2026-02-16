Create an ACL user with the specified rules or modify the rules of an
existing user. 

Manipulate Redis ACL users interactively.
If the username does not exist, the command creates the username without any privilege.
It then reads from left to right all the [rules](#acl-rules) provided as successive arguments, setting the user ACL rules as specified.
If the user already exists, the provided ACL rules are simply applied
*in addition* to the rules already set. For example:

    ACL SETUSER virginia on allkeys +set

The above command creates a user called `virginia` who is active(the _on_ rule), can access any key (_allkeys_ rule), and can call the set command (_+set_ rule).
Then, you can use another `ACL SETUSER` call to modify the user rules:

    ACL SETUSER virginia +get

The above rule applies the new rule to the user `virginia`, so other than `SET`, the user `virginia` can now also use the `GET` command.

Starting from Redis 7.0, ACL rules can also be grouped into multiple distinct sets of rules, called _selectors_.
Selectors are added by wrapping the rules in parentheses and providing them just like any other rule.
In order to execute a command, either the root permissions (rules defined outside of parenthesis) or any of the selectors (rules defined inside parenthesis) must match the given command.
For example:

    ACL SETUSER virginia on +GET allkeys (+SET ~app1*)

This sets a user with two sets of permissions, one defined on the user and one defined with a selector.
The root user permissions only allow executing the get command, but can be executed on any keys.
The selector then grants a secondary set of permissions: access to the `SET` command to be executed on any key that starts with `app1`.
Using multiple selectors allows you to grant permissions that are different depending on what keys are being accessed.

When we want to be sure to define a user from scratch, without caring if
it had previously defined rules associated, we can use the special rule
`reset` as first rule, in order to flush all the other existing rules:

    ACL SETUSER antirez reset [... other rules ...]

After resetting a user, its ACL rules revert to the default: inactive, passwordless, can't execute any command nor access any key or channel:

    > ACL SETUSER antirez reset
    +OK
    > ACL LIST
    1) "user antirez off -@all"

ACL rules are either words like "on", "off", "reset", "allkeys", or are
special rules that start with a special character, and are followed by
another string (without any space in between), like "+SET".

The following documentation is a reference manual about the capabilities of this command, however our [ACL tutorial](/topics/acl) may be a more gentle introduction to how the ACL system works in general.

## ACL rules

Redis ACL rules are split into two categories: rules that define command permissions or _command rules_, and rules that define the user state or _user management rules_.
This is a list of all the supported Redis ACL rules:

### Command rules

* `~<pattern>`: Adds the specified key pattern (glob style pattern, like in the `KEYS` command), to the list of key patterns accessible by the user. This grants both read and write permissions to keys that match the pattern. You can add multiple key patterns to the same user. Example: `~objects:*`
* `%R~<pattern>`: (Available in Redis 7.0 and later) Adds the specified read key pattern. This behaves similar to the regular key pattern but only grants permission to read from keys that match the given pattern. See [key permissions](/topics/acl#key-permissions) for more information.
* `%W~<pattern>`: (Available in Redis 7.0 and later) Adds the specified write key pattern. This behaves similar to the regular key pattern but only grants permission to write to keys that match the given pattern. See [key permissions](/topics/acl#key-permissions) for more information.
* `%RW~<pattern>`: (Available in Redis 7.0 and later) Alias for `~<pattern>`.
* `allkeys`: Alias for `~*`, it allows the user to access all the keys.
* `resetkeys`: Removes all the key patterns from the list of key patterns the user can access.
* `&<pattern>`: (Available in Redis 6.2 and later) Adds the specified glob style pattern to the list of Pub/Sub channel patterns accessible by the user. You can add multiple channel patterns to the same user. Example: `&chatroom:*`
* `allchannels`: Alias for `&*`, it allows the user to access all Pub/Sub channels.
* `resetchannels`: Removes all channel patterns from the list of Pub/Sub channel patterns the user can access.
* `+<command>`: Adds the command to the list of commands the user can call. Can be used with `|` for allowing subcommands (e.g "+config|get").
* `+@<category>`: Adds all the commands in the specified category to the list of commands the user is able to execute. Example: `+@string` (adds all the string commands). For a list of categories, check the `ACL CAT` command.
* `+<command>|first-arg`: Allows a specific first argument of an otherwise disabled command. It is only supported on commands with no sub-commands, and is not allowed as negative form like -SELECT|1, only additive starting with "+". This feature is deprecated and may be removed in the future.
* `allcommands`: Alias of `+@all`. Adds all the commands there are in the server, including *future commands* loaded via module, to be executed by this user.
* `-<command>`: Remove the command to the list of commands the user can call. Starting Redis 7.0, it can be used with `|` for blocking subcommands (e.g., "-config|set").
* `-@<category>`: Like `+@<category>` but removes all the commands in the category instead of adding them.
* `nocommands`: Alias for `-@all`. Removes all the commands, and the user is no longer able to execute anything.

### User management rules

* `on`: Set the user as active, it will be possible to authenticate as this user using `AUTH <username> <password>`.
* `off`: Set user as not active, it will be impossible to log as this user. Please note that if a user gets disabled (set to off) after there are connections already authenticated with such a user, the connections will continue to work as expected. To also kill the old connections you can use `CLIENT KILL` with the user option. An alternative is to delete the user with `ACL DELUSER`, that will result in all the connections authenticated as the deleted user to be disconnected.
* `nopass`: The user is set as a _no password_ user. It means that it will be possible to authenticate as such user with any password. By default, the `default` special user is set as "nopass". The `nopass` rule will also reset all the configured passwords for the user.
* `>password`: Adds the specified clear text password as a hashed password in the list of the users passwords. Every user can have many active passwords, so that password rotation will be simpler. The specified password is not stored as clear text inside the server. Example: `>mypassword`.
* `#<hashedpassword>`: Adds the specified hashed password to the list of user passwords. A Redis hashed password is hashed with SHA256 and translated into a hexadecimal string. Example: `#c3ab8ff13720e8ad9047dd39466b3c8974e592c2fa383d4a3960714caef0c4f2`.
* `<password`: Like `>password` but removes the password instead of adding it.
* `!<hashedpassword>`: Like `#<hashedpassword>` but removes the password instead of adding it.
* `(<rule list>)`: (Available in Redis 7.0 and later) Creates a new selector to match rules against. Selectors are evaluated after the user permissions, and are evaluated according to the order they are defined. If a command matches either the user permissions or any selector, it is allowed. See [selectors](/docs/management/security/acl#selectors) for more information.
* `clearselectors`: (Available in Redis 7.0 and later) Deletes all of the selectors attached to the user.
* `reset`: Removes any capability from the user. They are set to off, without passwords, unable to execute any command, unable to access any key.

@return

@simple-string-reply: `OK` on success.

If the rules contain errors, the error is returned.

@examples

```
> ACL SETUSER alan allkeys +@string +@set -SADD >alanpassword
+OK

> ACL SETUSER antirez heeyyyy
(error) ERR Error in ACL SETUSER modifier 'heeyyyy': Syntax error
```
