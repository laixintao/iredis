Produces an ASCII-art style graph for the specified event.

`LATENCY GRAPH` lets you intuitively understand the latency trend of an `event`
via state-of-the-art visualization. It can be used for quickly grasping the
situation before resorting to means such parsing the raw data from
`LATENCY HISTORY` or external tooling.

Valid values for `event` are:

- `active-defrag-cycle`
- `aof-fsync-always`
- `aof-stat`
- `aof-rewrite-diff-write`
- `aof-rename`
- `aof-write`
- `aof-write-active-child`
- `aof-write-alone`
- `aof-write-pending-fsync`
- `command`
- `expire-cycle`
- `eviction-cycle`
- `eviction-del`
- `fast-command`
- `fork`
- `rdb-unlink-temp-file`

@example

```
127.0.0.1:6379> latency reset command
(integer) 0
127.0.0.1:6379> debug sleep .1
OK
127.0.0.1:6379> debug sleep .2
OK
127.0.0.1:6379> debug sleep .3
OK
127.0.0.1:6379> debug sleep .5
OK
127.0.0.1:6379> debug sleep .4
OK
127.0.0.1:6379> latency graph command
command - high 500 ms, low 101 ms (all time high 500 ms)
--------------------------------------------------------------------------------
   #_
  _||
 _|||
_||||

11186
542ss
sss
```

The vertical labels under each graph column represent the amount of seconds,
minutes, hours or days ago the event happened. For example "15s" means that the
first graphed event happened 15 seconds ago.

The graph is normalized in the min-max scale so that the zero (the underscore in
the lower row) is the minimum, and a # in the higher row is the maximum.

For more information refer to the [Latency Monitoring Framework page][lm].

[lm]: /topics/latency-monitor

@return

@bulk-string-reply
