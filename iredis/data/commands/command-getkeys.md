Returns @array-reply of keys from a full Redis command.

`COMMAND GETKEYS` is a helper command to let you find the keys
from a full Redis command.

`COMMAND` provides information on how to find the key names of each command (see `firstkey`, [key specifications](/topics/key-specs#logical-operation-flags), and `movablekeys`),
but in some cases it's not possible to find keys of certain commands and then the entire command must be parsed to discover some / all key names.
You can use `COMMAND GETKEYS` or `COMMAND GETKEYSANDFLAGS` to discover key names directly from how Redis parses the commands.


@return

@array-reply: list of keys from your command.

@examples

```cli
COMMAND GETKEYS MSET a b c d e f
COMMAND GETKEYS EVAL "not consulted" 3 key1 key2 key3 arg1 arg2 arg3 argN
COMMAND GETKEYS SORT mylist ALPHA STORE outlist
```
