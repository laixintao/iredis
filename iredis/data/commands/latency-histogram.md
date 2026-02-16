`LATENCY HISTOGRAM` returns a cumulative distribution of commands' latencies in histogram format.

By default, all available latency histograms are returned.
You can filter the reply by providing specific command names.

Each histogram consists of the following fields:

* Command name
* The total calls for that command
* A map of time buckets:
  * Each bucket represents a latency range
  * Each bucket covers twice the previous bucket's range
  * Empty buckets are excluded from the reply
  * The tracked latencies are between 1 microsecond and roughly 1 second
  * Everything above 1 second is considered +Inf
  * At max, there will be log2(1,000,000,000)=30 buckets

This command requires the extended latency monitoring feature to be enabled, which is the default.
If you need to enable it, call `CONFIG SET latency-tracking yes`.

To delete the latency histograms' data use the `CONFIG RESETSTAT` command.

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

The command returns a map where each key is a command name.
The value is a map with a key for the total calls, and a map of the histogram time buckets.
