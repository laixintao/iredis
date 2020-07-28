The command shows the available ACL categories if called without arguments. If a
category name is given, the command shows all the Redis commands in the
specified category.

ACL categories are very useful in order to create ACL rules that include or
exclude a large set of commands at once, without specifying every single
command. For instance, the following rule will let the user `karin` perform
everything but the most dangerous operations that may affect the server
stability:

    ACL SETUSER karin on +@all -@dangerous

We first add all the commands to the set of commands that `karin` is able to
execute, but then we remove all the dangerous commands.

Checking for all the available categories is as simple as:

```
> ACL CAT
 1) "keyspace"
 2) "read"
 3) "write"
 4) "set"
 5) "sortedset"
 6) "list"
 7) "hash"
 8) "string"
 9) "bitmap"
10) "hyperloglog"
11) "geo"
12) "stream"
13) "pubsub"
14) "admin"
15) "fast"
16) "slow"
17) "blocking"
18) "dangerous"
19) "connection"
20) "transaction"
21) "scripting"
```

Then we may want to know what commands are part of a given category:

```
> ACL CAT dangerous
 1) "flushdb"
 2) "acl"
 3) "slowlog"
 4) "debug"
 5) "role"
 6) "keys"
 7) "pfselftest"
 8) "client"
 9) "bgrewriteaof"
10) "replicaof"
11) "monitor"
12) "restore-asking"
13) "latency"
14) "replconf"
15) "pfdebug"
16) "bgsave"
17) "sync"
18) "config"
19) "flushall"
20) "cluster"
21) "info"
22) "lastsave"
23) "slaveof"
24) "swapdb"
25) "module"
26) "restore"
27) "migrate"
28) "save"
29) "shutdown"
30) "psync"
31) "sort"
```

@return

@array-reply: a list of ACL categories or a list of commands inside a given
category. The command may return an error if an invalid category name is given
as argument.
