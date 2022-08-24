The `LATENCY HISTOGRAM` command reports a cumulative distribution of latencies in the format of a histogram for each of the specified command names. 
If no command names are specified then all commands that contain latency information will be replied.

Each reported histogram has the following fields:

* Command name.
* The total calls for that command.
* A map of time buckets:
  * Each bucket represents a latency range.
  * Each bucket covers twice the previous bucket's range.
  * Empty buckets are not printed.
  * The tracked latencies are between 1 microsecond and roughly 1 second.
  * Everything above 1 sec is considered +Inf.
  * At max there will be log2(1000000000)=30 buckets.

This command requires the extended latency monitoring feature to be enabled (by default it's enabled).
If you need to enable it, use `CONFIG SET latency-tracking yes`.

@examples

```
127.0.0.1:6379> LATENCY HISTOGRAM set
1# "set" =>
   1# "calls" => (integer) 100000
   2# "histogram_usec" =>
      1# (integer) 1 => (integer) 99583
      2# (integer) 2 => (integer) 99852
      3# (integer) 4 => (integer) 99914
      4# (integer) 8 => (integer) 99940
      5# (integer) 16 => (integer) 99968
      6# (integer) 33 => (integer) 100000
```

@return

@array-reply: specifically:

The command returns a map where each key is a command name, and each value is a map with the total calls, and an inner map of the histogram time buckets.
