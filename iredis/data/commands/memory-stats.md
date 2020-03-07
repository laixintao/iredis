The `MEMORY STATS` command returns an @array-reply about the memory usage of the
server.

The information about memory usage is provided as metrics and their respective
values. The following metrics are reported:

- `peak.allocated`: Peak memory consumed by Redis in bytes (see `INFO`'s
  `used_memory_peak`)
- `total.allocated`: Total number of bytes allocated by Redis using its
  allocator (see `INFO`'s `used_memory`)
- `startup.allocated`: Initial amount of memory consumed by Redis at startup in
  bytes (see `INFO`'s `used_memory_startup`)
- `replication.backlog`: Size in bytes of the replication backlog (see `INFO`'s
  `repl_backlog_active`)
- `clients.slaves`: The total size in bytes of all replicas overheads (output
  and query buffers, connection contexts)
- `clients.normal`: The total size in bytes of all clients overheads (output and
  query buffers, connection contexts)
- `aof.buffer`: The summed size in bytes of the current and rewrite AOF buffers
  (see `INFO`'s `aof_buffer_length` and `aof_rewrite_buffer_length`,
  respectively)
- `lua.caches`: the summed size in bytes of the overheads of the Lua scripts'
  caches
- `dbXXX`: For each of the server's databases, the overheads of the main and
  expiry dictionaries (`overhead.hashtable.main` and
  `overhead.hashtable.expires`, respectively) are reported in bytes
- `overhead.total`: The sum of all overheads, i.e. `startup.allocated`,
  `replication.backlog`, `clients.slaves`, `clients.normal`, `aof.buffer` and
  those of the internal data structures that are used in managing the Redis
  keyspace (see `INFO`'s `used_memory_overhead`)
- `keys.count`: The total number of keys stored across all databases in the
  server
- `keys.bytes-per-key`: The ratio between **net memory usage**
  (`total.allocated` minus `startup.allocated`) and `keys.count`
- `dataset.bytes`: The size in bytes of the dataset, i.e. `overhead.total`
  subtracted from `total.allocated` (see `INFO`'s `used_memory_dataset`)
- `dataset.percentage`: The percentage of `dataset.bytes` out of the net memory
  usage
- `peak.percentage`: The percentage of `peak.allocated` out of `total.allocated`
- `fragmentation`: See `INFO`'s `mem_fragmentation_ratio`

@return

@array-reply: nested list of memory usage metrics and their values

**A note about the word slave used in this man page**: Starting with Redis 5, if
not for backward compatibility, the Redis project no longer uses the word slave.
Unfortunately in this command the word slave is part of the protocol, so we'll
be able to remove such occurrences only when this API will be naturally
deprecated.
