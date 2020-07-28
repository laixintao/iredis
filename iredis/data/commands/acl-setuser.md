Create an ACL user with the specified rules or modify the rules of an existing
user. This is the main interface in order to manipulate Redis ACL users
interactively: if the username does not exist, the command creates the username
without any privilege, then reads from left to right all the rules provided as
successive arguments, setting the user ACL rules as specified.

If the user already exists, the provided ACL rules are simply applied _in
addition_ to the rules already set. For example:

    ACL SETUSER virginia on allkeys +set

The above command will create a user called `virginia` that is active (the on
rule), can access any key (allkeys rule), and can call the set command (+set
rule). Then another SETUSER call can modify the user rules:

    ACL SETUSER virginia +get

The above rule will not apply the new rule to the user virginia, so other than
`SET`, the user virginia will now be able to also use the `GET` command.

When we want to be sure to define an user from scratch, without caring if it had
previously defined rules associated, we can use the special rule `reset` as
first rule, in order to flush all the other existing rules:

    ACL SETUSER antirez reset [... other rules ...]

After resetting an user, it returns back to the status it has when it was just
created: non active (off rule), can't execute any command, can't access any key:

    > ACL SETUSER antirez reset
    +OK
    > ACL LIST
    1) "user antirez off -@all"

ACL rules are either words like "on", "off", "reset", "allkeys", or are special
rules that start with a special character, and are followed by another string
(without any space in between), like "+SET".

The following documentation is a reference manual about the capabilities of this
command, however our [ACL tutorial](/topics/acl) may be a more gentle
introduction to how the ACL system works in general.

## List of rules

This is a list of all the supported Redis ACL rules:

- `on`: set the user as active, it will be possible to authenticate as this user
  using `AUTH <username> <password>`.
- `off`: set user as not active, it will be impossible to log as this user.
  Please note that if a user gets disabled (set to off) after there are
  connections already authenticated with such a user, the connections will
  continue to work as expected. To also kill the old connections you can use
  `CLIENT KILL` with the user option. An alternative is to delete the user with
  `ACL DELUSER`, that will result in all the connections authenticated as the
  deleted user to be disconnected.
- `~<pattern>`: add the specified key pattern (glob style pattern, like in the
  `KEYS` command), to the list of key patterns accessible by the user. You can
  add as many key patterns you want to the same user. Example: `~objects:*`
- `allkeys`: alias for `~*`, it allows the user to access all the keys.
- `resetkey`: removes all the key patterns from the list of key patterns the
  user can access.
- `+<command>`: add this command to the list of the commands the user can call.
  Example: `+zadd`.
- `+@<category>`: add all the commands in the specified category to the list of
  commands the user is able to execute. Example: `+@string` (adds all the string
  commands). For a list of categories check the `ACL CAT` command.
- `+<command>|<subcommand>`: add the specified command to the list of the
  commands the user can execute, but only for the specified subcommand. Example:
  `+config|get`. Generates an error if the specified command is already allowed
  in its full version for the specified user. Note: there is no symmetrical
  command to remove subcommands, you need to remove the whole command and re-add
  the subcommands you want to allow. This is much safer than removing
  subcommands, in the future Redis may add new dangerous subcommands, so
  configuring by subtraction is not good.
- `allcommands`: alias of `+@all`. Adds all the commands there are in the
  server, including _future commands_ loaded via module, to be executed by this
  user.
- `-<command>`. Like `+<command>` but removes the command instead of adding it.
- `-@<category>`: Like `+@<category>` but removes all the commands in the
  category instead of adding them.
- `nocommands`: alias for `-@all`. Removes all the commands, the user will no
  longer be able to execute anything.
- `nopass`: the user is set as a "no password" user. It means that it will be
  possible to authenticate as such user with any password. By default, the
  `default` special user is set as "nopass". The `nopass` rule will also reset
  all the configured passwords for the user.
- `>password`: Add the specified clear text password as an hashed password in
  the list of the users passwords. Every user can have many active passwords, so
  that password rotation will be simpler. The specified password is not stored
  in cleartext inside the server. Example: `>mypassword`.
- `#<hashedpassword>`: Add the specified hashed password to the list of user
  passwords. A Redis hashed password is hashed with SHA256 and translated into a
  hexadecimal string. Example:
  `#c3ab8ff13720e8ad9047dd39466b3c8974e592c2fa383d4a3960714caef0c4f2`.
- `<password`: Like `>password` but removes the password instead of adding it.
- `!<hashedpassword>`: Like `#<hashedpassword>` but removes the password instead
  of adding it.
- reset: Remove any capability from the user. It is set to off, without
  passwords, unable to execute any command, unable to access any key.

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
