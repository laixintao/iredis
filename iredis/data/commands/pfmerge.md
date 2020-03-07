Merge multiple HyperLogLog values into an unique value that will approximate the
cardinality of the union of the observed Sets of the source HyperLogLog
structures.

The computed merged HyperLogLog is set to the destination variable, which is
created if does not exist (defaulting to an empty HyperLogLog).

If the destination variable exists, it is treated as one of the source sets and
its cardinality will be included in the cardinality of the computed HyperLogLog.

@return

@simple-string-reply: The command just returns `OK`.

@examples

```cli
PFADD hll1 foo bar zap a
PFADD hll2 a b c foo
PFMERGE hll3 hll1 hll2
PFCOUNT hll3
```
