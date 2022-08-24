The command returns all the rules defined for an existing ACL user.

Specifically, it lists the user's ACL flags, password hashes, commands, key patterns, channel patterns (Added in version 6.2) and selectors (Added in version 7.0).
Additional information may be returned in the future if more metadata is added to the user.

Command rules are always returned in the same format as the one used in the `ACL SETUSER` command.
Before version 7.0, keys and channels were returned as an array of patterns, however in version 7.0 later they are now also returned in same format as the one used in the `ACL SETUSER` command.
Note: This description of command rules reflects the user's effective permissions, so while it may not be identical to the set of rules used to configure the user, it is still functionally identical.

Selectors are listed in the order they were applied to the user, and include information about commands, key patterns, and channel patterns.

@array-reply: a list of ACL rule definitions for the user.

If `user` does not exist a @nil-reply is returned.

@examples

Here's an example configuration for a user

```
> ACL SETUSER sample on nopass +GET allkeys &* (+SET ~key2)
"OK"
> ACL GETUSER sample
1) "flags"
2) 1) "on"
   2) "allkeys"
   3) "nopass"
3) "passwords"
4) (empty array)
5) "commands"
6) "+@all"
7) "keys"
8) "~*"
9) "channels"
10) "&*"
11) "selectors"
12) 1) 1) "commands"
       6) "+SET"
       7) "keys"
       8) "~key2"
       9) "channels"
       10) "&*"
```
