Adds all the element arguments to the HyperLogLog data structure stored at the
variable name specified as first argument.

As a side effect of this command the HyperLogLog internals may be updated to
reflect a different estimation of the number of unique items added so far (the
cardinality of the set).

If the approximated cardinality estimated by the HyperLogLog changed after
executing the command, `PFADD` returns 1, otherwise 0 is returned. The command
automatically creates an empty HyperLogLog structure (that is, a Redis String of
a specified length and with a given encoding) if the specified key does not
exist.

To call the command without elements but just the variable name is valid, this
will result into no operation performed if the variable already exists, or just
the creation of the data structure if the key does not exist (in the latter case
1 is returned).

For an introduction to HyperLogLog data structure check the `PFCOUNT` command
page.

@return

@integer-reply, specifically:

- 1 if at least 1 HyperLogLog internal register was altered. 0 otherwise.

@examples

```cli
PFADD hll a b c d e f g
PFCOUNT hll
```
