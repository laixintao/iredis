Returns @array-reply of details about all Redis commands.

Cluster clients must be aware of key positions in commands so commands can go to
matching instances, but Redis commands vary between accepting one key, multiple
keys, or even multiple keys separated by other data.

You can use `COMMAND` to cache a mapping between commands and key positions for
each command to enable exact routing of commands to cluster instances.

## Nested Result Array

Each top-level result contains six nested results. Each nested result is:

- command name
- command arity specification
- nested @array-reply of command flags
- position of first key in argument list
- position of last key in argument list
- step count for locating repeating keys

### Command Name

Command name is the command returned as a lowercase string.

### Command Arity

<table style="width:50%">
<tr><td>
<pre>
<code>1) 1) "get"
   2) (integer) 2
   3) 1) readonly
   4) (integer) 1
   5) (integer) 1
   6) (integer) 1
</code>
</pre>
</td>
<td>
<pre>
<code>1) 1) "mget"
   2) (integer) -2
   3) 1) readonly
   4) (integer) 1
   5) (integer) -1
   6) (integer) 1
</code>
</pre>
</td></tr>
</table>

Command arity follows a simple pattern:

- positive if command has fixed number of required arguments.
- negative if command has minimum number of required arguments, but may have
  more.

Command arity _includes_ counting the command name itself.

Examples:

- `GET` arity is 2 since the command only accepts one argument and always has
  the format `GET _key_`.
- `MGET` arity is -2 since the command accepts at a minimum one argument, but up
  to an unlimited number: `MGET _key1_ [key2] [key3] ...`.

Also note with `MGET`, the -1 value for "last key position" means the list of
keys may have unlimited length.

### Flags

Command flags is @array-reply containing one or more status replies:

- _write_ - command may result in modifications
- _readonly_ - command will never modify keys
- _denyoom_ - reject command if currently OOM
- _admin_ - server admin command
- _pubsub_ - pubsub-related command
- _noscript_ - deny this command from scripts
- _random_ - command has random results, dangerous for scripts
- _sort_for_script_ - if called from script, sort output
- _loading_ - allow command while database is loading
- _stale_ - allow command while replica has stale data
- _skip_monitor_ - do not show this command in MONITOR
- _asking_ - cluster related - accept even if importing
- _fast_ - command operates in constant or log(N) time. Used for latency
  monitoring.
- _movablekeys_ - keys have no pre-determined position. You must discover keys
  yourself.

### Movable Keys

```
1) 1) "sort"
   2) (integer) -2
   3) 1) write
      2) denyoom
      3) movablekeys
   4) (integer) 1
   5) (integer) 1
   6) (integer) 1
```

Some Redis commands have no predetermined key locations. For those commands,
flag `movablekeys` is added to the command flags @array-reply. Your Redis
Cluster client needs to parse commands marked `movablekeys` to locate all
relevant key positions.

Complete list of commands currently requiring key location parsing:

- `SORT` - optional `STORE` key, optional `BY` weights, optional `GET` keys
- `ZUNIONSTORE` - keys stop when `WEIGHT` or `AGGREGATE` starts
- `ZINTERSTORE` - keys stop when `WEIGHT` or `AGGREGATE` starts
- `EVAL` - keys stop after `numkeys` count arguments
- `EVALSHA` - keys stop after `numkeys` count arguments

Also see `COMMAND GETKEYS` for getting your Redis server tell you where keys are
in any given command.

### First Key in Argument List

For most commands the first key is position 1. Position 0 is always the command
name itself.

### Last Key in Argument List

Redis commands usually accept one key, two keys, or an unlimited number of keys.

If a command accepts one key, the first key and last key positions is 1.

If a command accepts two keys (e.g. `BRPOPLPUSH`, `SMOVE`, `RENAME`, ...) then
the last key position is the location of the last key in the argument list.

If a command accepts an unlimited number of keys, the last key position is -1.

### Step Count

<table style="width:50%">
<tr><td>
<pre>
<code>1) 1) "mset"
   2) (integer) -3
   3) 1) write
      2) denyoom
   4) (integer) 1
   5) (integer) -1
   6) (integer) 2
</code>
</pre>
</td>
<td>
<pre>
<code>1) 1) "mget"
   2) (integer) -2
   3) 1) readonly
   4) (integer) 1
   5) (integer) -1
   6) (integer) 1
</code>
</pre>
</td></tr>
</table>

Key step count allows us to find key positions in commands like `MSET` where the
format is `MSET _key1_ _val1_ [key2] [val2] [key3] [val3]...`.

In the case of `MSET`, keys are every other position so the step value is 2.
Compare with `MGET` above where the step value is just 1.

@return

@array-reply: nested list of command details. Commands are returned in random
order.

@examples

```cli
COMMAND
```
