The `LATENCY HISTORY` command returns the raw data of the `event`'s latency
spikes time series.

This is useful to an application that wants to fetch raw data in order to
perform monitoring, display graphs, and so forth.

The command will return up to 160 timestamp-latency pairs for the `event`.

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
127.0.0.1:6379> latency history command
1) 1) (integer) 1405067822
   2) (integer) 251
2) 1) (integer) 1405067941
   2) (integer) 1001
```

For more information refer to the [Latency Monitoring Framework page][lm].

[lm]: /topics/latency-monitor

@return

@array-reply: specifically:

The command returns an array where each element is a two elements array
representing the timestamp and the latency of the event.
